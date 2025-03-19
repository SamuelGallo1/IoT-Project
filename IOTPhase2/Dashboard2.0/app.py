import time
import board
import adafruit_dht
from flask import Flask, jsonify, render_template
import psutil
import smtplib
import imaplib
import email
import RPi.GPIO as GPIO
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


app = Flask(__name__)

# Terminate any running libgpiod processes to avoid conflicts
for process in psutil.process_iter():
    if process.name() in ['libgpiod_pulsein', 'libgpiod_plsei']:
        process.kill()

# DHT11 Sensor configuration
DHTPin = board.D27  # GPIO pin for DHT11 sensor
sensor = adafruit_dht.DHT11(DHTPin)

#Motor configuration..
Motor1 = 22 # Enable Pin
Motor2 = 18 # Input Pin
Motor3 = 17 # Input Pin
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

#so when it starts it starts false.
GPIO.output(Motor1,GPIO.LOW)
GPIO.output(Motor2,GPIO.LOW)
GPIO.output(Motor3,GPIO.LOW)

#========================================================
# TODO: CHANGE THE SMTP CREDENTIALS.
# SAMUEL: create smtp account for project
#=========================================================

# Gmail configuration
GMAIL_USER = 'gmail.com'
GMAIL_PASSWORD = "fjfifr"  # App-specific password

fan_on = False
email_sent = False
last_temp = None
last_humidity = None

def send_email_alert(temp):
    global email_sent
    try:
        subject = "Temperature Alert - Fan Control"
        body = f"The current temperature is {temp}°C. Please reply 'YES' to turn on the fan."

        message = MIMEMultipart()
        message['From'] = GMAIL_USER
        message['To'] = GMAIL_USER
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, GMAIL_USER, message.as_string())
        server.quit()

        print("Alert email sent.")
        email_sent = True
    except Exception as e:
        print(f"Error sending email: {e}")
def check_for_yes_reply():
    global fan_on, email_sent
    try:
        print("Connecting to Gmail to check for replies...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select('inbox')

        # Search for unseen messages with the specific subject
        status, messages = mail.search(None, '(UNSEEN SUBJECT "Re: Temperature Alert - Fan Control")')
        print("Checking for unread 'YES' replies...")

        for msg_num in messages[0].split():
            print(f"Checking message number: {msg_num}")  # Debug message
            status, msg_data = mail.fetch(msg_num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    print(f"Processing email: {msg}")  # Debug message
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode().strip()
                                print(f"Email body received: '{body}'")  # Debug message
                                # Split the body to get the first line or relevant reply part
                                first_line = body.splitlines()[0].strip().lower()  # Get first line and normalize
                                print(f"First line extracted: '{first_line}'")  # Debug message
                                if first_line == "yes":
                                    print("Found 'YES' reply! Turning on the fan...")
                                    mail.store(msg_num, '+FLAGS', '\\Seen')  # Mark as read
                                    fan_on = True  # Turn the fan on
                                    toggle_fan_ON()
                                    email_sent = False  # Reset email sent status
                                    print("Fan status updated to ON.")
                                    mail.logout()
                                    return True
                                else:
                                    print("Reply was not 'YES'.")  # Debug message
                    else:
                        body = msg.get_payload(decode=True).decode().strip()
                        print(f"Email body received (not multipart): '{body}'")  # Debug message
                        first_line = body.splitlines()[0].strip().lower()  # Get first line and normalize
                        print(f"First line extracted: '{first_line}'")  # Debug message
                        if first_line == "yes":
                            print("Found 'YES' reply! Turning on the fan...")
                            mail.store(msg_num, '+FLAGS', '\\Seen')  # Mark as read
                            fan_on = True  # Turn the fan on
                            toggle_fan_ON()
                            email_sent = False  # Reset email sent status
                            print("Fan status updated to ON.")
                            mail.logout()
                            return True
                        else:
                            print("Reply was not 'YES'.")  # Debug message
        mail.logout()
        print("No 'YES' reply found.")
        return False
    except Exception as e:
        print(f"Error checking emails: {e}")
        return False





@app.route('/')
def index():
    return render_template('index.html', fan_on=fan_on)

@app.route('/toggle-fan')  # Changed to POST
def toggle_fan():
    global fan_on
    if not fan_on:
        GPIO.output(Motor1,GPIO.HIGH)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.HIGH)
        fan_on = True
    else:
        GPIO.output(Motor1,GPIO.LOW)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.LOW)
        fan_on = False

    return jsonify({'success': True, 'fan': fan_on})  


@app.route('/toggle-fan-ON')  # used forr the email. toggle ON 
def toggle_fan_ON():
    global fan_on
    GPIO.output(Motor1,GPIO.HIGH)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.HIGH)
    fan_on = True
    

@app.route('/sensor-data')
def get_sensor_data():
    global fan_on, email_sent, last_temp, last_humidity
    retries = 3
    #For testing (joseph --> do not touch)
    #send_email_alert(21)
    #check_for_yes_reply()


    for _ in range(retries):
        try:
           # temp = sensor.temperature
            temp = sensor.temperature
            humidity = sensor.humidity

            if temp is not None and humidity is not None:
                last_temp, last_humidity = temp, humidity  # Cache successful readings
                print(f"Temperature: {temp}°C, Humidity: {humidity}%, Fan Status: {'ON' if fan_on else 'OFF'}")

                # Send an email if temperature exceeds 20°C and no email has been sent
                if temp > 20 and not email_sent and not fan_on:
                    send_email_alert(temp)

                # Check for a 'YES' reply only if an email has been sent
                if email_sent:
                    check_for_yes_reply()

                return jsonify({
                    'temperature': temp,
                    'humidity': humidity,
                    'fan': fan_on  # Return the current fan status
                })

        except RuntimeError as error:
            print(f"Sensor Error: {str(error)} - Retrying...")
            time.sleep(1)

    # If all retries fail, return last known values or error message
    if last_temp is not None and last_humidity is not None:
        print("Returning last known good readings.")
        return jsonify({
            'temperature': last_temp,
            'humidity': last_humidity,
            'fan': fan_on
        }), 500
    else:
        print("Failed to read sensor data.")
        return jsonify({'error': 'Failed to read sensor data.'}), 500

if __name__ == '__main__':
    while True:
        try:
            app.run(host='0.0.0.0', port=5001)
            time.sleep(10)  # Wait for 10 seconds before the next check
        finally:
            sensor.exit()
