
'''
	import pathlib
	THIS_FOLDER = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	SEARCH = normpath (join (THIS_FOLDER, "../.."))

	import BODY_SCAN
	BODY_SCAN.START (
		GLOB 		= SEARCH + '/**/*STATUS.py'
	)
'''

import glob

from BOTANIST.PORTS.FIND_AN_OPEN_PORT import FIND_AN_OPEN_PORT

from .START_MULTIPLE_PROCESSES import START_MULTIPLE_PROCESSES

def CHECK_STATUS_LOCATION ():
	import pathlib
	THIS_FOLDER = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	CHECK_STATUS = normpath (join (THIS_FOLDER, "SCAN/__init__.py"))
	
	return CHECK_STATUS

def START (
	GLOB 		= "",
	#DB_FOLDER 	= DB_FOLDER
):
	FINDS = glob.glob (GLOB, recursive = True)
	
	START_PORT = 40000;
	PORT = START_PORT;
	
	print ()
	print ("SEARCHING FOR GLOB:")
	print ("	", GLOB)
	print ()
	
	PORTS = []
	PROCESSES = []
	for FOUND in FINDS:
		print ("	FOUND:", FOUND)
		
		PORTS.append (PORT)
		
		PROCESSES.append ({
			"STRING": f'python3 { CHECK_STATUS_LOCATION () }  KEG OPEN --port { PORT }',
			"CWD": None
		})
		
		PORT += 1;
		
	print ()
	print ("	FINDS COUNT:", len (FINDS))
	print ();

	PROCS = START_MULTIPLE_PROCESSES (
		PROCESSES = PROCESSES
	)
	
	import time
	time.sleep (0.5)
	
	REQUEST_ADDRESS = f'http://127.0.0.1:{ PORTS [0] }'
	
	import requests
	r = requests.put (
		REQUEST_ADDRESS, 
		data = { 
			'FIND': FINDS [0]
		}
	)
	
	print ()
	print ("REQUEST ADDRESS :", REQUEST_ADDRESS)
	print ("REQUEST STATUS  :", r.status_code)
	print ("REQUEST STATUS  :", r.text)
	print ()
	
	EXIT 			= PROCS ["EXIT"]
	PROCESSES 		= PROCS ["PROCESSES"]

	#print (PROCS)

	time.sleep (2.5)
	
	#EXIT ()