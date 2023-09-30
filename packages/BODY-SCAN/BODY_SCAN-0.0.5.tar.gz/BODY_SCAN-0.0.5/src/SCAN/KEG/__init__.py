

def ADD_PATHS_TO_SYSTEM (PATHS):
	import pathlib
	FIELD = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	for PATH in PATHS:
		sys.path.insert (0, normpath (join (FIELD, PATH)))

from .SCAN import SCAN

import json

def TAP (
	PORT = 0
):
	print ("OPENING KEG ON PORT:", PORT)

	from flask import Flask, request

	app = Flask (__name__)

	@app.route ("/", methods = [ 'GET' ])
	def HOME ():	
		return "?"

	@app.route ("/", methods = [ 'PUT' ])
	def HOME_POST ():
		print ("@ HOME PUT", request.data)
	
		DATA = json.loads (request.data.decode ('utf8'))
		print ("DATA:", DATA)

		FINDS = DATA ['FINDS']
		MODULE_PATHS = DATA ['MODULE PATHS']



		ADD_PATHS_TO_SYSTEM (MODULE_PATHS)

		STATUS = {
			"PATHS": [],
			"STATS": {
				"PASSES": 0,
				"ALARMS": 0
			}
		}

		for FIND in FINDS:
			SCAN_STATUS = SCAN (FIND)
		
			STATUS ["STATS"] ["PASSES"] += SCAN_STATUS ["STATS"] ["PASSES"]
			STATUS ["STATS"] ["ALARMS"] +=	SCAN_STATUS	["STATS"] ["ALARMS"]
		
			STATUS ["PATHS"].append ({
				"PATH": FIND,
				** SCAN_STATUS
			})
			
			
		return json.dumps (STATUS, indent = 4)
		
	app.run (
		port = PORT
	)