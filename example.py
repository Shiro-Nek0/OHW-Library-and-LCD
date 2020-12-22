from subprocess import call
import OHWjson as OHW
import I2C_LCD_driver 
import os
import time

cycles = range(2)
time_between = 3

mylcd = I2C_LCD_driver.lcd()

cd = os.path.join(os.getcwd(), os.path.dirname(__file__))
__location__ = os.path.realpath(cd)
config = OHW.get_local_json_contents(os.path.join(__location__, 'config.json'))

mylcd.backlight(1)
mylcd.lcd_clear()

def update():
    data = OHW.get_hardware_info(config['ohw_ip'],config['ohw_port'],config['cpu_name'],config['ram_name'],config['gpu_name'],config['gpu_mem_size'])
    return data

while True:
    try:
        my_info = update()
        mylcd.backlight(1)
        for _ in cycles:
            mylcd.lcd_display_string("[---ShiroNeko-PC---]",1)
            mylcd.lcd_display_string("CPU:{}% Temp:{}c".format(my_info["cpu"]["load"],my_info["cpu"]["temp"]),2)
            mylcd.lcd_display_string("GPU:{}% Temp:{}c".format(my_info["gpu"]["load"],my_info["gpu"]["temp"]),3)
            mylcd.lcd_display_string("RAM:{} Ava:{}".format(my_info["ram"]["used"],my_info["ram"]["available"]),4)
            time.sleep(time_between)
            mylcd.lcd_clear()

        for _ in cycles:
            my_info = update()
            mylcd.lcd_display_string("[-{}-]".format((config['gpu_name'].replace("NVIDIA ","")).replace(" ","-")),1)
            mylcd.lcd_display_string("Load:{}% Temp:{}c".format(my_info["gpu"]["load"],my_info["gpu"]["temp"]),2)
            mylcd.lcd_display_string("Clock:{}Mhz".format(my_info["gpu"]["core_clock"]),3)
            mylcd.lcd_display_string("Mem:{}GB Ava:{}GB".format(round(float(my_info["gpu"]["used_mem"])/1024,1),round(float(my_info["gpu"]["free_memory"])/1024,1)),4)
            time.sleep(time_between)
            mylcd.lcd_clear()

        for _ in cycles:
            my_info = update()
            clock = [float(n) for n in my_info["cpu"]["clocks"] if n]
            mylcd.lcd_display_string("[-{}--]".format((config['cpu_name'].replace("Intel ","").replace(" ","-"))),1)
            mylcd.lcd_display_string("Load:{}%".format(my_info["cpu"]["load"]),2)
            mylcd.lcd_display_string("Temp:{}c".format(my_info["cpu"]["temp"]),3)
            mylcd.lcd_display_string("Clock:{}Ghz".format(round(sum(clock)/len(clock)/1000,2)),4)
            time.sleep(time_between)
            mylcd.lcd_clear()

        for _ in cycles:
            my_info = update()
            mylcd.lcd_display_string("[-----{}-RAM-----]".format(my_info["ram"]["total"]),1)
            mylcd.lcd_display_string("Load:{}%".format(my_info["ram"]["load"]),2)
            mylcd.lcd_display_string("Used:{}".format(my_info["ram"]["used"]),3)
            mylcd.lcd_display_string("Available:{}".format(my_info["ram"]["available"]),4)
            time.sleep(time_between)
            mylcd.lcd_clear()

            my_info = update()
            mylcd.lcd_display_string("[---ShiroNeko-PC---]",1)
            mylcd.lcd_display_string(config['cpu_name'].replace("Intel ",""),2)
            mylcd.lcd_display_string(config['gpu_name'].replace("NVIDIA ",""),3)
            mylcd.lcd_display_string("{} {}".format(config['ram_name'],my_info["ram"]["total"]),4)
            time.sleep(time_between*2)
            mylcd.lcd_clear()
    except:
        print("connection failed!")
        
        mylcd.lcd_clear()
        mylcd.lcd_display_string("[---ShiroNeko-PC---]",1)
        mylcd.lcd_display_string("[Connection--Failed]",2)
        mylcd.lcd_display_string("[-----Retrying!----]",3)
        mylcd.lcd_display_string("[------------------]",4)
        time.sleep(1)
        if "SSH_CONNECTION" in os.environ:
            print("ssh detected NOT shutting down!")