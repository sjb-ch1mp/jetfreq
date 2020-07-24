import jfutil
import jfexceptions
import re
import json

class EventFreq():
	def __init__(self, path, perc, count, total):
		self.path = path
		self.perc = perc
		self.count = count
		self.total = total

class EventDiff():
	def __init__(self, target_event, representative_event, difftype):
		self.target_event = target_event
		self.representative_event = representative_event
		self.difftype = difftype
	
class DiffType(): 
	def __init__(self):
		self.MISS_FM_REP = 'MISSING FROM REPRESENTATIVE SAMPLE'
		self.MISS_FM_TAR = 'MISSING FROM TARGET SAMPLE'
		self.HIGH_FQ_REP = 'OCCURS MORE IN REPRESENTATIVE SAMPLE'
		self.HIGH_FQ_TAR = 'OCCURS MORE IN TARGET SAMPLE'
		self.REP_MISS_M = 'REPRESENTATIVE SAMPLE HAS NO MODLOADS, BUT TARGET SAMPLE DOES'
		self.REP_MISS_R = 'REPRESENTATIVE SAMPLE HAS NO REGMODS, BUT TARGET SAMPLE DOES'
		self.REP_MISS_F = 'REPRESENTATIVE SAMPLE HAS NO FILEMODS, BUT TARGET SAMPLE DOES'
		self.REP_MISS_C = 'REPRESENTATIVE SAMPLE HAS NO CHILDPROCS, BUT TARGET SAMPLE DOES'
		self.REP_MISS_D = 'REPRESENTATIVE SAMPLE HAS NO NETCONNS, BUT TARGET SAMPLE DOES'
		self.REP_MISS_X = 'REPRESENTATIVE SAMPLE HAS NO CROSSPROCS, BUT TARGET SAMPLE DOES'
		self.TAR_MISS_M = 'TARGET SAMPLE HAS NO MODLOADS, BUT REPRESENTATIVE SAMPLE DOES'
		self.TAR_MISS_R = 'TARGET SAMPLE HAS NO REGMODS, BUT REPRESENTATIVE SAMPLE DOES'
		self.TAR_MISS_F = 'TARGET SAMPLE HAS NO FILEMODS, BUT REPRESENTATIVE SAMPLE DOES'
		self.TAR_MISS_C = 'TARGET SAMPLE HAS NO CHILDPROCS, BUT REPRESENTATIVE SAMPLE DOES'
		self.TAR_MISS_D = 'TARGET SAMPLE HAS NO NETCONNS, BUT REPRESENTATIVE SAMPLE DOES'
		self.TAR_MISS_X = 'TARGET SAMPLE HAS NO CROSSPROCS, BUT REPRESENTATIVE SAMPLE DOES'
	
	def get_diff_type_by_event(event_type, sample):
		if sample == 'rep':
			if event_type == 'modloads':
				return self.REP_MISS_M
			elif event_type == 'regmods':
				return self.REP_MISS_R
			elif event_type == 'filemods':
				return self.REP_MISS_F
			elif event_type == 'childprocs':
				return self.REP_MISS_C
			elif event_type == 'netconns':
				return self.REP_MISS_D
			else:
				return self.REP_MISS_X
		else:
			if event_type == 'modloads':
				return self.TAR_MISS_M
			elif event_type == 'regmods':
				return self.TAR_MISS_R
			elif event_type == 'filemods':
				return self.TAR_MISS_F
			elif event_type == 'childprocs':
				return self.TAR_MISS_C
			elif event_type == 'netconns':
				return self.TAR_MISS_D
			else:	
				return self.TAR_MISS_X
		

def alphabetize_events(events):
	for i in range(len(events)):
		j = i
		while j < len(events):
			if events[i].path > events[j].path:
				hold = events[i]
				events[i] = events[j]
				events[j] = hold
			j = j + 1
	return events
	
def sort_events(events):
	for i in range(len(events)):
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
		perc = round((event_counts[key]/float(total_processes)), 5)
		if perc * 100 <= float(threshold):
			events.append(EventFreq(key, perc, event_counts[key], total_processes))
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

def analyze_by_event(params, data):
	# event = {process:"", id:"", segment_id:""}
	jfutil.debug(params['verbose'], "Conducting analysis for {}".format(params['search_name']))

	event_counts = {}
	for process in data:
		if not process['path'] in event_counts:
			event_counts[process['path']] = 1
		else:
			event_counts[process['path']] = event_counts[process['path']] + 1
	jfutil.debug(params['verbose'], "Count complete")

	event_freqs = calculate_event_frequency(event_counts, len(data), params['threshold'])
	jfutil.debug(params['verbose'], "Freq calculations complete")
	
	return event_freqs

def load_into_dict(events):
	event_dict = {}
	for event in events:
		event_dict[event.path] = {'freq':event.perc,'object':event}
	return event_dict

def compare_process(params, representative_sample, target_sample):
	
	jfutil.debug(params['verbose'], 'Comparing target process {} to representative sample {}'.format(params['search_name'], params['import_sample']))	
	event_diffs = {'modloads':[],'regmods':[],'childprocs':[],'filemods':[],'netconns':[],'crossprocs':[]}
	difftype = DiffType()
	
	for key in event_diffs:
		if not representative_sample[key] == None and target_sample[key] == None:
			for event in representative_sample[key]:
				event_diffs[key].append(EventDiff(None, event, difftype.get_diff_type_by_event(key, 'rep')))
		elif not target_sample[key] == None and representative_sample[key] == None:
			for event in target_sample[key]:
				event_diffs[key].append(EventDiff(None, event, difftype.get_diff_type_by_event(key, 'tar')))
		elif not target_sample[key] == None and not representative_sample[key] == None:
			rep_dict = load_into_dict(representative_sample[key])
			tar_dict = load_into_dict(target_sample[key])
			# check for target samples missing from rep sample
			for sub_key in tar_dict:
				if not sub_key in rep_dict:
					event_diffs[key].append(EventDiff(tar_dict[sub_key]['object'], None, difftype.MISS_FM_REP))
				else:
					if float(tar_dict[sub_key]['freq']) > float(rep_dict[sub_key]['freq']):
						event_diffs[key].append(EventDiff(tar_dict[sub_key]['object'], rep_dict[sub_key]['object'], difftype.HIGH_FQ_TAR))
					elif float(tar_dict[sub_key]['freq']) < float(rep_dict[sub_key]['freq']):
						event_diffs[key].append(EventDiff(tar_dict[sub_key]['object'], rep_dict[sub_key]['object'], difftype.HIGH_FQ_REP))
			# check for rep samples missing from tar sample
			for sub_key in rep_dict:
				if not sub_key in tar_dict:
					event_diffs[key].append(EventDiff(None, rep_dict[sub_key]['object'], difftype.MISS_FM_TAR))
	jfutil.debug(params['verbose'], 'Comparison complete')
	return event_diffs	


def compare_event(params, representative_sample, target_sample):

	jfutil.debug(params['verbose'], 'Comparing target event {} to representative sample {}'.format(params['search_name'], params['import_sample']))
	event_diffs = []
	difftype = DiffType()
	rep_dict = load_into_dict(representative_sample)
	tar_dict = load_into_dict(target_sample)
	
	# check for target samples missing from representative sample (new processes spawning an event)
	for key in tar_dict:
		if not key in rep_dict:
			event_diffs.append(EventDiff(tar_dict[key]['object'], None, difftype.MISS_FM_REP))
		else:
			if float(tar_dict[key]['freq']) > float(rep_dict[key]['freq']): # check if there is a higher frequency in the target sample
				event_diffs.append(EventDiff(tar_dict[key]['object'], rep_dict[key]['object'], difftype.HIGH_FQ_TAR))
			elif float(tar_dict[key]['freq']) < float(rep_dict[key]['freq']): # check if there is a higher frequency in the representative sample
				event_diffs.append(EventDiff(tar_dict[key]['object'], rep_dict[key]['object'], difftype.HIGH_FQ_REP))
	
	# check for representative samples missing from target sample (process no longer spawning an event)
	for key in rep_dict:
		if not key in tar_dict:
			event_diffs.append(EventDiff(None, rep_dict[key]['object'], difftype.MISS_FM_TAR))
	jfutil.debug(params['verbose'], 'Comparison complete')	
	return event_diffs
