from flask import Flask, render_template, redirect, url_for, jsonify #access library (mods)

import RPi.GPIO as GPIO

from time import sleep

app = Flask(__name__) #machine...


GPIO.setwarnings(False) # Ignore warning for now

GPIO.setmode(GPIO.BCM)
LED=18
GPIO.setup(LED,GPIO.OUT)

GPIO.output(LED,GPIO.LOW) #



#setup:
led_status="OFF" #it wont force it to be OFF. 
#------------------------------------

@app.route("/")
def index():
    return render_template("index.html",led_status=led_status)

@app.route("/toggle",methods=["POST"])#it is in AJAX. (no route just mods of index.html)
def toggle_led():
    global led_status
    if led_status == "OFF":
        #toggle("ON")
        GPIO.output(LED,GPIO.HIGH)
        led_status = "ON"
    else:
        #toggle("OFF")
        GPIO.output(LED,GPIO.LOW)
        led_status = "OFF"
        
    return jsonify(status=led_status) #(AJAX. this will return the same template and specific info to change the light)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
#------------------------------------
#while True:

