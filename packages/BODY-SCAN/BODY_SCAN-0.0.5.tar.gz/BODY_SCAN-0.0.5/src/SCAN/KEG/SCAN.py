
def SCAN_FILE (PATH):
	with open (PATH, mode = 'r') as file:
		STRING = file.read ()
		return STRING


import io
import sys
import traceback
def GET_EXCEPTION_TRACEBACK (EXCEPTION : Exception) -> str:
	try:
		file = io.StringIO ()
		traceback.print_exception (EXCEPTION, file = file)
		
		return file.getvalue ().rstrip ()
	except Exception:
		pass;
		
	return 'An exception occurred while calculating trace.'


import json
import time
from time import sleep, perf_counter as pc
'''
TIME_START = pc ()
sleep (1)
TIME_ELAPSED = pc () - TIME_START
'''


def SCAN (FIND):
	PATH = {}
	
	FINDINGS = {}
	STATS = {
		"PASSES": 0,
		"ALARMS": 0
	}

	EX = "?"

	try:
		
		CONTENTS = SCAN_FILE (FIND)
				
		CONTENTS += '''
______BODY_SCAN ["CHECKS"] = CHECKS;			
		'''
		
		______BODY_SCAN = {}
		exec (CONTENTS, { '______BODY_SCAN': ______BODY_SCAN })
		CHECKS = ______BODY_SCAN ['CHECKS']
		
		
		
		for CHECK in CHECKS:
			try:
				TIME_START = pc ()
				#print ("TIME_START:", CHECK, TIME_START)
				CHECKS [ CHECK ] ()
				TIME_END = pc ()
				TIME_ELAPSED = TIME_END - TIME_START
				
				#print ("TIME_END:", CHECK, TIME_END)				
				#print ("TIME_ELAPSED:", CHECK, TIME_ELAPSED)
				
				FINDINGS [ CHECK ] = {
					"PASSED": True,
					"ELAPSED": [ TIME_ELAPSED, "SECONDS" ]
				}
				
				STATS ["PASSES"] += 1
				
			except Exception as E:
				#print ("E:", E)
				#print ("E:", type (repr (E)))

				TRACE = GET_EXCEPTION_TRACEBACK (E)
				
				FINDINGS [ CHECK ] = {
					"PASSED": False,
					"EXCEPTION": repr (E),
					"EXCEPTION TRACE": TRACE
				}
				
				STATS ["ALARMS"] += 1
		
		
		return {
			"STATS": STATS,			
			"FINDINGS": FINDINGS
		}
		
	except Exception as E:		
		EX = E;

	return {
		"ALARM": "AN EXCEPTION OCCURRED WHILE SCANNING PATH",
		"EXCEPTION": EX,
		"EXCEPTION TRACE": TRACE
	}