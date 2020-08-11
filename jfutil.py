# THIS MODULE CONTAINS VARIOUS UTILITY FUNCTIONS USED
# BY ALL OTHER MODULES IN JETFREQ

import re
import jfexceptions
import os
from jfanalyze import sort_events
from jfanalyze import EventFreq
from jfanalyze import EventDiff
from jfanalyze import DiffType
from datetime import datetime

# THIS FUNCTION FORMATS AND WRITES DEBUG INFORMATION TO STDOUT
def debug(verbose, message):
	if verbose:
		if type(message) == list:
			for line in message:
				print("jetfreq.py: {}".format(line))
		else:
			print("jetfreq.py: {}".format(message))

# THIS FUNCTION SORT A LIST OF EVENT_DIFF OBJECTS 
# ALPHABETICALLY BY THEIR DIFFTYPE VALUE
def sort_event_diffs_by_type(event_diffs):
	for i in range(len(event_diffs)):
		j = i + 1
		while j < len(event_diffs):
			if event_diffs[i].difftype > event_diffs[j].difftype:
				hold = event_diffs[i]
				event_diffs[i] = event_diffs[j]
				event_diffs[j] = hold
			j = j + 1
	return event_diffs

# THIS FUNCTION FORMATS THE CONTENTS OF EVENT_DIFF OBJECTS
# AND APPENDS IT TO THE REPORT LIST 
def append_diff_to_report(report, event_diffs, event_type):
	dt = DiffType()
	report.append('::::::')
	report.append(':::::: {}'.format(event_type))

	event_diffs = sort_event_diffs_by_type(event_diffs)
	for diff in event_diffs:
		if diff.difftype == dt.MISS_FM_REP:
			report.append(':::::: {} | {}'.format(diff.difftype, diff.target_event.path))
		elif diff.difftype == dt.MISS_FM_TAR:
			report.append(':::::: {} | {}'.format(diff.difftype, diff.representative_event.path))
		elif diff.difftype == dt.HIGH_FQ_REP:
			report.append(':::::: {} | {} | {} > {}'.format(diff.difftype, diff.target_event.path, diff.representative_event.perc, diff.target_event.perc))
		elif diff.difftype == dt.HIGH_FQ_TAR:
			report.append(':::::: {} | {} | {} > {}'.format(diff.difftype, diff.target_event.path, diff.target_event.perc, diff.representative_event.perc))
		elif not re.match(r'TAR_MISS_', diff.difftype) == None:
			report.append(':::::: {} | {}'.format(diff.difftype, diff.representative_event.path))
		elif not re.match(r'REP_MISS_', diff.difftype) == None:
			report.append(':::::: {} | {}'.format(diff.difftype, diff.target_event.path))
	return report

# THIS FUNCTION FORMATS THE CONTENTS OF EVENT_FREQ OBJECTS
# AND APPENDS IT TO THE REPORT LIST
def append_to_report(report, event_freqs, event_type):
	report.append('::::::')
	report.append(':::::: {}'.format(event_type))
	for event in event_freqs:
		report.append(':::::: {}/{} | {:8.4f} | {}'.format(event.count, event.total, event.perc, event.path))
	return report

# THIS IS THE MAIN FUNCTION FOR FORMATTING THE RESULTS
# OF A --BY-PROCESS MODE QUERY INTO A REPORT
def format_report_by_process(params, event_freqs):

	debug(params['verbose'], 'Generating report')
	report = []
	
	# CHECK THAT THERE ARE, IN FACT, RESULTS TO REPORT
	no_results = True
	for key in event_freqs:
		if not event_freqs[key] == None and len(event_freqs[key]) > 0:
			no_results = False
			break
	# OTHERWISE, YOU SHALL NOT PASS
	if no_results == True:
		report.append('::::::')
		report.append(':::::: NO RESULTS FOR PROCESS {}'.format(params['search_name'].upper()))
		return report
	
	# APPEND THE REPORT HEADERS TO THE REPORT
	report.append('::::::')
	report.append(':::::: RESULTS FOR PROCESS {}'.format(params['search_name'].upper()))
	report.append('::::::')
	report.append(':::::: FILTERS')
	report.append(':::::: start_time = {}'.format(params['start_time']))
	if params['threshold_lt'] != None:
		report.append(':::::: threshold (less than) = {}%'.format(params['threshold_lt']))
	if params['threshold_gt'] != None:
		report.append(':::::: threshold (greater than) = {}%'.format(params['threshold_gt']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	elif not params['exclude_user'] == None:
		report.append(':::::: exclude_user = {}'.format(params['exclude_user']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	elif not params['exclude_host'] == None:
		report.append(':::::: exclude_host = {}'.format(params['exclude_host']))

	# APPEND THE EVENTS TO THE REPORT
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

	# CLOSE AND RETURN THE REPORT
	report.append('::::::')
	report.append(':::::: END')
	return report

# THIS IS THE MAIN FUNCTION FOR FORMATTING THE RESULTS OF A 
# --BY-EVENT QUERY INTO A REPORT
def format_report_by_event(params, event_freqs):
	
	debug(params['verbose'], 'Generating report')	
	report = []
	
	# GET THE EVENT TYPE THAT WAS IN THE QUERY
	event_type = get_event_type_flags(params)	
	if event_type == 'm':
		event_type = 'MODLOAD'
	elif event_type == 'r':
		event_type = 'REGMOD'
	elif event_type == 'f':
		event_type = 'FILEMOD'
	elif event_type == 'c':
		event_type = 'CHILDMOD'
	elif event_type == 'd':
		event_type = 'NETCONN'

	# IF THERE ARE NO RESULTS, GO NO FURTHER
	if len(event_freqs) == 0:
		report.append('::::::')
		report.append(':::::: NO RESULTS FOR {} {}'.format(event_type, params['search_name'].upper()))
		return report
	
	# APPEND THE REPORT HEADERS TO THE REPORT
	report.append('::::::')
	report.append(':::::: RESULTS FOR {} {}'.format(event_type, params['search_name'].upper()))
	report.append('::::::')
	report.append(':::::: FILTERS')
	report.append(':::::: start_time = {}'.format(params['start_time']))
	if params['threshold_lt'] != None:
		report.append(':::::: threshold (less than) = {}%'.format(params['threshold_lt']))
	if params['threshold_gt'] != None:
		report.append(':::::: threshold (greater than) = {}%'.format(params['threshold_gt']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	elif not params['exclude_user'] == None:
		report.append(':::::: exclude_user = {}'.format(params['exclude_user']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	elif not params['exclude_host'] == None:
		report.append(':::::: exclude_host = {}'.format(params['exclude_host']))

	# APPEND THE PROCESSES TO THE REPORT
	report = append_to_report(report, event_freqs, 'PROCESSES')

	# CLOSE AND RETURN THE REPORT
	report.append('::::::')
	report.append(':::::: END')
	return report

# THIS FUNCTION TAKES A FILE NAME AND USES IT TO 
# CREATE A PARAMS JSON CONTAINER TO HOLD THE PARAMETERS
# USED IN THE SEARCH THAT GENERATED THE FILE
def get_params_from_file_name(file_name):
	# INITIALIZE JSON CONTAINER FOR PARAMETERS
	params = {
		'search_name':None,
		'regmods':False,
		'filemods':False,
		'modloads':False,
		'crossprocs':False,
		'childprocs':False,
		'netconns':False,
		'sample_size':10,
		'user_name':None,
		'exclude_user':None,
		'host_name':None,
		'exclude_host':None,
		'threshold_lt':100,
		'threshold_gt':0,
		'event_type':None
		}

	# SPLIT THE NAME AT THE DEFINED FLAGS, INTO AN ARRAY
	name_ary = re.split(r'_[hHuUtTnse]{1}-', file_name[0:len(file_name) - 4]) # trim .csv
	params['search_name'] = name_ary[1].replace('__BS__', '\\')
	params['sample_size'] = int(name_ary[3])
	params['threshold_lt'] = int(name_ary[4]) if not name_ary[4] == "None" else "None"
	params['threshold_gt'] = int(name_ary[5]) if not name_ary[5] == "None" else "None"
	flags = name_ary[2]
	if 'r' in flags:
		params['regmods'] = True
		params['event_type'] = 'REGMOD'
	if 'f' in flags:
		params['filemods'] = True
		params['event_type'] = 'FILEMOD'
	if 'm' in flags:
		params['modloads'] = True
		params['event_type'] = 'MODLOAD'
	if 'x' in flags:
		params['crossprocs'] = True
		params['event_type'] = 'CROSSPROC'
	if 'c' in flags:
		params['childprocs'] = True
		params['event_type'] = 'CHILDPROC'
	if 'd' in flags:
		params['netconns'] = True
		params['event_type'] = 'NETCONN'
	# IF THERE ARE 8 ELEMENTS IN THE NAME_ARY, THEN A USER FLAG AND A HOST FLAG WAS USED
	if len(name_ary) == 8:
		if '_u-' in file_name:
			params['user_name'] = name_ary[6]
		elif '_U-' in file_name:
			params['exclude_user'] = name_ary[6]
		if '_h-' in file_name:
			params['host_name'] = name_ary[7]
		elif '_H-' in file_name:
			params['exclude_host'] = name_ary[7]
	# IF THERE ARE 7 ELEMENTS IN THE NAME_ARY, THEN EITHER A USER FLAG OR A HOST FLAG WAS USED
	elif len(name_ary) == 7:
		if '_h-' in file_name:
			params['host_name'] = name_ary[6]
		elif '_H-' in file_name:
			params['exclude_host'] = name_ary[6]
		elif '_u-' in file_name:
			params['user_name'] = name_ary[6]
		elif '_U-' in file_name:
			params['exclude_user'] = name_ary[6]
	return params

# THIS IS THE MAIN FUNCTION FOR FORMATTING THE RESULTS OF A 
# --COMPARE-PROCESS MODE QUERY INTO A REPORT
def format_report_compare_process(params, event_freqs):
	report = []
	
	# CHECK THAT THERE ARE INDEED RESULTS
	no_results = True
	for key in event_freqs:
		if not event_freqs[key] == None and len(event_freqs[key]) > 0:
			no_results = False
			break
	# IF NOT, GO NO FURTHER
	if no_results:
		report.append('::::::')
		report.append(':::::: TARGET AND REPRESENTATIVE SAMPLES ARE THE SAME')
		return report
	
	# EXTRACT THE PARAMETERS USED TO GENERATE THE REPRESENTATIVE SAMPLE FROM ITS FILE NAME
	representative_sample_params = get_params_from_file_name(params['import_sample'])

	# APPEND THE REPORT HEADERS TO THE REPORT
	report.append('::::::')
	report.append(':::::: PROCESS COMPARISON RESULTS')
	report.append('::::::')
	report.append(':::::: REPRESENTATIVE SAMPLE PROCESS {}'.format(representative_sample_params['search_name'].upper()))
	report.append(':::::: file = {}'.format(params['import_sample'].replace('__BS__', '\\')))
	if representative_sample_params['threshold_lt'] != None:
		report.append(':::::: threshold (less than) = {}%'.format(representative_sample_params['threshold_lt']))
	if representative_sample_params['threshold_gt'] != None:
		report.append(':::::: threshold (greather than) = {}%'.format(representative_sample_params['threshold_gt']))
	report.append(':::::: sample_size = {}'.format(representative_sample_params['sample_size']))
	if not representative_sample_params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(representative_sample_params['user_name']))
	elif not representative_sample_params['exclude_user'] == None:
		report.append(':::::: exclude_user = {}'.format(representative_sample_params['exclude_user']))
	if not representative_sample_params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(representative_sample_params['host_name']))
	elif not representative_sample_params['exclude_host'] == None:
		report.append(':::::: exclude_host = {}'.format(representative_sample_params['exclude_host']))
	report.append('::::::')
	report.append(':::::: TARGET SAMPLE PROCESS {}'.format(params['search_name'].upper()))
	report.append(':::::: start_time = {}'.format(params['start_time']))
	if params['threshold_lt'] != None:
		report.append(':::::: threshold (less than) = {}%'.format(params['threshold_lt']))
	if params['threshold_gt'] != None:
		report.append(':::::: threshold (greater than) = {}%'.format(params['threshold_gt']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	elif not params['exclude_user'] == None:
		report.append(':::::: exclude_user = {}'.format(params['exclude_user']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	elif not params['exclude_host'] == None:
		report.append(':::::: exclude_host = {}'.format(params['exclude_host']))

	# APPEND THE EVENT DIFFERENCES TO THE REPORT
	for key in event_freqs:
		if not event_freqs[key] == None and len(event_freqs[key]) > 0:
			report = append_diff_to_report(report, event_freqs[key], key.upper())

	# CLOSE AND RETURN REPORT
	report.append('::::::')
	report.append(':::::: END')
	return report

# THIS IS THE MAIN FUNCTION FOR FORMATTING THE RESULTS
# OF A --COMPARE-EVENT QUERY INTO A REPORT
def format_report_compare_event(params, event_freqs):
	report = []
	
	# IF THERE ARE NO RESULTS, GO NO FURTHER
	if len(event_freqs) == 0:
		report.append('::::::')
		report.append(':::::: TARGET AND REPRESENTATIVE SAMPLES ARE THE SAME')
		return report
	
	# GET THE EVENT TYPE USED IN THE TARGET SAMPLE
	event_type = 'NETCONN'
	if params['modloads'] == True:
		event_type = 'MODLOAD'
	elif params['regmods'] == True:
		event_type = 'REGMOD'
	elif params['filemods'] == True:
		event_type = 'FILEMOD'
	elif params['childprocs'] == True:
		event_type = 'CHILDPROC'
	
	# EXTRACT THE PARAMETERS USED TO GENERATE THE REPRESENTATIVE SAMPLE FROM THE FILE NAME
	representative_sample_params = get_params_from_file_name(params['import_sample'])

	# APPEND THE REPORT HEADERS TO THE REPORT
	report.append('::::::')
	report.append(':::::: EVENT COMPARISON RESULTS')
	report.append('::::::')
	report.append(':::::: REPRESENTATIVE SAMPLE {} {}'.format(representative_sample_params['event_type'], representative_sample_params['search_name'].upper()))
	report.append(':::::: file = {}'.format(params['import_sample'].replace('__BS__', '\\')))
	report.append(':::::: threshold (less than) = {}'.format(representative_sample_params['threshold_lt']))
	report.append(':::::: threshold (greater than) = {}'.format(representative_sample_params['threshold_gt']))
	report.append(':::::: sample_size = {}'.format(representative_sample_params['sample_size']))
	if not representative_sample_params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(representative_sample_params['user_name']))
	elif not representative_sample_params['exclude_user'] == None:
		report.append(':::::: exclude_user = {}'.format(representative_sample_params['exclude_user']))
	if not representative_sample_params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(representative_sample_params['host_name']))
	elif not representative_sample_params['exclude_host'] == None:
		report.append(':::::: exclude_host = {}'.format(representative_sample_params['exclude_host']))
	report.append('::::::')
	report.append(':::::: TARGET SAMPLE {} {}'.format(event_type, params['search_name'].upper()))
	report.append(':::::: start_time = {}'.format(params['start_time']))
	report.append(':::::: threshold (less than) = {}'.format(params['threshold_lt']))
	report.append(':::::: threshold (greater than) = {}'.format(params['threshold_gt']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	elif not params['exclude_user'] == None:
		report.append(':::::: exclude_user = {}'.format(params['exclude_user']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	elif not params['exclude_host'] == None:
		report.append(':::::: exclude_host = {}'.format(params['exclude_host']))

	# APPEND THE PROCESS DIFFERENCES TO THE REPORT
	report = append_diff_to_report(report, event_freqs, 'PROCESSES')

	# CLOSE AND RETURN THE REPORT
	report.append('::::::')
	report.append(':::::: END')
	return report

# THIS FUNCTION EXTRACTS THE EVENT TYPE FLAGS
# FROM PARAMS AND RETURN THEM IN A STRING
def get_event_type_flags(params):
	flags = ""
	if params['modloads'] == True:
		flags += 'm'
	if params['regmods'] == True:
		flags += 'r'
	if params['filemods'] == True:
		flags += 'f'
	if params['crossprocs'] == True:
		flags += 'x'
	if params['childprocs'] == True:
		flags += 'c'
	if params['netconns'] == True:
		flags += 'd'
	return flags

# THIS FUNCTION IMPORTS THE CONTENTS OF A SAMPLE FILE
# AND RETURNS THEM AS A LIST OR DICTIONARY OF EVENT_FREQ OBJECTS
def import_sample(params):
	# INITIALIZE THE COLUMN INDEX VARIABLES
	search_name = None
	event_type = None
	path = None
	count = None
	total = None
	freq = None
	
	# CHECK THAT THE USER HASN'T ACCIDENTALLY COPIED DIRECTORY SECTIONS INTO THE FILEPATH
	file_path = ''
	if '/' in params['import_sample']:
		hold = params['import_sample'].split('/')
		params['import_sample'] = hold[len(hold) - 1]

	# FORMAT THE IMPORT_SAMPLE VALUE AS A FILE PATH
	file_path = './samples/{}/{}'.format('process' if params['mode'] == 'COMPARE_PROCESS' else 'event', params['import_sample'])
	
	# THE COLUMN IN THE .CSV FILE DIFFERS DEPENDING UPON WHETHER THE 
	# FILE IS THE RESULT OF A PROCESS OR EVENT SEARCH
	if params['mode'] == 'COMPARE_PROCESS':
		search_name = 0
		event_type = 1
		path = 2
		count = 3
		total = 4
		freq = 5
	elif params['mode'] == 'COMPARE_EVENT':
		search_name = 0
		path = 1
		count = 2
		total = 3
		freq = 4
	
	# INITIALIZE THE EVENT_FREQS CONTAINER AS A LIST (FOR --COMPARE-EVENT) OR DICTIONARY (FOR --COMPARE-PROCESS)
	event_freqs = [] if event_type == None else {'modloads':None, 'regmods':None, 'childprocs':None, 'filemods':None, 'netconns':None, 'crossprocs':None}
	file = open(file_path, 'r')
	skip = True
	for line in file:
		# SKIP THE FIRST LINE IN THE FILE (I.E. THE HEADERS)
		if skip:
			skip = False
		else:	
			# EXTRACT THE VALUES FROM THE LINE IN THE FILE AND REMOVE QUOTATION MARKS
			path_value = line.split(',')[path].replace('\'','')
			freq_value = line.split(',')[freq].replace('\'','')
			freq_value = freq_value.replace('\n','')
			count_value = line.split(',')[count].replace('\'','')
			total_value = line.split(',')[total].replace('\'','')
			if not event_type == None:
				# IF RUNNING IN --COMPARE-PROCESS MODE, RETRIEVE THE EVENT_TYPE VALUE
				event_type_value = '{}s'.format(line.split(',')[event_type].replace('\'',''))
				if not event_freqs[event_type_value] == None:
					event_freqs[event_type_value].append(EventFreq(path_value, freq_value, count_value, total_value))
				else:
					event_freqs[event_type_value] = []
					event_freqs[event_type_value].append(EventFreq(path_value, freq_value, count_value, total_value))
			else:
				event_freqs.append(EventFreq(path_value, freq_value, count_value, total_value))
	file.close()	
	return event_freqs

# THIS FUNCTION CHECKS WHETHER THE NECESSARY FILE DIRECTORIES
# EXISTS IN THE JETFREQ WORKING DIRECTORY AND CREATES THEM
# IF NECESSARY
def check_for_sample_dir():
	dirs = [
		"./samples",
		"./samples/process",
		"./samples/event",
		"./samples/process/diff",
		"./samples/event/diff"
	]
	for d in dirs:
		try:
			os.mkdir(d)
		except OSError:
			pass

# THIS FUNCTION FORMATS THE CURRENT DATE TIME INTO
# A STRING APPROPRIATE FOR A FILE NAME
def format_datetime():
	dt = str(datetime.now())

	# REMOVE COLONS AND PERIODS
	dt = re.sub(r'(:|\.)', '-', dt)
	
	# REMOVE WHITESPACE
	dt = re.sub(r'\s', '_', dt)
	
	return dt

# THIS FUNCTION CHECKS THE JETFREQ MODE AND CREATES
# AN APPROPRIATE SUB DIRECTORY PREFIX FOR THE FILENAME
def build_sub_dir(params):
	if params['mode'] == 'BY_EVENT':
		return 'event'
	elif params['mode'] == 'COMPARE_PROCESS':
		return 'process/diff'
	elif params['mode'] == 'COMPARE_EVENT':
		return 'event/diff'
	return 'process'

# THIS FUNCTION AUTOMATICALLY GENERATES A FILEPATH IN 
# WHICH TO SAVE THE CONTENTS OF A JETFREQ QUERY 
def build_file_path(params):
	
	debug(params['verbose'], 'Creating the file path')

	# GENERATE THE BASE NAME OF THE FILE
	file_path = './samples/{}/{}_s-{}_e-{}_n-{}'.format(
		build_sub_dir(params), 
		format_datetime(), 
		params['search_name'].replace('\\', '__BS__'), 
		get_event_type_flags(params), 
		params['sample_size']
	)
	if params['threshold_lt'] == None:
		file_path += "_t-None"
	else:
		file_path += "_t-{}".format(params['threshold_lt'])
	if params['threshold_gt'] == None:
		file_path += "_T-None"
	else:
		file_path += "_T-{}".format(params['threshold_gt'])

	# APPEND THE USER NAME FILTERS, IF THEY EXIST
	if params['user_name'] != None:
		file_path += '_u-{}'.format(params['user_name'].lower())
	elif params['exclude_user'] != None:
		file_path += '_U-{}'.format(params['exclude_user'].lower())
	
	# APPEND THE HOST NAME FILTERS, IF THEY EXIST
	if params['host_name'] != None:
		file_path += '_h-{}'.format(params['host_name'].lower())
	elif params['exclude_host'] != None:
		file_path += '_H-{}'.format(params['exclude_host'].lower())
	
	# APPEND THE FILE NAME FOR THE REPRESENTATIVE SAMPLE IF WRITING A 'COMPARE' MODE REPORT
	if not re.match(r'^COMPARE_', params['mode']) == None:
		dt = params['import_sample']
		if '/' in params['import_sample']:
			fn_ary = params['import_sample'].split('/')
			dt = fn_ary[len(fn_ary) - 1]
		dt = re.split(r'_s-', dt)[0]
		file_path += '_i-{}'.format(dt)
	
	# CLOSE FILE PATH WITH CSV EXTENSION
	file_path += '.csv'
	
	# ALTHOUGH HIGHLY UNLIKELY BECAUSE OF THE TIME STAMP, IF THE FILE
	# ALREADY EXISTS, APPEND A NUMERAL ON THE END OF THE FILENAME
	sn = 0
	while os.path.isfile(file_path):
		sn = sn + 1
		file_path = file_path[0:file_path.index('.csv')]
		file_path += '_' + sn + '.csv'

	debug(params['verbose'], 'File path is {}'.format(file_path))

	return file_path

# THIS IS THE MAIN FUNCTION FOR WRITING THE RESULTS OF A --COMPARE-PROCESS
# QUERY TO FILE
def out_file_compare_process(params, event_diffs):
	# CHECK THAT THERE ARE INDEED RESULTS
	no_results = True
	for key in event_diffs:
		if len(event_diffs[key]) > 0:
			no_results = False
	# IF NOT, GO NO FURTHER
	if no_results:
		raise jfexceptions.NoDiffsFoundError(params['search_name'], params['import_sample'])
	
	# CHECK THAT THE APPROPRIATE DIRECTORIES EXIST
	# GENERATE THE FILE PATH AND RETRIEVE THE REPRESENTATIVE SAMPLE PARAMETERS
	check_for_sample_dir()
	file_path = build_file_path(params)
	rep_params = get_params_from_file_name(params['import_sample'])
	difftype = DiffType()	

	debug(params['verbose'], 'Writing to file {}'.format(file_path))
	
	# WRITE THE EVENT DIFFERENCES TO FILE
	file = open(file_path, 'w')
	file.write('\'event_type\',\'diff_type\',\'tar_process\',\'tar_event\',\'tar_freq\',\'tar_count\',\'tar_total\',\'rep_process\',\'rep_event\',\'rep_freq\',\'rep_count\',\'rep_total\'\n')
	for key in event_diffs:
		if len(event_diffs[key]) > 0:
			event_diffs_for_type = sort_event_diffs_by_type(event_diffs[key])
			for event_diff in event_diffs_for_type:
				if event_diff.difftype == difftype.MISS_FM_REP or not re.match(r'^REPRESENTATIVE SAMPLE HAS NO', event_diff.difftype) == None:
					file.write('\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'NA\',\'NA\',\'NA\',\'NA\'\n'.format(
						key,
						event_diff.difftype, 
						params['search_name'],
						event_diff.target_event.path,
						event_diff.target_event.perc,
						event_diff.target_event.count,
						event_diff.target_event.total,
						rep_params['search_name']
						)
					)
				elif event_diff.difftype == difftype.MISS_FM_TAR or not re.match(r'^TARGET SAMPLE HAS NO', event_diff.difftype) == None:
					file.write('\'{}\',\'{}\',\'{}\',\'NA\',\'NA\',\'NA\',\'NA\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(
						key,
						event_diff.difftype,
						params['search_name'],
						rep_params['search_name'],
						event_diff.representative_event.path,
						event_diff.representative_event.perc,
						event_diff.representative_event.count,
						event_diff.representative_event.total
						)
					)
				else:
					file.write('\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(
						key,
						event_diff.difftype,
						params['search_name'],
						event_diff.target_event.path,
						event_diff.target_event.perc,
						event_diff.target_event.count,
						event_diff.target_event.total,
						rep_params['search_name'],
						event_diff.representative_event.path,
						event_diff.representative_event.perc,
						event_diff.representative_event.count,
						event_diff.representative_event.total
						)
					)
	file.close()
	return file_path

# THIS IS THE MAIN FUNCTION FOR WRITING THE RESULTS OF 
# A --COMPARE-EVENT QUERY TO FILE
def out_file_compare_event(params, event_diffs):
	# IF THERE ARE NO RESULTS, GO NO FURTHER
	if len(event_diffs) == 0:
		raise NoDiffsFoundError(params['search_name'], params['import_sample'])
	
	# CHECK THAT THE APPROPRIATE DIRECTORY EXISTS, GENERATE
	# THE FILE NAME AND RETRIEVE THE PARAMETERS USED IN THE
	# REPRESENTATIVE SAMPLE
	check_for_sample_dir()
	file_path = build_file_path(params)
	rep_params = get_params_from_file_name(params['import_sample'])
	difftype = DiffType()
	event_diffs = sort_event_diffs_by_type(event_diffs)
	
	# RETRIEVE THE EVENT TYPE USED IN THE QUERY
	target_event_type = 'modload'
	if params['regmods'] == True:
		target_event_type = 'regmod'
	elif params['filemods'] == True:
		target_event_type = 'filemod'
	elif params['childprocs'] == True:
		target_event_type = 'childproc'
	elif params['netconns'] == True:
		target_event_type = 'netconn'
	
	debug(params['verbose'], 'Writing to file {}'.format(file_path))
	
	# WRITE TO FILE
	file = open(file_path, 'w')
	file.write('\'diff_type\',\'tar_event\',\'tar_process\',\'tar_freq\',\'tar_count\',\'tar_total\',\'rep_event\',\'rep_process\',\'rep_freq\',\'rep_count\',\'rep_total\'\n'.format())	
	for event_diff in event_diffs:
		if event_diff.difftype == difftype.MISS_FM_REP:
			file.write('\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'NA\',\'NA\',\'NA\',\'NA\'\n'.format(
				event_diff.difftype, 
				target_event_type,
				event_diff.target_event.path,
				event_diff.target_event.perc,
				event_diff.target_event.count,
				event_diff.target_event.total,
				rep_params['event_type'].lower()
				)
			)
		elif event_diff.difftype == difftype.MISS_FM_TAR:
			file.write('\'{}\',\'{}\',\'NA\',\'NA\',\'NA\',\'NA\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(
				event_diff.difftype,
				target_event_type,
				rep_params['event_type'].lower(),
				event_diff.representative_event.path,
				event_diff.representative_event.perc,
				event_diff.representative_event.count,
				event_diff.representative_event.total
				)
			)
		else: #difftype.HIGH_FQ_*
			file.write('\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(
				event_diff.difftype,
				target_event_type,
				event_diff.target_event.path,
				event_diff.target_event.perc,
				event_diff.target_event.count,
				event_diff.target_event.total,
				rep_params['event_type'].lower(),
				event_diff.representative_event.path,
				event_diff.representative_event.perc,
				event_diff.representative_event.count,
				event_diff.representative_event.total
				)
			)
	file.close()
	return file_path

# THIS IS THE MAIN FUNCTION FOR WRITING THE RESULTS OF A
# --BY-EVENT QUERY TO FILE
def out_file_by_event(params, event_freqs):
	# IF THERE ARE NO RESULTS, GO NO FURTHER
	if len(event_freqs) == 0:
		raise jfexceptions.NoEventsFoundError(params['search_name'])
	
	# CHECK THAT THE APPROPRIATE DIRECTORY EXISTS AND 
	# GENERATE THE FILE PATH
	check_for_sample_dir()
	file_path = build_file_path(params)
	
	# GET THE EVENT TYPE USED IN THE QUERY
	event_type = 'modload'
	if params['filemods'] == True:
		event_type = 'filemod'
	elif params['regmods'] == True:
		event_type = 'regmod'
	elif params['childprocs'] == True:
		event_type = 'childproc'
	elif params['netconns'] == True:
		event_type = 'netconn'

	debug(params['verbose'], 'Writing to file {}'.format(file_path))

	# WRITE TO FILE
	file = open(file_path, 'w')
	file.write('\'{}\',\'path\',\'count\',\'total\',\'frequency\'\n'.format(event_type))
	for event in event_freqs:
		file.write('\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	file.close()
	return file_path
	
# THIS IS THE MAIN FUNCTION FOR WRITING THE RESULTS
# OF A --BY-PROCESS QUERY TO FILE
def out_file_by_process(params, event_freqs):
	# CHECK THAT THERE ARE INDEED RESULTS
	no_results = True
	for key in event_freqs:
		if not event_freqs[key] == None:
			no_results = False
	# IF NOT, THOU SHALT NOT PASSETH
	if no_results:
		raise jfexceptions.NoEventsFoundError(params['search_name'])
	
	# CHECK THAT THE APPROPRIATE DIRECTORY EXISTS
	# AND GENERATE THE FILE PATH
	check_for_sample_dir()
	file_path = build_file_path(params)

	debug(params['verbose'], 'Writing to file {}'.format(file_path))

	# WRITE TO FILE
	file = open(file_path, 'w')
	file.write('\'process\',\'event_type\',\'path\',\'count\',\'total\',\'freq\'\n')
	if not event_freqs['modloads'] == None:
		events = sort_events(event_freqs['modloads'])
		for event in events:
			file.write('\'{}\',\'modload\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	if not event_freqs['regmods'] == None:
		events = sort_events(event_freqs['regmods'])
		for event in events:
			file.write('\'{}\',\'regmod\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	if not event_freqs['childprocs'] == None:
		events = sort_events(event_freqs['childprocs'])
		for event in events:
			file.write('\'{}\',\'childproc\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	if not event_freqs['filemods'] == None:
		events = sort_events(event_freqs['filemods'])
		for event in events:
			file.write('\'{}\',\'filemod\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	if not event_freqs['netconns'] == None:
		events = sort_events(event_freqs['netconns'])
		for event in events:
			file.write('\'{}\',\'netconn\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	if not event_freqs['crossprocs'] == None:
		events = sort_events(event_freqs['crossprocs'])
		for event in events:
			file.write('\'{}\',\'crossproc\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	file.close()
	return file_path

# THIS FUNCTION READS THE README.TXT FILE
# OUT OUTPUTS THE USAGE SECTION TO STDOUT
def show_usage():
	h = open("README.txt", "r")
	usage = ""
	capture = False
	for line in h:
		if capture == False and len(usage) > 0:
			break
		elif capture == True:
			usage += line
			if re.match(r'^Show Help :', line) != None: 
				capture = False
		elif re.match(r'^Usage:', line) != None:
			capture = True
	print("\nUSAGE:\n{}".format(usage))

# THIS FUNCTION WRITES THE CONTENTS OF THE README.TXT
# FILE TO STDOUT
def show_help():
	h = open("README.txt", "r")
	print(h.read())

# THIS FUNCTION IMPORTS THE CONTENTS OF THE CONF FILE
# AND ADDS THEM TO THE PARAMS DICTIONARY
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

# THIS FUNCTION CHECKS FOR USER SPECIFIC REG KEY ADDRESSES
# OR USER SPECIFIC FILE DIRECTORIES AND REPLACES THE UNIQUE
# STRINGS WITH A GENERIC STRING, E.G. 'BROOKES' TO '<USER>'.
# THIS ENSURES THAT THE SAME FILE OR REG KEY IN DIFFERENT USERS
# PROFILES OR MACHINES ARE CONSIDERED THE SAME FILE OR REG KEY
# BY JETFREQ.
def homogenize_path(path, path_type):
	if path_type == "reg":
		# \registry\...\usersettings\<sid>\\
		# \registry\user\<sid>\
		if path.lower().startswith('\\registry\\') and '\\usersettings\\' in path:
			try:
				path_ary = path.split('\\')
				sid = False
				for i in range(len(path_ary)):
					if sid == True:
						path_ary[i] = "<SID>"
						sid = False
						break
					elif path_ary[i] == "usersettings":
						sid = True
				return '\\'.join(path_ary)
			except:
				debug(True, 'Error homogenizing regmod path {}'.format(path))
				return path
		elif path.lower().startswith('\\registry\\user\\'):
			try:
				path_ary = path.split('\\')
				path_ary[3] = '<SID>'
				return '\\'.join(path_ary)
			except:
				debug(True, 'Error homogenizing regmod path {}'.format(path))
		else:
			return path
	elif path_type == "dir":
		# c:\users\<user>\
		if path.lower().startswith('c:\\users\\'):
			try:
				path_ary = path.split('\\')
				path_ary[2] = '<USER>'
				return '\\'.join(path_ary)
			except:
				debug(True, 'Error homogenizing path {}'.format(path))
				return path
		else:
			return path
	else:
		return path

# THIS FUNCTION EXTRACTS THE PATH OF AN EVENT FROM THE 
# DATA RETURNED BY THE CARBON BLACK REST API. AS EACH 
# EVENT TYPE HAS A UNIQUE FORMAT, THE COLUMN MUST
# BE DEFINED.
def get_event_paths(events, col, path_type):
	paths = []
	for event in events:
		paths.append(homogenize_path(event.split('|')[col], path_type))
	return paths
