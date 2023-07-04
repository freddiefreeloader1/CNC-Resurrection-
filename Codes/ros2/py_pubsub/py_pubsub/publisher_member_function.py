# import the libraries
import rclpy
from rclpy.node import Node
import socket
from std_msgs.msg import String
import serial
import time 
import re 
# define and inilialize the global variables
global j_val            # joystick direction list
j_val = "[0, 0]"
global hwaxis            # handwheel axis
global stepsize            # defines how many steps should be sent via serial
stepsize = 0
hwaxis = ""
global joyaxis             # defines which axes the joystick should work
joyaxis = ""
global prec                # defines how much should the step motors work after one step
prec = "0.3"

class MinimalPublisher(Node):                    # basic ros2 publisher class that takes the topic name as the input

    def __init__(self, topic_name):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, topic_name, 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        #msg = String()
        #msg.data = 'Hello World: %d' % self.i
        ## self.publisher_.publish(msg)
        #self.get_logger().info('Publishing: "%s"' % msg.data)
        #self.i += 1
        pass 

    def publish_data(self, incomedata):
        msg = String()
        msg.data = incomedata
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1
def sumdigits(no):                        # the handwheel data sometimes comes as "11-21" when rotated swiftly. This function sums all the digits in this string to find the step size
    if no == 0:
        return 0  
    if "-" in no: 
        return sum(map(int,re.findall(r'(\d|-\d)', no)))        # parsing and summing for strings with negative digits
    else:
        return sum(int(x) for x in no if x.isdigit())            # summing for only positive digit strings

def main(args=None):

    global j_val
    global hwaxis
    global stepsize
    global joyaxis 
    global prec
    com = serial.Serial('/dev/ttyUSB0',baudrate=115200)                # define the serial 
    com.write(str.encode("\r\n\r\n"))                                  # wake up grbl                
   

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);            # opening the socket
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(("192.168.1.100",5151))                                    # here use your own global ip you found with ifconfig command in linux 

    rclpy.init(args=args)                                                    # init rclpy

    minimal_publisher = MinimalPublisher("CNC")                                # create two publishers, one for the information coming from the remote, and one for the heartbeat
    heart_beat_publisher = MinimalPublisher("heartbeat")

    while(True):                                                # listen for the socket connection

        serverSocket.listen();

        (clientConnected, clientAddress) = serverSocket.accept();

        print("Accepted a connection request from %s:%s"%(clientAddress[0], clientAddress[1]));
    
        break                    # if a connection is received break the loop
    
    while(True):

        dataFromClient = str(clientConnected.recv(1024).decode())                # get the data from the client in string format
        
        if "HB" in dataFromClient:                                        # if there is "HB" string in data, publish to heartbeat topic and get rid of "HB" in the data. 
            heart_beat_publisher.publish_data("HB")
            dataFromClient = dataFromClient.replace("HB","")

        # print(j_val)

        if dataFromClient != "":                                    # if something else comes, also publish "HB" to heartbeat topic, and get rid of it 
            heart_beat_publisher.publish_data("HB")
            if dataFromClient.replace("HB","") != "":
                minimal_publisher.publish_data(dataFromClient.replace("HB",""))   # 

        ############################################## for CNC purposes
        if dataFromClient == "X":                            # here is for initial variables: define the handwheel axis, joystick axis, and the precision according to the data coming from remote
            hwaxis = "X"
        if dataFromClient == "Y":
            hwaxis = "Y"
        if dataFromClient == "Z":
            hwaxis = "Z"
        if "|X|" in dataFromClient:
            joyaxis = "X"
        if "|Y|" in dataFromClient:
            joyaxis = "Y"
        if "|XY" in dataFromClient:
            joyaxis = "XY"
            
        if dataFromClient == "P0.3":
            prec = "0.3"
        if dataFromClient == "P0.5":
            prec = "0.5"
        if dataFromClient == "P0.7":
            prec = "0.7"
        if dataFromClient == "P1":
            prec = "1"
        ############################# HANDWHEEL
        if hwaxis == "X":                                                    # check the handwheel axis
            datahw = dataFromClient.replace("-","")                          # create new string without the - sign, e.g. input string "-1-234", output string is "1234" to check for .isdigit()
            if datahw.isdigit():                                             # check if the data is digit or not 
                stepsize = sumdigits(dataFromClient)                         # calculate the step size 
                print(stepsize)
                if stepsize > 0:
                    for i in range(stepsize):                                # apply the step size
                        com.write(str.encode("G91 G0 X" + prec + "\r\n"))    # apply the precision
                elif stepsize < 0:
                    for i in range(-stepsize):
                        com.write(str.encode("G91 G0 X-" + prec + "\r\n"))

        if hwaxis == "Y":                                                    # same as the X axis 
            datahw = dataFromClient.replace("-","")
            if datahw.isdigit():
                stepsize = sumdigits(dataFromClient)
                print(stepsize)
                if stepsize > 0:
                    for i in range(stepsize):
                        com.write(str.encode("G91 G0 Y" + prec + "\r\n"))
                elif stepsize < 0:
                    for i in range(-stepsize):
                        com.write(str.encode("G91 G0 Y-" + prec + "\r\n"))


        if hwaxis == "Z":                                                # same as the X axis
            datahw = dataFromClient.replace("-","")
            if datahw.isdigit():
                stepsize = sumdigits(dataFromClient)
                print(stepsize)
                if stepsize > 0:
                    for i in range(stepsize):
                        com.write(str.encode("G91 G0 Z" + prec + "\r\n"))
                elif stepsize < 0:
                    for i in range(-stepsize):
                        com.write(str.encode("G91 G0 Z-" + prec + "\r\n"))

        # print(dataFromClient)
        ######################################### joystick
        if joyaxis == "X" or joyaxis == "XY":                                # check joystick axis, if it is X or XY allow only X

            if "[0, 0" in dataFromClient:
                j_val = "[0, 0]"

            if dataFromClient == "[0, 0]" or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))

            if dataFromClient == "[1, 0]" or j_val == "[1, 0]":                # if the direction list is [1, 0], move in positive X direction by sending the appropriate g-code through serial
                j_val = "[1, 0]"
                com.write(str.encode("G91 G0 X-0.3\r\n"))
            
            if "[0, 0" in dataFromClient or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))
    
            if dataFromClient == "[-1, 0]" or j_val ==  "[-1, 0]":
                j_val = "[-1, 0]"
                com.write(str.encode("G91 G0 X0.3\r\n"))

            if "[0, 0" in dataFromClient or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n")) 

        if joyaxis == "Y" or joyaxis == "XY":                            # allow only Y movement 

            if dataFromClient == "[0, 1]" or j_val == "[0, 1]":
                j_val = "[0, 1]"
                com.write(str.encode("G91 G0 Y0.3\r\n"))
            if "[0, 0" in dataFromClient or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))  

            if dataFromClient == "[0, -1]" or j_val ==  "[0, -1]":
                j_val = "[0, -1]"
                com.write(str.encode("G91 G0 Y-0.3\r\n"))

        if joyaxis == "XY":                                            # allow X and Y movements along with the simultaneous movement 

            if dataFromClient == "[-1, 1]" or j_val ==  "[-1, 1]":
                j_val = "[-1, 1]"
                com.write(str.encode("G91 G0 X0.3 Y0.3\r\n"))

            if "[0, 0" in dataFromClient or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0 Y0\r\n"))

            if dataFromClient == "[1, 1]" or j_val == "[1, 1]":
                j_val = "[1, 1]"
                com.write(str.encode("G91 G0 X-0.3 Y0.3\r\n"))
            if "[0, 0" in dataFromClient or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))  

            if dataFromClient == "[1, -1]" or j_val ==  "[1, -1]":
                j_val = "[1, -1]"
                com.write(str.encode("G91 G0 X-0.3 Y-0.3\r\n"))
            if dataFromClient == "[-1, -1]" or j_val ==  "[-1, -1]":
                j_val = "[-1, -1]"
                com.write(str.encode("G91 G0 X0.3 Y-0.3\r\n"))
        ############################################################################3

    
        
        # print(dataFromClient)                


    


        '''else:
            if dataFromClient == "HB":
                heart_beat_publisher.publish_data("HB")'''











if __name__ == '__main__':                    # call the main
    main()
