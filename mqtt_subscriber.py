import network
import secrets
import mqtt_params
import net_connect
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led, Button, LED
from machine import Pin
import utime
import machine
from umqttsimple import MQTTClient

# do I need this?
sd_status = ""
ld_status = ""

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=30)
    client.connect()
    print(client)
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

# This code is executed once a new message is published
def new_message_callback(topic, msg):
    global sd_status
    global ld_status
    global temp_f
    topic , msg=topic.decode('ascii') , msg.decode('ascii')
    #print("Topic: "+topic+" | Message: "+msg)
    if msg[0:2] == "SD":
        sd_status = msg
    elif msg[0:2] == "LD":
        ld_status = msg
    elif msg[0:2] == "Te":
        temp_f = msg
    else:
        print("Just a heads-up ... msg in callback didn't match: " + msg)

def reset_pico():
   print('Failed to connect to the MQTT Broker. Bailing out with a machine reset...')
   #utime.sleep(5)
   #machine.reset()
   led.off()
   machine.soft_reset()

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
client_id = mqtt_params.client_id
mqtt_server = mqtt_params.mqtt_server
user_t = mqtt_params.user_t
password_t = mqtt_params.password_t
topic_pub = mqtt_params.topic_pub
count = 0

ip = net_connect.connect(secrets.SSID, secrets.PASSWORD, 10)
if ip != "-1":
    led.on()
else:
    reset_pico()

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

wlan = network.WLAN(network.STA_IF)

# Main loop
while True:
    if not wlan.isconnected():
        print("Network connection failed")
        led.toggle()
        
    try:
        if btn8.is_pressed:
            # kill it
            reset_pico()
        count += 1
        
        #print(sd_status, ld_status, count)
        
        # 
        if sd_status == 'SD_OPEN': #open
            s_door_up()
        elif sd_status == 'SD_CLOSED': #closed
            s_door_down()
        elif sd_status == 'SD_IN MOTION':
            s_door_in_motion()
        else:
            pass

        if ld_status == 'LD_OPEN': #open
            l_door_up()
        elif ld_status == 'LD_CLOSED': #closed
            l_door_down()
        elif ld_status == 'LD_IN MOTION':
            l_door_in_motion()
        else:
            pass

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

    








