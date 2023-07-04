import random
from machine import Pin, SPI
import gc9a01 as gc9a01

# Choose a font

# import vga1_8x8 as font
# from fonts import vga2_8x8 as font
# from fonts import vga1_8x16 as font
# from fonts import vga2_8x16 as font
import vga1_16x16 as font
# from fonts import vga1_bold_16x16 as font
# from fonts import vga2_16x16 as font
# from fonts import vga2_bold_16x16 as font
# from fonts import vga1_16x32 as font
# from fonts import vga1_bold_16x32 as font
# from fonts import vga2_16x32 as font
# from fonts import vga2_bold_16x32 as font




def write_lcd(tft,data,xpos,ypos,color):

    
    # tft.rotation(2)


    
    tft.text(
            font,
            data,
            xpos,
            ypos,
            color)
    




