import time
from rotary_irq_rp2 import RotaryIRQ
from machine import Pin, PWM, ADC,  SPI, Timer
from lcd_trial import write_lcd as lcd
import gc9a01 as gc9a01
import vga1_16x16 as font
import NotoSansMono_32 as font2
from math import *
import network
import socket
################################################ LCD
spi = SPI(0, baudrate=60000000, sck=Pin(6), mosi=Pin(3))   # define the lcd pins
tft = gc9a01.GC9A01(
    spi,
    dc=Pin(18, Pin.OUT),
    cs=Pin(20, Pin.OUT),
    reset=Pin(19, Pin.OUT),
    rotation=3)
tft.fill(0)
################################################# CONNECTION
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("mechalab_intra" ,"mechastudent")        # enter your own network information
time.sleep(15)                                        # waiting time for wifi connection
print(wlan.isconnected())
if wlan.isconnected() == True:
    lcd(tft, "wifi: Active", 10,100,15000)
    time.sleep(2)
else:
    lcd(tft, "wifi: Error ", 50,100,15000)
    time.sleep(2)

# # # # # # # # ############################## opening socket
SERVER_IP = '192.168.1.100'                        # learn you global ıp from ifconfig, not the local one! 
PORT = 5151                                        # select the port you want to use, preferably bigger than 1000, choose an unused one 
# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server socket
try:                                                # try expect makes the code try again if the connection is not succesful
    client_socket.connect((SERVER_IP, PORT))
except OSError as e:
    print(f"Error connecting to server: {e}")
    lcd(tft, "Socket: Error", 10,130,15000)
    

##################################################### buttons
ButtonR = Pin(15,Pin.IN,Pin.PULL_UP)


global flag_R                    # for debouncing 
global counter
global axis

axis = ["X","Y","Z"]                # define the axis list for CNC 
counter = 0                        # define the index counter for the axis list
def callback_R(ButtonR):
    global flag_R
    global counter
    ButtonR.irq(handler = None)

    time.sleep(0.01)
    if flag_R is 0 and ButtonR.value() == 1:
        # print("Interrupt has occured")
        flag_R = 0
        counter = counter + 1
        # print(counter)
        if counter == 3:
            counter = 0


    flag_R = ButtonR.value()
    ButtonR.irq(handler = callback_R)

flag_R = ButtonR.value()

ButtonR.irq(trigger = Pin.IRQ_RISING, handler = callback_R)
##############################################################3
ButtonY = Pin(11,Pin.IN,Pin.PULL_DOWN)


global flag_Y
global counterY
global axisJ

axisJ = ["|X| ","|Y| ","|XY|"]             # define the axis list for the joystick
counterY = 0                               # counter for joystick axis
def callback_Y(ButtonY):
    global flag_Y
    global counterY
    ButtonY.irq(handler = None)

    time.sleep(0.01)
    if flag_Y is 0 and ButtonY.value() == 1:                        # debouncing code
        # print("Interrupt has occured")
        flag_Y = 0
        counterY = counterY + 1
        print(counterY)
        if counterY == 3:
            counterY = 0


    flag_Y = ButtonY.value()
    ButtonY.irq(handler = callback_Y)

flag_Y = ButtonY.value()

ButtonY.irq(trigger = Pin.IRQ_RISING, handler = callback_Y)
############################################################################################## joystick
Buttonjoy = Pin(21,Pin.IN,Pin.PULL_UP)

global counterjoy
global flag_joy                        # debouncing 

counterjoy = 0                        # this is the variable for the selection of menu items, when it is 1 the function is selected in the menu
                    
def callback_joy(Buttonjoy):
    global flag_joy
    global counterjoy
    Buttonjoy.irq(handler = None)

    time.sleep(0.01)
    if flag_joy is 0 and Buttonjoy.value() == 1:
        flag_joy = 0
        counterjoy = 1                # when button is released, make the code select the function
        print(counterjoy)


    flag_joy = Buttonjoy.value()
    Buttonjoy.irq(handler = callback_joy)

flag_joy = Buttonjoy.value()

Buttonjoy.irq(trigger = Pin.IRQ_RISING, handler = callback_joy)

vrx = ADC(Pin(27))                # defining the x and y axis for the joystick, and also define the battery pin for analog read
vry = ADC(Pin(28))
bat = ADC(Pin(26))


def create_array(xval,yval):            # based on some predefined limits, create an direction array for the joystick, e.g. [1, 0] represents positive X direction
    xnum = 0
    ynum = 0
    if xval > 63000:
        xnum = 1
    if yval > 63000:
        ynum = 1
    if xval < 10000:
        xnum = -1
    if yval < 10000:
        ynum = -1
    return [xnum,ynum]
#######################################################################################################
###############################
def interruption_handler(timer):                                
    client_socket.send("HB".encode())


soft_timer = Timer(mode=Timer.PERIODIC, period=5, callback=interruption_handler)            # timer interrupt sends heartbeat at every 5 ms, can configure with changing the period value
################################Buzzer
buzz = PWM(Pin(10))                    # defining buzzer pins
buzz.freq(1000)                        # defining buzzer freq
###############################


r = RotaryIRQ(pin_num_clk=13,            # used an rotary encoder library to use as a quadrate encoder using two QRD's. Define the pins you use for the QRD's in here
              pin_num_dt=22,
              min_val=0,
              max_val=36,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_WRAP)

data = {"joystick":"", "encoder":"","axis":"","axisJ":""}        # create data dictionary for sending it 
val_old = 0                                                    
tft.fill(0)            # clear the lcd
old_val_new = 0
data_k = ""
old_data = {"joystick":"", "encoder":"","axis":"","axisJ":""}        # used for comparing the new data to old data in order to send message at each change in data
lcd(tft, "Socket: Active", 10,130,15000)
time.sleep(1)
tft.fill(0)
client_socket.send("X".encode())                        # send initial axis info to socket 
time.sleep(0.5)
def CNC():
    global counterjoy                                # defining global variables for comparing the old data to new data
    global val_new
    global old_val_new
    global val_old
    global data
    global old_data
    global data_k
    global data_j
    while True:
        batPer = int(bat.read_u16()*100/65535)                    # read battery, joystick, and encoder values
        xval = vrx.read_u16()
        yval = vry.read_u16()
        data_j = str(create_array(xval,yval))                # joystick direction list
        val_new = r.value()                                # encoder value
        lcd(tft,axisJ[counterY],105,70,10000)                    # display all the information on lcd
        lcd(tft,axis[counter],80,70,10000)
        lcd(tft,"%",106,180,15000)
        lcd(tft,"Bat",100,150,30000)
        lcd(tft,str(batPer),120,180,15000)  
        if val_old != val_new:                                    # check if the encoder value changed
               
            buzz.duty_u16(50000)                                # create a sound everytime the encoder value changes
            lcd(tft,".",int(90*cos(old_val_new/5.75))+110,int(90*sin(old_val_new/5.75)+110),0)        # delete the point on the lcd that represents the previous encoder position        

            tft.fill_rect(100, 110, 70,30, 0)
            if (val_new - val_old) < 0:                                            # calculate the encoder step size value. the every step in encoder corresponds to 10 degrees in lcd
                data["encoder"] = -((-(val_new - val_old))%36)
            else:
                data["encoder"] = (val_new - val_old)%36
            client_socket.send(str(data["encoder"]).encode())     # if encoder value changed send the value through socket 
            print(data["encoder"])
            val_old = val_new                                      # assign val_old for comparison
            # print('result =', val_new)
            data_k = str(val_new*10)
            lcd(tft,data_k,100,110,30000)                        # display the angle value on lcd
            lcd(tft,".",int(90*cos(val_new/5.75))+110,int(90*sin(val_new/5.75)+110),4000)            # display a point on the lcd that represents the encoder position as a reference   
            old_val_new = val_new
        buzz.duty_u16(0)
        data["joystick"] = data_j                                            # assign the information to data dictionary 
        data["axis"] = axis[counter]
        data["axisJ"] = axisJ[counterY]
        if data["joystick"] != old_data["joystick"]:                           # compare the old data dict with the new one, if anything changed send the changed information through socket
            client_socket.send(str(data["joystick"]).encode())
        if data["axis"] != old_data["axis"]:
            client_socket.send(str(data["axis"]).encode())
        if data["axisJ"] != old_data["axisJ"]:
            client_socket.send(str(data["axisJ"]).encode())
        
        
        old_data = data.copy()                            # create old_data at each iteration
        if counterjoy == 1:                                # if joystick button is pressed break the loop and return to main menu
            counterjoy = 0
            tft.fill(0)
            break
        time.sleep(0.04)
    
global prec                                             # define precision value for CNC
prec = [0.3, 0.5, 0.7, 1]                                # precision list that can be configured
val_prec = 0                                        
old_val_prec = 0                        # for comparison of the old and new
    
def other1():
    global counterjoy
    global prec
    global val_prec
    global old_val_prec
    while True:
        lcd(tft,"CNC Precision",20,80,15000)                    # display the title
        val_prec = (r.value())%len(prec)                        # val_prec should be in the range 0 and len(prec)
        if val_prec < 0:                                        # if it becomes smaller than 0, return to the last element of the prec list 
            val_prec = len(prec)
        lcd(tft,str(prec[val_prec]),80,120,45000)
        if old_val_prec != val_prec:                            # if anything changed then send the new prec value
            tft.fill_rect(80,120,50,50,0)                        # delete the old prec value on lcd
            client_socket.send(("P" + str(prec[val_prec])).encode())
            print(prec[val_prec])
        if counterjoy == 1:                                # if button joy is pressed, return to main menu
            counterjoy = 0
            tft.fill(0)
            break
        old_val_prec = val_prec
        
def other2():                                                # these functions are configurable for other uses, here you can define your own functions to suit your needs
    global counterjoy    
    while True:
        lcd(tft,"Mini Robot",50,80,15000)
        if counterjoy == 1:
            counterjoy = 0
            tft.fill(0)
            break
def other3():
    global counterjoy   
    while True:
        lcd(tft,"Drone",50,80,15000)
        if counterjoy == 1:
            counterjoy = 0
            tft.fill(0)
            break
        
tft.fill(0)
y = 40
global menu_count
menu_count = 0                                            # keeping track of which menu item we are in 
old_joy = 0
menu = ["CNC","CNC Prec","Mini Robot","Drone"]            # define the menu

while True:
    counterjoy = 0                                        # selection of menu items
    xvalmenu = vrx.read_u16()                
    yvalmenu = vry.read_u16()
    data_joy = str(create_array(xvalmenu,yvalmenu))       # create direction list for joystick for going through the menu
    if data_joy != old_joy:                                # if the list changed, then check what direction
        if data_joy == "[0, 1]":                        # if y direction is upwards increase the menu count
            menu_count += 1
        if data_joy == "[0, -1]":
            menu_count -= 1
        if menu_count < 0:
            menu_count = len(menu)
        if menu_count > len(menu):
            menu_count = 0
    for item in menu:
        lcd(tft,item, 50,60 + 20*(menu.index(item)),30000)
    tft.fill_rect(20,80,20,70,0)
    if menu_count == 0:
        tft.fill_rect(20,80,20,70,0)
        lcd(tft,".",30,60,10000)
    if menu_count == 1:
        tft.fill_rect(20,50,20,70,0)
        lcd(tft,".",30,80,10000)
    if menu_count == 2:
        tft.fill_rect(20,50,20,70,0)
        lcd(tft,".",30,100,10000)
    if menu_count == 3:
        tft.fill_rect(20,50,20,70,0)
        lcd(tft,".",30,120,10000)
    if counterjoy == 1 and menu_count == 0:
        tft.fill(0)
        counterjoy = 0
        CNC()
        tft.fill(0)
    if counterjoy == 1 and menu_count == 1:
        tft.fill(0)
        counterjoy = 0
        other1()
        tft.fill(0)
    if counterjoy == 1 and menu_count == 2:
        tft.fill(0)
        counterjoy = 0
        other2()
        tft.fill(0)
    if counterjoy == 1 and menu_count == 3:
        tft.fill(0)
        counterjoy = 0
        other3()
        tft.fill(0)
        
    old_joy = data_joy
    time.sleep(0.001)


