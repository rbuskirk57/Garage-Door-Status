import network
import secrets
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led, Button
from machine import Pin
import utime
import machine
from umqttsimple import MQTTClient

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # set static IP - put this in the secrets file for future)
    wlan.ifconfig(('192.168.2.185', '255.255.255.0', '192.168.2.1', '8.8.8.8'))
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    led.toggle()
    utime.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def mqtt_serve(door):
    client = mqtt_connect()
    #utime.sleep(1)
    client.publish(secrets.topic_pub, msg=door)
    utime.sleep(3)
        
def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=30)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reset_pico():
   print('Failed to connect to the MQTT Broker. Bailing out with a machine reset...')
   utime.sleep(5)
   machine.reset()

led = Pin(28, Pin.OUT)
btn1 = Button(1)
btn2 = Button(6)
btn8 = Button(16)
led.low()
#MQTT connection
#last_message = 0
#message_interval = 5
#counter = 0
client_id = secrets.client_id
mqtt_server = secrets.mqtt_server
user_t = secrets.user_t
password_t = secrets.password_t

ip = connect()

while True:
    try:
        print("First try section")
        client = mqtt_connect()
    except OSError as e:
        print("first exeption")
        reset_pico()
    while True:
        if btn8.is_pressed:
            # kill it
            reset_pico()
        elif btn1.is_pressed:
            door = 'OPEN'
        elif btn2.is_pressed:
            door = 'CLOSED'
        else:
            door = 'IN MOTION'

        try:
            client.publish(secrets.topic_pub, msg=door)
            utime.sleep(3)
        except:
            print("Client publish failed, executing a soft reset")
            machine.soft_reset()
            pass
    print("client disconnect")
    client.disconnect()
    





