





"""
	from abaculate.MOVES.STRATEGIZE import STRATEGIZE
	
	STRATEGIES = STRATEGIZE (
		MOVES = [
			{ 
				"STRING": 'python3 -m http.server 9000',
				"CWD": None
			},
			{
				"STRING": 'python3 -m http.server 9001',
				"CWD": None
			}
		]
	)
	
	EXIT 		= STRATEGIES ["EXIT"]
	MOVES 		= STRATEGIES ["MOVES"]

	time.sleep (.5)
	
	
	EXIT ()
"""


from subprocess import Popen
import shlex
import atexit

def STRATEGIZE (
	MOVES = [],
	WAIT = False
):
	MOVES_LIST = []

	for MOVE in MOVES:
		if (type (MOVE) == str):
			print ("STARTING MOVE", MOVE)
		
			MOVES_LIST.append (
				Popen (
					shlex.split (MOVE)
				)
			)
			
		elif (type (MOVE) == dict):
			print ("STARTING MOVE", MOVE)
		
			MOVE_STRING = MOVE ["STRING"]
		
			CWD = None
			ENV = None
		
			if ("CWD" in MOVE):
				CWD = MOVE ["CWD"]
			
			if ("ENV" in MOVE):
				ENV = MOVE ["ENV"]
		
			MOVES_LIST.append (
				Popen (
					shlex.split (MOVE_STRING),
					
					cwd = CWD,
					env = ENV
				)
			)

	
	def EXIT ():
		print ("ATEXIT EXITING")

		for MOVE in MOVES_LIST:
			print ("ENDING MOVE ATEXIT", MOVE);
			MOVE.kill ()

		#exit ();

	atexit.register (EXIT)
	
			
	if (WAIT):
		for MOVE in MOVES_LIST:
			#
			#	https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait
			#
			MOVE.wait ()	
		
	return {
		"MOVES": MOVES,
		"EXIT": EXIT
	}
	
	
	
	


