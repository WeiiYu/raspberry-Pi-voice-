#!/usr/bin/env python3
# Requires PyAudio and PySpeech.
import speech_recognition as sr

from picamera import PiCamera

from time import ctime
from time import sleep
import time
import os
from gtts import gTTS

import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from requests import get
from datetime import datetime, timedelta
from json import loads
from pprint import pprint

from TwitterAPI import TwitterAPI
from twython import Twython

from PIL import Image

import wikipedia

from twilio.rest import Client

COMMASPACE = ', '
KEY = '35625ebc8a6f29fbe4d5de8bffe46155'
account_sid = 'AC4fca6eb6da8bdd50cea9eba4887d5254'
auth_token = 'ef0cbfff00c959bf551c873b55525bfa'
client = Client(account_sid, auth_token)

def speak(audioString):
    print(audioString)
    tts = gTTS(text=audioString, lang='en')
    tts.save("audio.mp3")
    os.system("mpg321 audio.mp3")

# record the audio
def record():
    # Excute command line to record a audio
    #print("Please say something: ")
    os.chdir('/home/pi/Desktop/Project')
    os.system('sudo arecord -D plughw:1,0 -d 5 inputVoice.wav')
    
def recordAudio():
    record()
    AUDIO_FILE = ("inputVoice.wav")
    
    # Record Audio
    r = sr.Recognizer()
    
    #with sr.Microphone() as source:
    with sr.AudioFile(AUDIO_FILE) as source:  
        #print("Say something!")
        #audio = r.listen(source)
        audio = r.record(source)

    # Speech recognition using Google Speech Recognition
    data = ""
    try:
        # Uses the default API key
        # To use another API key: `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        data = r.recognize_google(audio)
        speak("You said: " + data)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        print("Please say again")
        #recordAudio()
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return data

# turn on the camera if the wake pharse is correct
def turnOnCamera():
    print("Turning on the camera")
    camera = PiCamera()
    camera.resolution = (800, 600)
    camera.start_preview()
    speak("Do you want to take a picture or record a video?")
    while 1:
        answer = recordAudio()
        if "picture" in answer:
            speak("Taking picture after 3 seconds")
            speak("3")
            sleep(0.5)
            speak("2")
            sleep(0.5)
            speak("1")
            sleep(0.5)
            camera.capture('/home/pi/Desktop/Project/pic1.jpg')
            speak("Do you want to do anything more?")
            
        if "video" in answer:
            speak("Recording 5-second video")
            camera.start_recording('/home/pi/Desktop/Project/video.h264')
            sleep(5)
            camera.stop_recording()
            speak("Do you want to do anything more?")
            
        if "turn off" in answer:
            print("Turning off the camera")
            camera.stop_preview()
            break
        
        if "no" in answer:
            print("Turning off the camera")
            camera.stop_preview()
            break
            
# send email by gmail API
def sendemail():
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 

    # start TLS for security 
    s.starttls() 

    # Authentication
    usr = b'\xff\xfey\x00w\x004\x00d\x00h\x00r\x001\x002\x003\x00@\x00g\x00m\x00a\x00i\x00l\x00.\x00c\x00o\x00m\x00'.decode('utf-16')
    pwd = b'\xff\xfey\x00u\x00w\x00e\x00i\x004\x00d\x00h\x00r\x00'.decode('utf-16')
    s.login(usr, pwd)

    # record audio
    speak("What messages do you want to send:")
    record()
    AUDIO_FILE = ("inputVoice.wav")
    r = sr.Recognizer() 
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
        inputSpeechtoText = r.recognize_google(audio)
        
    # message to be sent 
    message = inputSpeechtoText
    speak("Do you want to send message as: " + message)
    # if else method to make sure if you want to send corret message

    data = recordAudio()
    
    if "yes" in data:
        # sending the mail 
        s.sendmail(usr, "kirosa1994@gmail.com", message) 
        print("Sent")
        # terminating the session
        s.quit()
    else:
        sendemail()

# check the the weather
def get_city_id():
    with open('city2.json') as f:
        data = loads(f.read())
        
    city_id = False
    while city_id == False:
        speak("Which city do you want to check?")
        city = recordAudio()
        print(city)
        
        if "thank you" in city:
            break
        
        for item in data:
            if item['name'] == city:
                speak('Is this in ' + item['country'])
                answer = recordAudio()
                
                if "yes" in answer:
                #if answer == 'y':
                    city_id = item['id']
                    break

        if not city_id:
            speak('Sorry, that location is not available')

    return city_id

def get_weather_data(city_id):
    weather_data = get('http://api.openweathermap.org/data/2.5/forecast?id={}&APPID={}'.format(city_id, KEY))
    return weather_data.json()

def get_forecast(weather_data):
    data = weather_data["list"][0]["main"]
    temp = data["temp"] - 273.15
    temp_min = data["temp_min"]- 273.15
    temp_max = data["temp_max"]- 273.15
    pressure = data["pressure"]
    sea_level = data["sea_level"]
    grnd_level = data["grnd_level"]
    humidity = data["humidity"]
    speak("Current Temp is: " + str(temp) + " Celsius")
    print("Min Temp is: " + str(temp_min) + " Celsius")
    print("Max Temp is: " + str(temp_max) + " Celsius")
    print("Current Pressure is: " + str(pressure))
    print("Current Sea Level is: " + str(sea_level))
    print("Current Humidity is: " + str(humidity))

#twitter
def tweet():
    #initial
    CONSUMER_KEY = 'M0msWHjUgLY0LfpwhJa6TlV9d'
    CONSUMER_SECRET = 'shxyXxHgx5Idtna3qvwBdcI0e4A6wzrTZ6hIRz1i4TKeMjOij0'
    ACCESS_TOKEN_KEY = '2829274261-tIG4EwVofoo5N8OxX8NIGIsBD46PcM7efQCQwcJ'
    ACCESS_TOKEN_SECRET = 'Wb2wHSI6UgTEfBHMjVAvWyA77e5CFfqMrpDEF4hBl5090'
    
    twitter = TwitterAPI(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN_KEY,ACCESS_TOKEN_SECRET)
    
    n = 1
    while n == 1:
        speak("What do you want to post to Twitter? (Status or Photo or both of them)")
        preSta = recordAudio()
        #print(preSta)
        if "update" in preSta:
            print("What do you want to tweet today")
            preStatus = recordAudio()
            #print(preStatus)
            if preStatus == '':
                preStatus = 'CS642'
            r = twitter.request('statuses/update', {'status': preStatus})
            speak('SUCCESS' if r.status_code == 200 else 'FAILURE')
            
        if "photo" in preSta:
            file = open('./pic1.jpg', 'rb')
            data = file.read()
            r = twitter.request('media/upload', None, {'media': data})
            speak('UPLOAD MEDIA SUCCESS' if r.status_code == 200 else 'UPLOAD MEDIA FAILURE')

            # STEP 2 - post tweet with reference to uploaded image
            if r.status_code == 200:
                print("What do you want to tweet with your photo today")
                preStatus = recordAudio()
                #print(preStatus)
                media_id = r.json()['media_id']
                r = twitter.request('statuses/update', {'status' : preStatus, 'media_ids' : media_id})
                speak('UPDATE STATUS SUCCESS' if r.status_code == 200 else 'UPDATE STATUS FAILURE')
        
        if "thank you" in preSta:
            n = 0
        
        if "no" in preSta:
            n = 0
            
def openImage():
    image = Image.open('./pic1.jpg')
    image.show()

def sendSMS():
    print("What do you want to send to your friend?")
    data = recordAudio()
    print("Do you want to send this message to your friend?")
    preSta = recordAudio()
    if "yes" in preSta:
        message = client.messages \
        .create(
             body = data,
             from_ = '+17813039597',
             to = '+18572947850'
         )
        
        #print(message.sid)
        print("Sent")
    else:
        sendSMS()

# jarvis   
def jarvis():
    while 1:
        speak("Here are something that I can help you today:")
        print("1. Checking the time right now")
        print("2. Checking the weather in specific city")
        print("3. Taking a picture or recording a short video")
        print("4. Sending email to your friend")
        print("5. Update status or posting photo to Twitter")
        print("6. Map")
        print("7. Wikipedia")
        print("8. Sending SMS to your friend")
        
        data = recordAudio()
        
        if "photo" in data:
            openImage()
            
        if "hi" in data:
            speak("Hi, how are you doing today?")
            
        if "how are you" in data:
            speak("I am fine! Thank you")

        if "what time" in data:
            speak(ctime())
            
        # take picture
        if "camera" in data:
            turnOnCamera()
            
        # send picture to email:
        if "email" in data:
            sendemail()
            
        # check the weather    
        if "weather" in data:
            city_id = get_city_id()
            if city_id == False:
                break
            else:
                weather_data = get_weather_data(city_id)
                forecast = get_forecast(weather_data)
            
        # map
        if "where is" in data:
            data = data.split(" ")
            location = ""
            for i in range(2, len(data)):
                location += data[i]
            speak("Hold on, I will show you where " + location + " is.")
            os.system("chromium-browser https://www.google.nl/maps/place/" + location + "/&amp;")
            
            # Setting language for wikipedia
            wikipedia.set_lang("en")
            speak(wikipedia.summary(location, sentences = 2))
            
        #twitter
        if "Twitter" in data:
            tweet()
        
        #twitter
        if "tell me something about" in data:
            data = data.split(" ")
            infom = ""
            for i in range(4, len(data)):
                infom += data[i]
            # Setting language for wikipedia
            wikipedia.set_lang("en")
            try:
                speak(wikipedia.summary(infom, sentences = 2))
            except wikipedia.exceptions.PageError:
                speak("No information in Wikipedia about " + infom)
            except wikipedia.exceptions.DisambiguationError:
                speak("Can you specify the information")
        if "tell me about" in data:
            data = data.split(" ")
            infom = ""
            for i in range(3, len(data)):
                infom += data[i]
            # Setting language for wikipedia
            wikipedia.set_lang("en")
            try:
                speak(wikipedia.summary(infom, sentences = 2))
            except wikipedia.exceptions.PageError:
                speak("No information in Wikipedia about " + infom)
            except wikipedia.exceptions.DisambiguationError:
                speak("Can you specify the information")
        
        if "message" in data:
            sendSMS()
        
        if "thank you" in data:
            break
            
if __name__ == "__main__":
    # initialization
    speak("Hi, what can I do for you?")
    jarvis()
    #turnOnCamera()
    #sendSMS()
