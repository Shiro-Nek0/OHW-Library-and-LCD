import OHWjson as OHW
import os
import time

off_on_disconnect = False

cd = os.path.join(os.getcwd(), os.path.dirname(__file__))
__location__ = os.path.realpath(cd)
config = OHW.get_local_json_contents(os.path.join(__location__, 'config.json'))

def update():
    my_info = OHW.get_hardware_info(config['ohw_ip'],config['ohw_port'],config['cpu_name'],config['ram_name'],config['gpu_name'],config['gpu_mem_size'])
    return my_info


while True:
    try:
        my_info = update()

        clock = [float(n) for n in my_info["cpu"]["clocks"] if n]
    
        print("[---ShiroNeko-PC---]")
        print("CPU:{}% Temp:{}c".format(my_info["cpu"]["load"],my_info["cpu"]["temp"]))
        print("GPU:{}% Temp:{}c".format(my_info["gpu"]["load"],my_info["gpu"]["temp"]))
        print("RAM:{} Ava:{}".format(my_info["ram"]["used"],my_info["ram"]["available"]))
        time.sleep(6)
        

        my_info = update()
        print("[-{}-]".format((config['gpu_name'].replace("NVIDIA ","")).replace(" ","-")))
        print("Load:{}% Temp:{}c".format(my_info["gpu"]["load"],my_info["gpu"]["temp"]))
        print("Clock:{}Mhz".format(my_info["gpu"]["core_clock"]))
        print("Mem:{}GB Ava:{}GB".format(round(float(my_info["gpu"]["used_mem"])/1024),round(float(my_info["gpu"]["free_memory"])/1024)))
        time.sleep(6)
        

        my_info = update()
        print("[-{}--]".format((config['cpu_name'].replace("Intel ","").replace(" ","-"))))
        print("Load:{}%".format(my_info["cpu"]["load"]))
        print("Temp:{}c".format(my_info["cpu"]["temp"]))
        print("Clock:{}Ghz".format(round(sum(clock)/len(clock)/1000)))
        time.sleep(6)
        

        my_info = update()
        print("[-----{}-RAM-----]".format(my_info["ram"]["total"]))
        print("Load:{}%".format(my_info["ram"]["load"]))
        print("Used:{}".format(my_info["ram"]["used"]))
        print("Available:{}".format(my_info["ram"]["available"]))
        time.sleep(6)
        

        my_info = update()
        print("[---ShiroNeko-PC---]")
        print(config['cpu_name'].replace("Intel ",""))
        print(config['gpu_name'].replace("NVIDIA ",""))
        print("{} {}".format(config['ram_name'],my_info["ram"]["total"]))
        time.sleep(6)
        
    except:
        print("connection failed!")
        
        print("[---ShiroNeko-PC---]")
        print("[Connection--Failed]")
        print("[----Retrying!-----]")
        print("[------------------]")
        
        if (off_on_disconnect == True):
            print("[---ShiroNeko-PC---]")
            print("[Connection--Failed]")
            print("[---Shutting-down--]")
            print("[------------------]")
            print("Shutting down")
            time.sleep(3)
            call("sudo poweroff", shell=True)
    
#[---ShiroNeko-PC---]
#CPU:20% Temp:38c
#GPU:21% Temp:57c
#RAM:6.8GB Ava:9.1GB

#[-GeForce-GTX-1070-]
#Load21% Temp:57c
#Clock:607.5Mhz
#Mem:1695MB

#[-Xeon-E5-2650-v2--]
#Load:20%
#Temp:38c
#Clock:2594Mhz

#[-----16GB-RAM-----]
#Load:42%
#Used:6.8GB
#Available:9.2GB

#[---ShiroNeko-PC---]
#Xeon E5-2650 v2
#GeForce GTX 1070
#Generic Memory 16GB