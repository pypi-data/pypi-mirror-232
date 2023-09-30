
def READ_FILE (PATH):
	with open (PATH, mode = 'r') as file:
		BYTES = file.read ()
		
		PRIVATE_KEY			= ECC.import_key (
			BYTES,
			curve_name		= "Ed448"
		)
		
		STRING = BYTES.hex ()

		return [ PRIVATE_KEY, BYTES, STRING ];

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
		print ("@ HOME PUT")
	
		try:
			print ("@ HOME DATA", request.form.get ('FIND'))
			print ("data:", request.get_json (force=True))
			
			return "!"
		except Exception as E:
			print (E)
	
		return "?"
		
	app.run (
		port = PORT
	)