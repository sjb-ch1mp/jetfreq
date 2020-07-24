import re
import jfexceptions
import os
from jfanalyze import sort_events
from jfanalyze import EventFreq
from jfanalyze import EventDiff
from jfanalyze import DiffType
from datetime import datetime

def debug(verbose, message):
	if verbose:
		if type(message) == list:
			for line in message:
				print("jetfreq.py: {}".format(line))
		else:
			print("jetfreq.py: {}".format(message))

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

def append_to_report(report, event_freqs, event_type):
	report.append('::::::')
	report.append(':::::: {}'.format(event_type))
	for event in event_freqs:
		report.append(':::::: {}/{} | {:8.4f} | {}'.format(event.count, event.total, event.perc, event.path))
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
		report.append('::::::')
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
	report.append('::::::')
	report.append(':::::: END')
	return report

def format_report_by_event(params, event_freqs):
	
	debug(params['verbose'], 'Generating report')	
	report = []
	
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

	# check for no results
	# event_freq = [{path:<process_path>,perc:<perc>,count:<count>,total:<total>}]
	if len(event_freqs) == 0:
		report.append('::::::')
		report.append(':::::: NO RESULTS FOR {} {}'.format(event_type, params['search_name'].upper()))
		return report
	
	report.append('::::::')
	report.append(':::::: RESULTS FOR {} {}'.format(event_type, params['search_name'].upper()))
	report.append('::::::')
	report.append(':::::: FILTERS')
	report.append(':::::: start_time = {}'.format(params['start_time']))
	report.append(':::::: threshold = {}%'.format(params['threshold']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	report = append_to_report(report, event_freqs, 'PROCESSES')
	report.append('::::::')
	report.append(':::::: END')
	return report

def get_params_from_file_name(file_name):
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
		'host_name':None,
		'threshold':100,
		'event_type':None
		}

	name_ary = re.split(r'_[hutnse]{1}-', file_name[0:len(file_name) - 4]) # trim .csv
	params['search_name'] = name_ary[1]
	params['sample_size'] = int(name_ary[3])
	params['threshold'] = int(name_ary[4])
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
	if len(name_ary) == 7: # both username and hostname
		params['user_name'] = name_ary[5]
		params['host_name'] = name_ary[6]
	elif len(name_ary) == 6: # either username or hostname
		if re.match(r'_h-', file_name) == None:
			params['user_name'] = name_ary[5]
		else:
			params['host_name'] = name_ary[5]
	return params

def format_report_compare_process(params, event_freqs):
	report = []
	
	# check no results
	no_results = True
	for key in event_freqs:
		if not event_freqs[key] == None and len(event_freqs[key]) > 0:
			no_results = False
			break
	if no_results:
		report.append('::::::')
		report.append(':::::: TARGET AND REPRESENTATIVE SAMPLES ARE THE SAME')
		return report
	
	# if there are results, add them to the report
	representative_sample_params = get_params_from_file_name(params['import_sample'])
	report.append('::::::')
	report.append(':::::: PROCESS COMPARISON RESULTS')
	report.append('::::::')
	report.append(':::::: REPRESENTATIVE SAMPLE PROCESS {}'.format(representative_sample_params['search_name'].upper()))
	report.append(':::::: file = {}'.format(params['import_sample']))
	report.append(':::::: threshold = {}%'.format(representative_sample_params['threshold']))
	report.append(':::::: sample_size = {}'.format(representative_sample_params['sample_size']))
	if not representative_sample_params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(representative_sample_params['user_name']))
	if not representative_sample_params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(representative_sample_params['host_name']))
	report.append('::::::')
	report.append(':::::: TARGET SAMPLE PROCESS {}'.format(params['search_name'].upper()))
	report.append(':::::: start_time = {}'.format(params['start_time']))
	report.append(':::::: threshold = {}%'.format(params['threshold']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	for key in event_freqs:
		if not event_freqs[key] == None and len(event_freqs[key]) > 0:
			report = append_diff_to_report(report, event_freqs[key], key.upper())
	report.append('::::::')
	report.append(':::::: END')
	return report

def format_report_compare_event(params, event_freqs):
	report = []
	
	# check no results
	if len(event_freqs) == 0:
		report.append('::::::')
		report.append(':::::: TARGET AND REPRESENTATIVE SAMPLES ARE THE SAME')
		return report
	
	# get target event type
	event_type = 'NETCONN'
	if params['modloads'] == True:
		event_type = 'MODLOAD'
	elif params['regmods'] == True:
		event_type = 'REGMOD'
	elif params['filemods'] == True:
		event_type = 'FILEMOD'
	elif params['childprocs'] == True:
		event_type = 'CHILDPROC'
	
	representative_sample_params = get_params_from_file_name(params['import_sample'])
	report.append('::::::')
	report.append(':::::: EVENT COMPARISON RESULTS')
	report.append('::::::')
	report.append(':::::: REPRESENTATIVE SAMPLE {} {}'.format(representative_sample_params['event_type'], representative_sample_params['search_name'].upper()))
	report.append(':::::: file = {}'.format(params['import_sample']))
	report.append(':::::: threshold = {}'.format(representative_sample_params['threshold']))
	report.append(':::::: sample_size = {}'.format(representative_sample_params['sample_size']))
	if not representative_sample_params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(representative_sample_params['user_name']))
	if not representative_sample_params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(representative_sample_params['host_name']))
	report.append('::::::')
	report.append(':::::: TARGET SAMPLE {} {}'.format(event_type, params['search_name']))
	report.append(':::::: start_time = {}'.format(params['start_time']))
	report.append(':::::: threshold = {}'.format(params['threshold']))
	report.append(':::::: sample_size = {}'.format(params['sample_size']))
	if not params['user_name'] == None:
		report.append(':::::: user_name = {}'.format(params['user_name']))
	if not params['host_name'] == None:
		report.append(':::::: host_name = {}'.format(params['host_name']))
	report = append_diff_to_report(report, event_freqs, 'PROCESSES')
	report.append('::::::')
	report.append(':::::: END')
	return report

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

def import_sample(params):
	search_name = None
	event_type = None
	path = None
	count = None
	total = None
	freq = None
	
	file_path = ''
	# check for folder and prepend if not already included
	if re.match(r'^\./samples/', params['import_sample']) == None:
		file_path = './samples/{}/{}'.format('process' if params['mode'] == 'COMPARE_PROCESS' else 'event', params['import_sample'])
	elif not re.match(r'/', params['import_sample']) == None:
		file_path_ary = params['import_sample'].split('/')
		file_path = './samples/{}/{}'.format('process' if params['mode'] == 'COMPARE_PROCESS' else 'event', file_path_ary[len(file_path_ary) - 1])
	else:
		file_path = params['import_sample']
	
	# get the column indices for the compare mode
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
	
	# import
	event_freqs = [] if event_type == None else {'modloads':None, 'regmods':None, 'childprocs':None, 'filemods':None, 'netconns':None, 'crossprocs':None}
	file = open(file_path, 'r')
	skip = True
	for line in file:
		if skip:
			# skip the first line
			skip = False
		else:	
			# retrieve the values from the line
			path_value = line.split(',')[path].replace('\'','')
			freq_value = line.split(',')[freq].replace('\'','')
			freq_value = freq_value.replace('\n','')
			count_value = line.split(',')[count].replace('\'','')
			total_value = line.split(',')[total].replace('\'','')
			if not event_type == None:
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

def format_datetime():
	dt = str(datetime.now())

	# remove colons and periods
	dt = re.sub(r'(:|\.)', '-', dt)
	
	# remove whitespace
	dt = re.sub(r'\s', '_', dt)
	
	return dt

def build_sub_dir(params):
	if params['mode'] == 'BY_EVENT':
		return 'event'
	elif params['mode'] == 'COMPARE_PROCESS':
		return 'process/diff'
	elif params['mode'] == 'COMPARE_EVENT':
		return 'event/diff'
	return 'process'

def build_file_path(params):
	
	debug(params['verbose'], 'Creating the file path')

	# create base name
	file_path = './samples/{}/{}_s-{}_e-{}_n-{}_t-{}'.format(build_sub_dir(params), format_datetime(), params['search_name'], get_event_type_flags(params), params['sample_size'], params['threshold'])

	# add user name filter
	if not params['user_name'] == None:
		file_path += '_u-{}'.format(params['user_name']).lower()
	
	# add host name filter
	if not params['host_name'] == None:
		file_path += '_h-{}'.format(params['host_name']).lower()

	if not re.match(r'^COMPARE_', params['mode']) == None:
		dt = params['import_sample']
		if '/' in params['import_sample']:
			fn_ary = params['import_sample'].split('/')
			dt = fn_ary[len(fn_ary) - 1]
		dt = re.split(r'_s-', dt)[0]
		file_path += '_i-{}'.format(dt)
	
	# add file extension
	file_path += '.csv'
	
	# check that file already exists (highly unlikely)
	sn = 0
	while os.path.isfile(file_path):
		sn = sn + 1
		file_path = file_path[0:file_path.index('.csv')]
		file_path += '_' + sn + '.csv'

	debug(params['verbose'], 'File path is {}'.format(file_path))

	return file_path

def out_file_compare_process(params, event_diffs):
	# check for no results
	no_results = True
	for key in event_diffs:
		if len(event_diffs[key]) > 0:
			no_results = False
	if no_results:
		raise jfexceptions.NoDiffsFoundError(params['search_name'], params['import_sample'])

	check_for_sample_dir()
	file_path = build_file_path(params)
	rep_params = get_params_from_file_name(params['import_sample'])
	difftype = DiffType()	

	debug(params['verbose'], 'Writing to file {}'.format(file_path))

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
				else: # difftype.HIGH_FQ_*
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

def out_file_compare_event(params, event_diffs):
	# check for no results
	if len(event_diffs) == 0:
		raise NoDiffsFoundError(params['search_name'], params['import_sample'])

	check_for_sample_dir()
	file_path = build_file_path(params)
	rep_params = get_params_from_file_name(params['import_sample'])
	difftype = DiffType()
	event_diffs = sort_event_diffs_by_type(event_diffs)
	
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

def out_file_by_event(params, event_freqs):
	# check for no results
	if len(event_freqs) == 0:
		raise jfexceptions.NoEventsFoundError(params['search_name'])

	check_for_sample_dir()
	file_path = build_file_path(params)
	
	#get the event type for the column header
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
	file = open(file_path, 'w')
	file.write('\'{}\',\'path\',\'count\',\'total\',\'frequency\'\n'.format(event_type))
	for event in event_freqs:
		file.write('\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'\n'.format(params['search_name'], event.path, event.count, event.total, event.perc))
	file.close()
	return file_path
	

def out_file_by_process(params, event_freqs):
	check_for_sample_dir()
	file_path = build_file_path(params)
	
	no_results = True
	for key in event_freqs:
		if not event_freqs[key] == None:
			no_results = False
	if no_results:
		raise jfexceptions.NoEventsFoundError(params['search_name'])

	# write to file
	debug(params['verbose'], 'Writing to file {}'.format(file_path))
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

def homogenize_path(path):
	if re.match(r'^c:\\users\\', path.lower()) == None:
		return path
	else:
		try:
			path_ary = path.split('\\')
			path_ary[2] = '<USER>'
			return '\\'.join(path_ary)
		except:
			debug(True, 'Error homogenizing path {}'.format(path))
			return path

def get_event_paths(events, col):
	paths = []
	for event in events:
		paths.append(homogenize_path(event.split('|')[col]))
	return paths
