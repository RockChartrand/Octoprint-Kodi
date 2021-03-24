#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import urllib
import glob
import requests
import sys

import xbmc, xbmcaddon, xbmcgui, xbmcvfs
from datetime import datetime, timedelta

ACTION_PREVIOUS_MENU = 10
ACTION_BACKSPACE = 110
ACTION_NAV_BACK = 92
ACTION_STOP = 13
ACTION_SPACE = 12
ACTION_ENTER = 7
ACTION_SELECT = 93

__addon__ = xbmcaddon.Addon()
api = __addon__.getSetting("api1")
host = __addon__.getSetting("url1")


data_path = xbmc.translatePath(__addon__.getAddonInfo('profile'))
black = os.path.join(__addon__.getAddonInfo('path'), 'resources', 'media', 'black.png')

coords = (0, 0, 1280, 720)

url = "http://" + host + "/webcam/?action=snapshot"


def file_fmt():
    return os.path.join(data_path, "{0}.{{0}}.jpg".format(time.time()))


class CamView(xbmcgui.WindowDialog):
	def __init__(self):
		self.s = requests.Session()
		headers = {
			'X-Api-Key': api,
			'Content-Type': 'application/json'
			}
		self.s.headers.update(headers)
		self.addControl(xbmcgui.ControlImage(0, 0, 1380, 720, black))
		image_file_fmt = file_fmt()
		image_file = image_file_fmt.format(1)
		urllib.urlretrieve(url, image_file)
		self.cam = xbmcgui.ControlImage(*coords, filename=image_file, aspectRatio=1)
		self.addControl(self.cam)
		self.addControl(xbmcgui.ControlLabel(0, 0, 1280, 720, "3D PRINTER STATUS", alignment = 0x00000000, font="lyr2b", textColor="0xFF7ACAFE"))
		self.closing = False
		temp = "Loading..."
		self.status = xbmcgui.ControlLabel(0, 70, 1280, 720, temp, alignment = 0x00000000, font="Font-MusicVis-Info", textColor="0xFFFFFFFF")
		self.jobname = xbmcgui.ControlLabel(0, 110, 1280, 720, temp, alignment = 0x00000000, font="Font-MusicVis-Info", textColor="0xFFFFFFFF")
		self.progress = xbmcgui.ControlLabel(0, 150, 1280, 720, temp, alignment = 0x00000000, font="Font-MusicVis-Info", textColor="0xFFFFFFFF")
		self.tempstat = xbmcgui.ControlLabel(0, 190, 1280, 720, temp, alignment = 0x00000000, font="Font-MusicVis-Info", textColor="0xFFFFFFFF")
# added to test:
#		self.test = xbmcgui.ControlLabel(0, 220, 1280, 720, temp, alignment = 0x00000000, font="Font-MusicVis-Info", textColor="0xFFFFFFFF")		
		self.addControl(self.status)
		self.addControl(self.jobname)
		self.addControl(self.progress)		
		self.addControl(self.tempstat)
# added to test:
#		self.addControl(self.test)
		
	def __enter__(self):
		return self

	def get_bed_temp(self):
		data = self.s.get('http://' + host + '/api/printer/bed').content.decode('utf-8').split(',')
		for line in data:
			if 'actual' in line:
				return line[line.find('actual')+8:line.find('.')]
		return "N/A"

	def get_bed_target(self):
		data = self.s.get('http://' + host + '/api/printer/bed').content.decode('utf-8').split(',')
		for line in data:
			if 'target' in line:
				return line[line.find('"target"')+9:line.find('.')]
		return "N/A"
		
	def get_extruder_current_temp(self):
		data = self.s.get('http://' + host + '/api/printer/tool').content.decode('utf-8').split(',')
		for line in data:
			if 'actual' in line:
				return line[line.find('actual')+8:line.find('.')]
		return "N/A"

	def get_extruder_target_temp(self):
		data = self.s.get('http://' + host + '/api/printer/tool').content.decode('utf-8').split(',')
		for line in data:
			if 'target' in line:
				return line[line.find('"target"')+9:line.find('.')]
		return "N/A"
		

	def get_file_printing(self):
		data = self.s.get('http://' + host + '/api/job').content.decode('utf-8').split(',')
		for line in data:
				if 'name' in line:
					return line[line.find('name')+7:line.find('name')+20].strip()
		return "N/A"
		
	def get_print_progress(self):
		data = self.s.get('http://' + host + '/api/job').content.decode('utf-8').split(',')
		for line in data:
			if 'completion' in line:
					line = line[line.find('"completion"')+13:line.find('completion')+14]
					line = line.replace('.', '')
					return line
		return "N/A"

	def get_estimatePrinttime(self):
		data = self.s.get('http://' + host + '/api/job').content.decode('utf-8').split(',')
		for line in data:
			if 'printTime' in line:
					line = line.replace('"printTime":', '')
					return int(line)
		return "N/A"
			
	def get_printTimeLeft(self):
		data = self.s.get('http://' + host + '/api/job').content.decode('utf-8').split(',')
		for line in data:
			if 'printTimeLeft' in line:
					line = line.replace('"printTimeLeft":', '')
					return int(line)
		return "N/A"
		
	def get_printerState(self):
		data = self.s.get('http://' + host + '/api/job').content.decode('utf-8').split(',')
		for line in data:
			if 'state' in line:
					return line[line.find(':')+1:line.find('}')].replace('"', '').strip()
		return "N/A"


# added to test:		
	def get_test(self):
		data = self.s.get('http://' + host + '/api/job').content.decode('utf-8').split(',')
		for line in data:
			if 'completion' in line:
					line = line.replace('"progress":{"completion":', '')
					return line
		return "TEST FAILED"
		
	def pausePrint(self):
		r = self.s.post('http://' + host + '/api/job', json={'command': 'pause'})


		
	def onAction(self, action):
		print str(action)
		if action in (ACTION_PREVIOUS_MENU, ACTION_BACKSPACE, ACTION_NAV_BACK, ACTION_STOP):
			self.stop()
		elif action in (ACTION_SPACE, ACTION_ENTER, ACTION_SELECT):
			self.pausePrint()


	def start(self):
		self.show()
		while(not self.closing):
			image_file_fmt = file_fmt()
			printerstate = "Printer State: " + str(self.get_printerState())			
			nozzeltemp = str(self.get_extruder_current_temp())
			nozzeltarget = str(self.get_extruder_target_temp())
			heatbed = self.get_bed_temp()
			bedtarget = str(self.get_bed_target())
			tempsline = "Nozzle: " + str(nozzeltemp) + "°C" + " T: " + nozzeltarget + "°C" + " | Bed: " + str(heatbed) + "°C" + " T: " + bedtarget + "°C"
			jobline = "File: " + str(self.get_file_printing())
# added to test:
#			test = "test: " + str(self.get_printTimeLeft())
			sec = timedelta(seconds=self.get_printTimeLeft())
			sec2 = timedelta(seconds=self.get_estimatePrinttime())
			d = datetime(1,1,1) + sec
			d2 = datetime(1,1,1) + sec2			
			timeleft = "Elapsed Time: " + ( str(d2.day-1) + " days " if d2.day-1 else "" ) + str(d2.hour) + ":" + str(d2.minute).zfill(2) + ":" + str(d2.second).zfill(2) + " |  Remaining: " + ( str(d.day-1) + " days " if d.day-1 else "" ) + str(d.hour) + ":" + str(d.minute).zfill(2) + ":" + str(d.second).zfill(2) + " | Complete: " + str(self.get_print_progress()) + "%"
			image_file = image_file_fmt.format(1)
			urllib.urlretrieve(url, image_file)
			viewer.cam.setImage(image_file, useCache=False)
			viewer.status.setLabel(str(printerstate))
			viewer.jobname.setLabel(str(jobline))
			viewer.progress.setLabel(str(timeleft))			
			viewer.tempstat.setLabel(str(tempsline))
# added to test:
#			viewer.test.setLabel(str(test))	
			xbmc.sleep(50)


	def stop(self):
		self.closing = True
		self.close()
        
	def __exit__(self, exc_type, exc_value, traceback):
		for f in glob.glob(os.path.join(data_path, "*.jpg")):
			os.remove(f)


with CamView() as viewer:
    viewer.start()

del viewer
