import jfutil
import jfexceptions
import re
import json

class EventFreq():
	def __init__(self, path, perc):
		self.path = path
		self.perc = perc
		
def sort_events(events):
	for i in len(events):
		j = i
		while j < len(events):
			if events[i].perc > events[j].perc:
				hold = events[i]
				events[i] = events[j]
				events[j] = hold
			j = j + 1
	return events

def calculate_event_frequency(event_counts, total_processes, threshold):
	events = []
	for key in event_counts:
		perc = round((event_counts[key]/float(total_processes))*100, 4)
		if perc <= float(threshold):
			events.append(EventFreq(key, perc))
	events = sort_events(events)
	return events

def count_events(process, container, key):
	for event in process[key]:
		if event in container:
			container[event] = container[event] + 1
		else:
			container[event] = 1
	return container

def analyze_by_process(params, data):
	jfutil.debug(params['verbose'], "Conducting analysis for {}".format(params['search_name']))

	# do count
	event_counts = {
		'modloads':{},
		'regmods':{},
		'childprocs':{},
		'filemods':{},
		'netconns':{},
		'crossprocs':{}
	}
	for process in data:
		if 'modloads' in process:
			jfutil.debug(params['verbose'], 'Counting modloads')
			event_counts['modloads'] = count_events(process, event_counts['modloads'], 'modloads')
		if 'regmods' in process:
			jfutil.debug(params['verbose'], 'Counting regmods')
			event_counts['regmods'] = count_events(process, event_counts['regmods'], 'regmods')
		if 'childprocs' in process:
			jfutil.debug(params['verbose'], 'Counting childprocs')
			event_counts['childprocs'] = count_events(process, event_counts['childprocs'], 'childprocs')
		if 'filemods' in process:
			jfutil.debug(params['verbose'], 'Counting filemods')
			event_counts['filemods'] = count_events(process, event_counts['filemods'], 'filemods')
		if 'netconns' in process:
			jfutil.debug(params['verbose'], 'Counting netconns')
			event_counts['netconns'] = count_events(process, event_counts['netconns'], 'netconns')
		if 'crossprocs' in process:
			jfutil.debug(params['verbose'], 'Counting crossprocs')
			event_counts['crossprocs'] = count_events(process, event_counts['crossprocs'], 'crossprocs')
	jfutil.debug(params['verbose'], 'Count complete')

	# calculate frequencies	and exclude processes that exceed threshold
	event_freqs = {
		'modloads':None,
		'regmods':None,
		'childprocs':None,
		'filemods':None,
		'netconns':None,
		'crossprocs':None
	}
	for key in event_counts:
		if len(event_counts['modloads']) > 0:
			jfutil.debug(params['verbose'], 'Calculating freq of modloads')
			event_freqs['modloads'] = calculate_event_frequency(event_counts['modloads'], len(data), params['threshold'])
		if len(event_counts['regmods']) > 0:
			jfutil.debug(params['verbose'], 'Calculating freq of regmods')
			event_freqs['regmods'] = calculate_event_frequency(event_counts['regmods'], len(data), params['threshold'])
		if len(event_counts['childprocs']) > 0:
			jfutil.debug(params['verbose'], 'Calculating freq of childprocs')
			event_freqs['childprocs'] = calculate_event_frequency(event_counts['childprocs'], len(data), params['threshold'])
		if len(event_counts['filemods']) > 0:
			jfutil.debug(params['verbose'], 'Calculating freq of filemods')
			event_freqs['filemods'] = calculate_event_frequency(event_counts['filemods'], len(data), params['threshold'])
		if len(event_counts['netconns']) > 0:
			jfutil.debug(params['verbose'], 'Calculating freq of netconns')
			event_freqs['netconns'] = calculate_event_frequency(event_counts['netconns'], len(data), params['threshold'])
		if len(event_counts['crossprocs']) > 0:
			jfutil.debug(params['verbose'], 'Calculating freq of crossprocs')
			event_freqs['crossprocs'] = calculate_event_frequency(event_counts['crossprocs'], len(data), params['threshold'])
	jfutil.debug(params['verbose'], "Freq calculations complete")
	
	return event_freqs

def analyze_by_modload(params, data):
	pass
