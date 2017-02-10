
##!/usr/bin/env python

import sys
import json
import urllib
import subprocess
import pycurl
import StringIO
import os.path
import base64 
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT

def transcribe(duration):

	key = '<KEY>'
	stt_url = 'https://speech.googleapis.com/v1beta1/speech:syncrecognize?key=' + key
	filename = 'test.flac'

	#Do nothing if audio is playing
	#------------------------------------
	if isAudioPlaying():
		print time.strftime("%Y-%m-%d %H:%M:%S ")  + "Audio is playing"
		return ""

	

	#Record sound
	#----------------

 	print "listening .."
    	os.system(
        'arecord -D plughw:0,0 -f cd -c 1 -t wav -d ' + str(duration) + '  -q -r 16000 | flac - -s -f --best --sample-rate 16000 -o ' + filename)
    	

	#Check if the amplitude is high enough
	#---------------------------------------
	cmd = 'sox ' + filename + ' -n stat'
	p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	soxOutput = p.stdout.read()
	#print "Popen output" + soxOutput

	
	maxAmpStart = soxOutput.find("Maximum amplitude")+24
	maxAmpEnd = maxAmpStart + 7
	
	#print "Max Amp Start: " + str(maxAmpStart)
	#print "Max Amop Endp: " + str(maxAmpEnd)

	maxAmpValueText = soxOutput[maxAmpStart:maxAmpEnd]
	
	
	print "Max Amp: " + maxAmpValueText

	maxAmpValue = float(maxAmpValueText)

	if maxAmpValue < 0.1 :
		#print "No sound"
		#Exit if sound below minimum amplitude
		return ""	
	

	#Send sound  to Google Cloud Speech Api to interpret
	#----------------------------------------------------
	
	print time.strftime("%Y-%m-%d %H:%M:%S ")  + "Sending to google api"


  	# send the file to google speech api
	c = pycurl.Curl()
	c.setopt(pycurl.VERBOSE, 0)
	c.setopt(pycurl.URL, stt_url)
	fout = StringIO.StringIO()
	c.setopt(pycurl.WRITEFUNCTION, fout.write)
 
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])

	with open(filename, 'rb') as speech:
		# Base64 encode the binary audio file for inclusion in the JSON
        	# request.
        	speech_content = base64.b64encode(speech.read())

	jsonContentTemplate = """{
  		'config': {
      			'encoding':'FLAC',
      			'sampleRate': 16000,
      			'languageCode': 'en-GB',
			'speechContext': {
    				'phrases': [
    					'jarvis'
  				],
  			},
  		},
  		'audio': {
      		'content':'XXX'
  		}
	}"""


	jsonContent = jsonContentTemplate.replace("XXX",speech_content)

	#print jsonContent

	start = time.time()

	c.setopt(pycurl.POSTFIELDS, jsonContent)
	c.perform()


	#Extract text from returned message from Google
	#----------------------------------------------
	response_data = fout.getvalue()


	end = time.time()
	#print "Time to run:" 
	#print(end - start)


	#print response_data

	c.close()
	
	start_loc = response_data.find("transcript")
    	temp_str = response_data[start_loc + 14:]
	#print "temp_str: " + temp_str
    	end_loc = temp_str.find("\""+",")
    	final_result = temp_str[:end_loc]
	#print "final_result: " + final_result
    	return final_result


def isAudioPlaying():
	
	audioPlaying = False 

	#Check processes using ps
        #---------------------------------------
        cmd = 'ps -C omxplayer,mplayer'
	lineCounter = 0
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        for ln in p.stdout:
		lineCounter = lineCounter + 1
		if lineCounter > 1:
			audioPlaying = True
			break

	return audioPlaying ; 



def listenForCommand(): 
	
	command  = transcribe(3)
	
	print time.strftime("%Y-%m-%d %H:%M:%S ")  + "Command: " + command 

	success=True 

	if not command:
	   return False

	if command.lower().find("light")>-1  and  command.lower().find("on")>-1   :
		subprocess.call(["/usr/local/bin/tdtool", "-n 1"])
			
	elif command.lower().find("light")>-1  and  command.lower().find("off")>-1   :
		subprocess.call(["/usr/local/bin/tdtool", "-f 1"])
	elif command.lower().find("news")>-1 :
                os.system('python getNews.py')

 	elif command.lower().find("weather")>-1 :
               	os.system('python getWeather.py')
	
	elif command.lower().find("pray")>-1 :
                os.system('python sayPrayerTimers.py')
	
        elif command.lower().find("time")>-1 :
                subprocess.call(["/home/pi/Documents/speech.sh", time.strftime("%H:%M") ])
	
	elif command.lower().find("tube")>-1 :
                 os.system('python getTubeStatus.py')

	elif command.lower().find("who are you")>-1 :
                subprocess.call('echo "I am JARVIS" | /usr/bin/festival --tts', shell=True)

	elif command.lower().find("who created you")>-1 :
                subprocess.call('echo "Tony Stark Sir" | /usr/bin/festival --tts', shell=True)

	elif command.lower().find("who is your friend")>-1 :
                subprocess.call('echo "Vedant is my friend Sir" | /usr/bin/festival --tts', shell=True)

	elif command.lower().find("who are the avengers")>-1 :
                subprocess.call('echo "Iron Man, Captain America, Hulk, Hawkeye, Black Widow and Thor are the avengers Sir" | /usr/bin/festival --tts', shell=True)

	elif command.lower().find("thank you")>-1 :
                subprocess.call('echo "You are most welcome Sir" | /usr/bin/festival --tts', shell=True)

	else:
                subprocess.call('echo "Sorry sir I dont know" | /usr/bin/festival --tts', shell=True)
		success=False

	return success 



print time.strftime("%Y-%m-%d %H:%M:%S ")  + "Launched speechAnalyser.py"


while True:
		
	sys.stdout.flush() 
	
	#Listen for trigger word
        spokenText = transcribe(2) ;
	
	if len(spokenText) > 0: 
        	print time.strftime("%Y-%m-%d %H:%M:%S ")  + "Trigger word: " + spokenText

        triggerWordIndex  = spokenText.lower().find("jarvis")

        if triggerWordIndex >-1:
		#If trigger word found, listen for command 
                subprocess.call(["aplay", "beep-3.wav"])
                subprocess.call('echo "How can I help Sir ?" | /usr/bin/festival --tts', shell=True)
		success = listenForCommand()	
		
		if not success:
			subprocess.call(["aplay", "beep-3.wav"])
			listenForCommand()
	
