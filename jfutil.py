import re
import jfexceptions

def debug(verbose, message):
	if verbose:
		if type(message) == list:
			for line in message:
				print("jetfreq.py: {}".format(line))
		else:
			print("jetfreq.py: {}".format(message))

def append_to_report(report, event_freqs, event_type):
	report.append(':: {}'.format(event_type))
	for event in event_freqs:
		report.append('::: {}% || {}'.format(event.perc, event.path))
	return report
			
def format_report_by_process(params, event_freqs):
	report = []
	report.append(': RESULTS FOR {} {}'.format('MODLOAD' if params['by_modload'] else 'PROCESS', params['search_name'].upper()))
	if len(event_freqs['modloads']) > 0:
		report = append_to_report(report, event_freqs['modloads'], 'MODLOADS')
	if len(event_freqs['regmods']) > 0:
		report = append_to_report(report, event_freqs['regmods'], 'REGMODS')
	if len(event_freqs['childprocs']) > 0:
		report = append_to_report(report, event_freqs['childprocs'], 'CHILDPROCS')
	if len(event_freqs['filemods']) > 0:
		report = append_to_report(report, event_freqs['filemods'], 'FILEMODS')
	if len(event_freqs['netconns']) > 0:
		report = append_to_report(report, event_freqs['netconns'], 'NETCONNS')
	if len(event_freqs['crossprocs']) > 0:
		report = append_to_report(report, event_freqs['crossprocs'], 'CROSSPROCS')
	report.append(': END')
	return report

def format_report_by_modload(params, data):
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
