import re
import jfexceptions
import os
from jfanalyze import sort_events
from datetime import datetime

def debug(verbose, message):
	if verbose:
		if type(message) == list:
			for line in message:
				print("jetfreq.py: {}".format(line))
		else:
			print("jetfreq.py: {}".format(message))

def append_to_report(report, event_freqs, event_type):
	report.append('::::::')
	report.append(':::::: {}'.format(event_type))
	report.append(':::::: {:^8} | {:^8} | {:^}'.format('Count', 'Freq', 'Path'))
	for event in event_freqs:
		report.append(':::::: {:^8d} | {:^8.4f} | {}'.format(event.count, event.perc, event.path))
	return report
			
def format_report_by_process(params, event_freqs):
	debug(params['verbose'], 'Generating report')
	report = []
	
	# check for no results
	no_results = True
	for key in event_freqs:
		if not event_freqs[key] == None and len(event_freqs[key]) > 0:
			no_results = False
			break
	if no_results == True:
		report.append(':::::: NO RESULTS FOR PROCESS {}'.format(params['search_name'].upper()))
		return report
	
	# if there are results, add them to the report
	report.append('::::::')
	report.append(':::::: RESULTS FOR PROCESS {}'.format(params['search_name'].upper()))
	report.append('::::::')
	report.append(':::::: FILTERS')
	report.append(':::::: start_time = {}'.format(params['start_time']))
	report.append(':::::: threshold = {}%'.format(params['threshold']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	if not event_freqs['modloads'] == None and len(event_freqs['modloads']) > 0:
		report = append_to_report(report, event_freqs['modloads'], 'MODLOADS')
	if not event_freqs['regmods'] == None and len(event_freqs['regmods']) > 0:
		report = append_to_report(report, event_freqs['regmods'], 'REGMODS')
	if not event_freqs['childprocs'] == None and len(event_freqs['childprocs']) > 0:
		report = append_to_report(report, event_freqs['childprocs'], 'CHILDPROCS')
	if not event_freqs['filemods'] == None and len(event_freqs['filemods']) > 0:
		report = append_to_report(report, event_freqs['filemods'], 'FILEMODS')
	if not event_freqs['netconns'] == None and len(event_freqs['netconns']) > 0:
		report = append_to_report(report, event_freqs['netconns'], 'NETCONNS')
	if not event_freqs['crossprocs'] == None and len(event_freqs['crossprocs']) > 0:
		report = append_to_report(report, event_freqs['crossprocs'], 'CROSSPROCS')
	report.append(':::::: END')
	return report

def format_report_by_modload(params, data):
	pass

def out_file_by_process(params, event_freqs):
	# check ./reports dir exists, if not - create it
	try:
		os.mkdir("./reports")
	except OSError:
		pass

	# generate descriptive filename
	dt = str(datetime.now())
	dt = re.sub(r'(:|\.)', '-', dt)
	dt = re.sub(r'\s', '_', dt)
	sn = re.sub(r'\.', '-', params['search_name'].lower())
	file_path = './reports/{}_p-{}_n-{}_t-{}'.format(dt, sn, params['sample_size'], params['threshold'])
	if not params['user_name'] == None:
		file_path += '_u-{}'.format(params['user_name'].lower())
	if not params['host_name'] == None:
		file_path += '_h-{}'.format(params['host_name'].lower())
	file_path += '.csv'
	
	# check file already exists
	sn = 0
	while os.path.isfile(file_path):
		sn = sn + 1
		file_path = file_path[0:index('.csv')]
		file_path += '_' + sn + '.csv'

	# write to file
	debug(params['verbose'], 'Writing to file {}'.format(file_path))
	file = open(file_path, 'w')
	file.write('\'event_type\',\'event\',\'count\',\'freq\'\n')
	if not event_freqs['modloads'] == None:
		events = sort_events(event_freqs['modloads'])
		for event in events:
			file.write('\'modload\',\'{}\',\'{}\'\n'.format(event.path, event.count, event.perc))
	if not event_freqs['regmods'] == None:
		events = sort_events(event_freqs['regmods'])
		for event in events:
			file.write('\'regmod\',\'{}\',\'{}\'\n'.format(event.path, event.count, event.perc))
	if not event_freqs['childprocs'] == None:
		events = sort_events(event_freqs['childprocs'])
		for event in events:
			file.write('\'childproc\',\'{}\',\'{}\'\n'.format(event.path, event.count, event.perc))
	if not event_freqs['filemods'] == None:
		events = sort_events(event_freqs['filemods'])
		for event in events:
			file.write('\'filemod\',\'{}\',\'{}\'\n'.format(event.path, event.count, event.perc))
	if not event_freqs['netconns'] == None:
		events = sort_events(event_freqs['netconns'])
		for event in events:
			file.write('\'netconn\',\'{}\',\'{}\'\n'.format(event.path, event.count, event.perc))
	if not event_freqs['crossprocs'] == None:
		events = sort_events(event_freqs['crossprocs'])
		for event in events:
			file.write('\'crossproc\',\'{}\',\'{}\'\n'.format(event.path, event.count, event.perc))
	file.close()
	debug(True, 'Report written to file {}'.format(file_path))
	return file_path

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
	debug(params['verbose'], 'Importing configuration file')
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
