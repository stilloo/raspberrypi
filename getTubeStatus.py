#!/usr/bin/env python

import json
import urllib2
import subprocess


url = "https://api.tfl.gov.uk/Line/northern%2Cvictoria/Status?detail=false&app_id=<YOUR TFL APP ID>&app_key=<YOUR TFL APP KEY>"

data = json.load(urllib2.urlopen(url))


for lineData in data:

	lineName = lineData["name"]
	lineStatus  =  lineData["lineStatuses"][0]["statusSeverityDescription"]
	
	lineMessage = lineStatus + " on the " + lineName + " line"

	print lineMessage

	subprocess.call(["/home/pi/Documents/speech.sh", lineMessage])

	if 'reason' in lineData["lineStatuses"][0]:
		
        	reasonText = lineData["lineStatuses"][0]["reason"]
		reasonText  = reasonText[:99]
		print reasonText
		subprocess.call(["/home/pi/Documents/speech.sh", reasonText])

	
