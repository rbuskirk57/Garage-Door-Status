import network
import secrets
import mqtt_params
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led, Button, LED
from machine import Pin
import utime
import machine
from umqttsimple import MQTTClient

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # set static IP - put this in the secrets file for future)
    wlan.ifconfig(('192.168.40.58', '255.255.252.0', '192.168.42.1', '8.8.8.8'))
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        led.toggle()
        sleep(1)
    #led.toggle()
    utime.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=30)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client
# This code is executed once a new message is published
def new_message_callback(topic, msg):
    topic , msg=topic.decode('ascii') , msg.decode('ascii')
    print("Topic: "+topic+" | Message: "+msg)
    if msg[0:2] == "SD":
        f = open("sdoor.txt", 'w')
        f.write(msg)
        f.close()
        wrt_sysok("1")
    elif msg[0:2] == "LD":
        f = open("ldoor.txt", 'w')
        f.write(msg)
        f.close()
        wrt_sysok("1")
    elif msg[0:2] == "Te":
        f = open("temp.txt", 'w')
        f.write(msg)
        f.close()
        wrt_sysok("1")
    else:
        print("Just a heads-up ... msg in callback didn't match: " + msg)
        wrt_sysok("0")

def wrt_sysok(status):
    f = open("sysok.txt", "w")
    f.write(status)
    f.close()

def reset_pico():
   print('Failed to connect to the MQTT Broker. Bailing out with a machine reset...')
   utime.sleep(5)
   machine.reset()

def s_door_up(): #green on
    s_green.toggle()
    s_red.off()
    s_yellow.off()

def s_door_down(): # red on
    s_red.on()
    s_green.off()
    s_yellow.off()

def s_door_in_motion(): # yellow toggle
    s_red.off()
    s_green.off()
    s_yellow.toggle()

def l_door_up(): #green on
    l_green.toggle()
    l_red.off()
    l_yellow.off()

def l_door_down(): # red on
    l_red.on()
    l_green.off()
    l_yellow.off()

def l_door_in_motion(): # yellow toggle
    l_red.off()
    l_green.off()
    l_yellow.toggle()

led = Pin(28, Pin.OUT) #WiFi connected
s_red = LED(20, Pin.OUT) #closed
s_green = LED(18, Pin.OUT) #open
s_yellow = LED(19, Pin.OUT) #in motion
l_red = LED(14, Pin.OUT) #closed
l_green = LED(13, Pin.OUT) #open
l_yellow = LED(12, Pin.OUT) #in motion

btn8 = Button(17)
#led.low()
client_id = mqtt_params.client_id
mqtt_server = mqtt_params.mqtt_server
user_t = mqtt_params.user_t
password_t = mqtt_params.password_t
topic_pub = mqtt_params.topic_pub
count = 0

ip = connect()
led.on()

# the following will set the seconds between 2 keep alive messages
keep_alive=30

try:
    client = mqtt_connect()
    client.set_callback(new_message_callback)
    client.subscribe(topic_pub.encode('utf-8'))

except OSError as e:
    reset_pico()

last_message=utime.time()

mssg = client.check_msg()

# Main loop
while True:
    try:
        f = open("sdoor.txt")
        sd_status = f.read()
        f.close()
        
        f = open("ldoor.txt")
        ld_status = f.read()
        f.close()
        
        f = open("temp.txt")
        temp_f = f.read()
        f.close()
        
        f = open("sysok.txt")
        sys_ok = f.read()
        f.close()
        
        if btn8.is_pressed:
            # kill it
            reset_pico()

        if sd_status == 'SD_OPEN': #open
            s_door_up()
        elif sd_status == 'SD_CLOSED': #closed
            s_door_down()
        else:
            s_door_in_motion()

        if ld_status == 'LD_OPEN': #open
            l_door_up()
        elif ld_status == 'LD_CLOSED': #closed
            l_door_down()
        else:
            l_door_in_motion()

        if sys_ok == "1":
            count = 0
            led.on()
        else:
            count = count + 1
            if count > 500:
                led.toggle()
        
        client.check_msg()
        utime.sleep(0.1)
        if (utime.time() - last_message) > keep_alive:
              client.publish(topic_pub, "Keep alive message")
              last_message = utime.time()

    except OSError as e:
        print(e)
        reset_pico()
        pass

client.disconnect()

    






