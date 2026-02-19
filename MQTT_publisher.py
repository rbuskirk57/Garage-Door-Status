#import network
import secrets
import mqtt_pub_params
import net_connect
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led, Button
from machine import Pin
import utime
import machine
from umqtt.robust import MQTTClient

def mqtt_serve(door):
    client = mqtt_connect()
    client.publish(mqtt_pub_params.topic_pub, msg=door)
    utime.sleep(3)
        
def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=30)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reset_pico():
   print('Failed to connect to the MQTT Broker. Bailing out with a machine soft reset...')
   # Using the soft_reset is an experitment to see if I can improve recovery
   # when the Pico loses WiFi connection.
   led.off()
   machine.soft_reset()

led = Pin(15, Pin.OUT)
sd_btn1 = Button(2)
sd_btn2 = Button(3)
ld_btn1 = Button(4)
ld_btn2 = Button(5)
btn_reset = Button(17)
led.low()
client_id = mqtt_pub_params.client_id
mqtt_server = mqtt_pub_params.mqtt_server
user_t = mqtt_pub_params.user_t
password_t = mqtt_pub_params.password_t

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

ip = net_connect.connect(secrets.SSID, secrets.PASSWORD)
if ip != "-1":
    led.on()
else:
    reset_pico()

while True:
    try:
        client = mqtt_connect()
    except OSError as e:
        reset_pico()
    while True:
        # kill it
        if btn_reset.is_pressed:
            reset_pico()

        # Small Garage Door
        if sd_btn1.is_pressed:
            sdoor = 'SD_OPEN'
        elif sd_btn2.is_pressed:
            sdoor = 'SD_CLOSED'
        else:
            sdoor = 'SD_IN MOTION'

        # Large Garage Door
        if ld_btn1.is_pressed:
            ldoor = 'LD_OPEN'
        elif ld_btn2.is_pressed:
            ldoor = 'LD_CLOSED'
        else:
            ldoor = 'LD_IN MOTION'
            
        reading = sensor_temp.read_u16() * conversion_factor 
        temperature_c = 27 - (reading - 0.706)/0.001721
        fahrenheit_degrees = temperature_c * (9 / 5) + 32
        Temp_F = "Temp: " + str(round(fahrenheit_degrees,2)) + " *F"

        try:
            client.publish(mqtt_pub_params.topic_pub, msg=sdoor)
            client.publish(mqtt_pub_params.topic_pub, msg=ldoor)
            client.publish(mqtt_pub_params.topic_pub, msg=Temp_F)
            utime.sleep(1)
        except:
            print("Client publish failed, executing a machine reset")
            reset_pico()
            pass
    print("client disconnect")
    client.disconnect()
    





