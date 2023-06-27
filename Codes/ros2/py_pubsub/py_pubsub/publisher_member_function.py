
import rclpy
from rclpy.node import Node
import socket
from std_msgs.msg import String
import serial
import time 

global j_val
j_val = "[0, 0]"
global hwaxis
global stepsize
stepsize = 0
hwaxis = ""
global joyaxis 
joyaxis = ""

class MinimalPublisher(Node):

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
def sumdigits(no):
    return 0 if no == 0 else int(no%10) + sumdigits(int(no/10))
def main(args=None):

    global j_val
    global hwaxis
    global stepsize
    global joyaxis 
    com = serial.Serial('/dev/ttyUSB0',baudrate=115200)
    com.write(str.encode("\r\n\r\n")) # wake up grbl
   

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(("192.168.1.100",5151))

    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher("trial")
    heart_beat_publisher = MinimalPublisher("heartbeat")

    while(True):

        serverSocket.listen();

        (clientConnected, clientAddress) = serverSocket.accept();

        print("Accepted a connection request from %s:%s"%(clientAddress[0], clientAddress[1]));
    
        break
    
    while(True):

        dataFromClient = str(clientConnected.recv(1024).decode())
        
        if "HB" in dataFromClient:
            dataFromClient = dataFromClient.replace("HB","")

        # print(j_val)

        if dataFromClient != "":
            heart_beat_publisher.publish_data("HB")
            if dataFromClient.replace("HB","") != "":
                minimal_publisher.publish_data(dataFromClient.replace("HB",""))

        if dataFromClient == "X":
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

        if hwaxis == "X":
            if dataFromClient.isdigit():
                stepsize = sumdigits(int(dataFromClient))
                for i in range(stepsize):
                    print("h")
                    com.write(str.encode("G91 G0 X0.3\r\n"))
            elif "-" in dataFromClient:
                datahw = dataFromClient.replace("-","")
                if datahw.isdigit():
                    stepsize = sumdigits(int(datahw))
                    for i in range(stepsize):
                        print("h")
                        com.write(str.encode("G91 G0 X-0.3\r\n"))

        if hwaxis == "Y":
            if dataFromClient.isdigit():
                stepsize = sumdigits(int(dataFromClient))
                for i in range(stepsize):
                    com.write(str.encode("G91 G0 Y0.3\r\n"))
            elif "-" in dataFromClient:
                datahw = dataFromClient.replace("-","")
                if datahw.isdigit():
                    stepsize = sumdigits(int(datahw))
                    for i in range(stepsize):
                        print("h")
                        com.write(str.encode("G91 G0 Y-0.3\r\n"))


        # print(dataFromClient)
        ######################################### joystick
        if joyaxis == "X" or joyaxis == "XY":

            if dataFromClient == "[0, 0]":
                j_val = "[0, 0]"

            if dataFromClient == "[0, 0]" or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))

            if dataFromClient == "[1, 0]" or j_val == "[1, 0]":
                j_val = "[1, 0]"
                com.write(str.encode("G91 G0 X0.3\r\n"))
            
            if dataFromClient == "[0, 0]" or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))
    
            if dataFromClient == "[-1, 0]" or j_val ==  "[-1, 0]":
                j_val = "[-1, 0]"
                com.write(str.encode("G91 G0 X-0.3\r\n"))

            if dataFromClient == "[0, 0]" or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n")) 

        if joyaxis == "Y" or joyaxis == "XY":    

            if dataFromClient == "[0, 1]" or j_val == "[0, 1]":
                j_val = "[0, 1]"
                com.write(str.encode("G91 G0 Y0.3\r\n"))
            if dataFromClient == "[0, 0]" or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))  

            if dataFromClient == "[0, -1]" or j_val ==  "[0, -1]":
                j_val = "[0, -1]"
                com.write(str.encode("G91 G0 Y-0.3\r\n"))

        if joyaxis == "XY":

            if dataFromClient == "[-1, 1]" or j_val ==  "[-1, 1]":
                j_val = "[-1, 1]"
                com.write(str.encode("G91 G0 X-0.3 Y0.3\r\n"))

            if dataFromClient == "[0, 0]" or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0 Y0\r\n"))

            if dataFromClient == "[1, 1]" or j_val == "[1, 1]":
                j_val = "[1, 1]"
                com.write(str.encode("G91 G0 X0.3 Y0.3\r\n"))
            if dataFromClient == "[0, 0]" or j_val == "[0, 0]":
                j_val = "[0, 0]"
                com.write(str.encode("G91 G0 X0\r\n"))  

            if dataFromClient == "[1, -1]" or j_val ==  "[1, -1]":
                j_val = "[1, -1]"
                com.write(str.encode("G91 G0 X0.3 Y-0.3\r\n"))
            if dataFromClient == "[-1, -1]" or j_val ==  "[-1, -1]":
                j_val = "[-1, -1]"
                com.write(str.encode("G91 G0 X-0.3 Y-0.3\r\n"))
        ################################################## encoder

    
        
        # print(dataFromClient)                


    


        '''else:
            if dataFromClient == "HB":
                heart_beat_publisher.publish_data("HB")'''











if __name__ == '__main__':
    main()
