import time
from rotary_irq_rp2 import RotaryIRQ
from lcd_trial import write_lcd as lcd
from machine import Pin, PWM, ADC,  SPI
import gc9a01 as gc9a01
import vga1_16x16 as font
import NotoSansMono_32 as font2
from math import *
import network
import socket

################################################# CONNECTION
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Name of the network" ,"password")
time.sleep(5)
print(wlan.isconnected())
# # # # # # # # ############################## opening socket
SERVER_IP = 'Global IP adress'
PORT = ****  
# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server socket
try:
    client_socket.connect((SERVER_IP, PORT))
except OSError as e:
    print(f"Error connecting to server: {e}")

#####################################################33 
ButtonR = Pin(22,Pin.IN,Pin.PULL_UP)


global flag_R
global counter
global axis

axis = ["X","Y","Z"]
counter = 0
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
# # # # # # # #

############################################################################################## joystick
vrx = ADC(Pin(26))
vry = ADC(Pin(27))

def create_array(xval,yval):
    xnum = 0
    ynum = 0
    if xval > 64000:
        xnum = 1
    if yval > 64000:
        ynum = 1
    if xval < 5000:
        xnum = -1
    if yval < 5000:
        ynum = -1
    return [xnum,ynum]
#######################################################################################################

spi = SPI(0, baudrate=60000000, sck=Pin(6), mosi=Pin(3))
tft = gc9a01.GC9A01(
    spi,
    dc=Pin(18, Pin.OUT),
    cs=Pin(20, Pin.OUT),
    reset=Pin(19, Pin.OUT),
    rotation=0)




r = RotaryIRQ(pin_num_clk=13,
              pin_num_dt=12,
              min_val=0,
              max_val=36,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_WRAP)
data = {"joystick":"", "encoder":"","axis":""}
val_old = r.value()
tft.fill(0)
old_val_new = 0
data_k = ""
old_data = {}
while True:
    xval = vrx.read_u16()
    yval = vry.read_u16()
    data_j = str(create_array(xval,yval))
    val_new = r.value()
    lcd(tft,axis[counter],110,70,10000)
    if val_old != val_new:
        lcd(tft,".",int(80*cos(old_val_new/5.75))+110,int(80*sin(old_val_new/5.75)+110),0)

        tft.fill_rect(100, 110, 70,30, 0)
        val_old = val_new
        # print('result =', val_new)
        data_k = str(val_new*10)
        lcd(tft,data_k,100,110,30000)
        lcd(tft,".",int(80*cos(val_new/5.75))+110,int(80*sin(val_new/5.75)+110),4000)
        old_val_new = val_new
    data["joystick"] = data_j
    data["encoder"] = data_k
    data["axis"] = axis[counter]
    if data != old_data:
        client_socket.send(str(data).encode())
    old_data = data.copy()

    time.sleep_ms(10)
