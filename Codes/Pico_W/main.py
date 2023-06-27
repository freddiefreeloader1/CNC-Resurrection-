import time
from rotary_irq_rp2 import RotaryIRQ
from lcd_trial import write_lcd as lcd
from machine import Pin, PWM, ADC,  SPI, Timer
import gc9a01 as gc9a01
import vga1_16x16 as font
import NotoSansMono_32 as font2
from math import *
import network
import socket
################################################ LCD
spi = SPI(0, baudrate=60000000, sck=Pin(6), mosi=Pin(3))
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
# wlan.connect("SUPERONLINE_WiFi_3659","vujnDFh4PbeH")
wlan.connect("mechalab_intra" ,"mechastudent")
time.sleep(10)
print(wlan.isconnected())
if wlan.isconnected() == True:
    lcd(tft, "wifi: Active", 10,100,15000)
    time.sleep(2)
else:
    lcd(tft, "wifi: Error ", 50,100,15000)
    time.sleep(2)

# # # # # # # # ############################## opening socket
SERVER_IP = '192.168.1.100'
PORT = 5151   
# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server socket
try:
    client_socket.connect((SERVER_IP, PORT))
except OSError as e:
    print(f"Error connecting to server: {e}")
    lcd(tft, "Socket: Error", 10,130,15000)
    

##################################################### buttons
ButtonR = Pin(15,Pin.IN,Pin.PULL_UP)


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
##############################################################3
ButtonY = Pin(12,Pin.IN,Pin.PULL_DOWN)


global flag_Y
global counterY
global axisJ

axisJ = ["|X| ","|Y| ","|XY|"]
counterY = 0
def callback_Y(ButtonY):
    global flag_Y
    global counterY
    ButtonY.irq(handler = None)

    time.sleep(0.01)
    if flag_Y is 0 and ButtonY.value() == 1:
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
vrx = ADC(Pin(27))
vry = ADC(Pin(28))
bat = ADC(Pin(26))


def create_array(xval,yval):
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


soft_timer = Timer(mode=Timer.PERIODIC, period=5, callback=interruption_handler)
################################Buzzer
buzz = PWM(Pin(10))
buzz.freq(1000)
###############################


r = RotaryIRQ(pin_num_clk=13,
              pin_num_dt=22,
              min_val=0,
              max_val=36,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_WRAP)

data = {"joystick":"", "encoder":"","axis":"","axisJ":""}
val_old = 0
tft.fill(0)
old_val_new = 0
data_k = ""
old_data = {"joystick":"", "encoder":"","axis":"","axisJ":""}
lcd(tft, "Socket: Active", 10,130,15000)
time.sleep(1)
tft.fill(0)
client_socket.send("X".encode())
time.sleep(0.5)
while True:

    
    batPer = int(bat.read_u16()*100/65535)
    xval = vrx.read_u16()
    yval = vry.read_u16()
    data_j = str(create_array(xval,yval))
    val_new = r.value()
    lcd(tft,axisJ[counterY],105,70,10000)
    lcd(tft,axis[counter],80,70,10000)
    lcd(tft,"%",106,180,15000)
    lcd(tft,"Bat",100,150,30000)
    lcd(tft,str(batPer),120,180,15000)  
    if val_old != val_new:
        client_socket.send(str(data["encoder"]).encode())
        buzz.duty_u16(50000)
        lcd(tft,".",int(90*cos(old_val_new/5.75))+110,int(90*sin(old_val_new/5.75)+110),0)

        tft.fill_rect(100, 110, 70,30, 0)
        if (val_new - val_old) < 0:
            data["encoder"] = -((-(val_new - val_old))%36)
        else:
            data["encoder"] = (val_new - val_old)%36
        print(data["encoder"])
        val_old = val_new
        # print('result =', val_new)
        data_k = str(val_new*10)
        lcd(tft,data_k,100,110,30000)
        lcd(tft,".",int(90*cos(val_new/5.75))+110,int(90*sin(val_new/5.75)+110),4000)
        old_val_new = val_new
    buzz.duty_u16(0)
    data["joystick"] = data_j
    data["axis"] = axis[counter]
    data["axisJ"] = axisJ[counterY]
    if data["joystick"] != old_data["joystick"]:
        client_socket.send(str(data["joystick"]).encode())
    if data["axis"] != old_data["axis"]:
        client_socket.send(str(data["axis"]).encode())
    if data["axisJ"] != old_data["axisJ"]:
        client_socket.send(str(data["axisJ"]).encode())
    
    
    old_data = data.copy()
    
    time.sleep_ms(1)
    
