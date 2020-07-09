import re
import jfexceptions

def debug(verbose, message):
	if verbose:
		print("jetfreq.py: {}".format(message))

def format_report(params, data):
	# format the data into a human-readable format
	pass

def out_file(params, data):
	# writes the report to a file
	pass

def show_usage():
	h = open("README.txt", "r")
	usage = ""
	capture = False
	for line in h:
		if capture == False and len(usage) > 0:
			break
		elif capture == True:
			usage += line
			if re.match(r'^show_help', line) != None: 
				capture = False
		elif re.match(r'^Usage:', line) != None:
			capture = True
	print("\nUSAGE:\n{}".format(usage))

def show_help():
	h = open("README.txt", "r")
	print(h.read())

def import_conf(params):
	conf = open('./conf/jetfreq.cfg', 'r')
	for line in conf:
		if line.startswith('#'):
			pass
		else:
			params[line.split('=')[0].lower().strip()] = line.split('=')[1].strip()
	conf.close()
	return params

def get_event_paths(events, col):
	paths = []
	for event in events:
		paths.append(event.split('|')[col])
	return paths
