





"""
	from botanist.PROCESSES.START_MULTIPLE import START_MULTIPLE
	
	PROCS = START_MULTIPLE (
		PROCESSES = [
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
	
	EXIT 			= PROCS ["EXIT"]
	PROCESSES 		= PROCS ["PROCESSES"]

	time.sleep (.5)
	
	EXIT ()
"""


from subprocess import Popen
import shlex
import atexit

def START_MULTIPLE (
	PROCESSES = [],
	WAIT = False
):
	PROCESSES_LIST = []

	for PROCESS in PROCESSES:
		if (type (PROCESS) == str):
			#print ("STARTING PROCESS", PROCESS)
		
			PROCESSES_LIST.append (
				Popen (
					shlex.split (PROCESS)
				)
			)
			
		elif (type (PROCESS) == dict):
			#print ("STARTING PROCESS", PROCESS)
		
			PROCESS_STRING = PROCESS ["STRING"]
		
			CWD = None
			ENV = None
		
			if ("CWD" in PROCESS):
				CWD = PROCESS ["CWD"]
			
			if ("ENV" in PROCESS):
				ENV = PROCESS ["ENV"]
		
			PROCESSES_LIST.append (
				Popen (
					shlex.split (PROCESS_STRING),
					
					cwd = CWD,
					env = ENV
				)
			)

	
	def EXIT ():
		#print ("ATEXIT EXITING")

		for PROCESS in PROCESSES_LIST:
			#print ("ENDING PROCESS ATEXIT", PROCESS);
			PROCESS.kill ()

		#exit ();

	atexit.register (EXIT)
	
	if (WAIT):
		for PROCESS in PROCESSES_LIST:
			#
			#	https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait
			#
			PROCESS.wait ()	
		
	return {
		"PROCESSES": PROCESSES,
		"EXIT": EXIT
	}
	
	
	
	


