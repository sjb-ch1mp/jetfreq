# MODULE CONTAINS ALL FUNCTIONS THAT CONDUCT FREQUENCY ANALYSIS ON 
# THE RESULTS OF A CARBON BLACK QUERY

import jfutil
import jfexceptions
import re
import json

# CONTAINER CLASS FOR EVENT FREQUENCIES
class EventFreq():
	def __init__(self, path, perc, count, total):
		self.path = path # PATH OF EVENT
		self.perc = perc # PERCENTAGE OF PROCESSES IN WHICH EVENT OCCURS
		self.count = count # THE NUMBER OF PROCESSES IN WHICH EVENT OCCURS
		self.total = total # THE TOTAL NUMBER OF PROCESSES THAT CONTAIN AN EVENT OF THIS TYPE

# CONTAINER CLASS FOR EVENT DIFFERENCES
class EventDiff():
	def __init__(self, target_event, representative_event, difftype):
		self.target_event = target_event # AN EVENT FROM THE TARGET SAMPLE
		self.representative_event = representative_event # THE CORRESPONDING EVENT FROM THE REPRESENTATIVE SAMPLE
		self.difftype = difftype # THE TYPE OF DIFFERENCE BETWEEN THE EVENTS

# CONTAINER CLASS FOR DIFFERENCE TYPES
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
	
	# TAKES AN EVENT TYPE AND RETURNS THE CORRESPONDING DIFFERENCE TYPE
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
		
# ORDER A LIST OF EVENTS ALPHABETICALLY
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

# ORDER A LIST OF EVENTS BY THEIR FREQUENCY
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

# CALCULATE THE FREQUENCY OF A GIVEN EVENT
def calculate_event_frequency(event_counts, total_processes, greater_than, less_than):
	events = []
	for key in event_counts:
		perc = round((event_counts[key]/float(total_processes)), 5)
		if greater_than == None:
			if perc * 100 <= float(less_than):
				events.append(EventFreq(key, perc, event_counts[key], total_processes))
		elif less_than == None:
			if perc * 100 >= float(greater_than):
				events.append(EventFreq(key, perc, event_counts[key], total_processes))
		elif float(greater_than) > float(less_than): # both are not None
			if perc * 100 <= float(less_than) or perc * 100 >= float(greater_than):
				events.append(EventFreq(key, perc, event_counts[key], total_processes))
		else:
			if perc * 100 <= float(less_than) and perc * 100 >= float(greater_than):
				events.append(EventFreq(key, perc, event_counts[key], total_processes))
	events = sort_events(events)
	return events

# COUNT HOW MANY TIMES AN EVENT OCCURS IN A GIVEN PROCESS
def count_events(process, container, key):
	for event in process[key]:
		if event in container:
			container[event] = container[event] + 1
		else:
			container[event] = 1
	return container

# THE MAIN FUNCTION FOR THE --BY-PROCESS AND --COMPARE-PROCESS MODES
# THIS FUNCTION TAKES THE DATA RETURNED FROM CARBON BLACK AND CALCULATES
# THE FREQUENCY IN WHICH THE SPECIFIED EVENT TYPES OCCUR ACROSS PROCESSES
# IN THE SAMPLE
def analyze_by_process(params, data):
	jfutil.debug(params['verbose'], "Conducting analysis for {}".format(params['search_name']))

	# INITIALIZE THE JSON CONTAINER FOR THE RESULTS OF THE EVENT COUNT
	event_counts = {
		'modloads':{},
		'regmods':{},
		'childprocs':{},
		'filemods':{},
		'netconns':{},
		'crossprocs':{}
	}

	# COUNT HOW MANY TIMES EACH SPECIFIC EVENT OCCURS ACROSS ALL 
	# PROCESSES IN THE SAMPLE RETURNED FROM CARBON BLACK
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

	# INITIALIZE THE JSON CONTAINER FOR THE RESULTS OF THE EVENT FREQUENCY ANALYSIS
	event_freqs = {
		'modloads':None,
		'regmods':None,
		'childprocs':None,
		'filemods':None,
		'netconns':None,
		'crossprocs':None
	}

	# USING THE COUNTS, CALCULATE THE FREQUENCY IN WHICH EACH EVENT OCCURS ACROSS
	# PROCESSES IN THE SAMPLE RETURNED BY CARBON BLACK
	if len(event_counts['modloads']) > 0:
		jfutil.debug(params['verbose'], 'Calculating freq of modloads')
		event_freqs['modloads'] = calculate_event_frequency(event_counts['modloads'], len(data), params['threshold_gt'], params['threshold_lt'])
	if len(event_counts['regmods']) > 0:
		jfutil.debug(params['verbose'], 'Calculating freq of regmods')
		event_freqs['regmods'] = calculate_event_frequency(event_counts['regmods'], len(data), params['threshold_gt'], params['threshold_lt'])
	if len(event_counts['childprocs']) > 0:
		jfutil.debug(params['verbose'], 'Calculating freq of childprocs')
		event_freqs['childprocs'] = calculate_event_frequency(event_counts['childprocs'], len(data), params['threshold_gt'], params['threshold_lt'])
	if len(event_counts['filemods']) > 0:
		jfutil.debug(params['verbose'], 'Calculating freq of filemods')
		event_freqs['filemods'] = calculate_event_frequency(event_counts['filemods'], len(data), params['threshold_gt'], params['threshold_lt'])
	if len(event_counts['netconns']) > 0:
		jfutil.debug(params['verbose'], 'Calculating freq of netconns')
		event_freqs['netconns'] = calculate_event_frequency(event_counts['netconns'], len(data), params['threshold_gt'], params['threshold_lt'])
	if len(event_counts['crossprocs']) > 0:
		jfutil.debug(params['verbose'], 'Calculating freq of crossprocs')
		event_freqs['crossprocs'] = calculate_event_frequency(event_counts['crossprocs'], len(data), params['threshold_gt'], params['threshold_lt'])
	jfutil.debug(params['verbose'], "Freq calculations complete")
	
	return event_freqs

# THIS IS THE MAIN FUNCTION FOR --COMPARE-EVENT AND --BY-EVENT MODES
# THIS FUNCTION CALCULATES THE FREQUENCY IN WHICH EACH PROCESS IN A SAMPLE
# CREATES A GIVEN EVENT
def analyze_by_event(params, data):
	jfutil.debug(params['verbose'], "Conducting analysis for {}".format(params['search_name']))
	
	# COUNT HOW MANY PROCESSES CREATE A GIVEN EVENT IN THE SAMPLE
	event_counts = {}
	for process in data:
		if not process['path'] in event_counts:
			event_counts[process['path']] = 1
		else:
			event_counts[process['path']] = event_counts[process['path']] + 1
	jfutil.debug(params['verbose'], "Count complete")
	
	# CALCULATE THE FREQUENCY IN WHICH PROCESSES CREATE THE EVENT
	event_freqs = calculate_event_frequency(event_counts, len(data), params['threshold_gt'], params['threshold_lt'])
	jfutil.debug(params['verbose'], "Freq calculations complete")
	
	return event_freqs

# THIS IS A UTILITY FUNCTION THAT LOADS A LIST INTO A 
# DICTIONARY IN ORDER TO MAKE THE COMPARISON PROCESS 
# MORE EFFICIENT
def load_into_dict(events):
	event_dict = {}
	for event in events:
		event_dict[event.path] = {'freq':event.perc,'object':event}
	return event_dict

# THIS IS THE MAIN FUNCTION FOR THE --COMPARE-PROCESS MODE
# THIS FUNCTION COMPARES TWO SAMPLES, AND COLLATES THE DIFFERENCES
# BETWEEN THE SAMPLES INTO DEFINED DIFFERENCE CATEGORIES
def compare_process(params, representative_sample, target_sample):
	jfutil.debug(params['verbose'], 'Comparing target process {} to representative sample {}'.format(params['search_name'], params['import_sample']))	
	
	# INITIALIZE THE JSON CONTAINER FOR EVENT DIFFERENCES
	event_diffs = {'modloads':[],'regmods':[],'childprocs':[],'filemods':[],'netconns':[],'crossprocs':[]}
	difftype = DiffType()
	
	# FOR EACH EVENT TYPE
	for key in event_diffs:
		# IF THE EVENT TYPE EXISTS IN THE REP SAMPLE AND DOES NOT EXIST IN THE TAR SAMPLE
		if not representative_sample[key] == None and target_sample[key] == None:
			# FOR ALL EVENTS OF THIS TYPE IN THE REP SAMPLE, ADD AN APPROPRIATE 'MISSING FROM TAR' DIFF TYPE
			for event in representative_sample[key]:
				event_diffs[key].append(EventDiff(None, event, difftype.get_diff_type_by_event(key, 'rep')))
		# IF THE EVENT TYPE EXISTS IN THE TAR SAMPLE AND DOES NOT EXIST IN THE REP SAMPLE
		elif not target_sample[key] == None and representative_sample[key] == None:
			# FOR ALL EVENTS OF THIS TYPE IN THE TAR SAMPLE, ADD AN APPROPRIATE 'MISSING FROM REP' DIFF TYPE
			for event in target_sample[key]:
				event_diffs[key].append(EventDiff(None, event, difftype.get_diff_type_by_event(key, 'tar')))
		# IF THE EVENT TYPE EXISTS IN BOTH THE REP AND TAR SAMPLES
		elif not target_sample[key] == None and not representative_sample[key] == None:
			# LOAD THE EVENT LIST INTO A DICTIONARY
			rep_dict = load_into_dict(representative_sample[key])
			tar_dict = load_into_dict(target_sample[key])
			# FOR EACH EVENT OF THIS TYPE IN THE TAR SAMPLE
			for sub_key in tar_dict:
				# IF THE EVENT DOES NOT EXIST IN THE REP SAMPLE, ADD A 'MISSING FROM REP' DIFF TYPE
				if not sub_key in rep_dict:
					event_diffs[key].append(EventDiff(tar_dict[sub_key]['object'], None, difftype.MISS_FM_REP))
				else:
					# IF THE EVENT EXISTS IN BOTH SAMPLES, CALCULATE WHETHER IT OCCURS MORE IN THE REP OR TAR SAMPLES
					if float(tar_dict[sub_key]['freq']) > float(rep_dict[sub_key]['freq']):
						event_diffs[key].append(EventDiff(tar_dict[sub_key]['object'], rep_dict[sub_key]['object'], difftype.HIGH_FQ_TAR))
					elif float(tar_dict[sub_key]['freq']) < float(rep_dict[sub_key]['freq']):
						event_diffs[key].append(EventDiff(tar_dict[sub_key]['object'], rep_dict[sub_key]['object'], difftype.HIGH_FQ_REP))
			# FOR EACH EVENT OF THIS TYPE IN THE REP SAMPLE
			for sub_key in rep_dict:
				# IF THE EVENT DOES NOT EXIST IN THE TAR SAMPLE, ADD A 'MISSING FROM TAR' DIFF TYPE
				if not sub_key in tar_dict:
					event_diffs[key].append(EventDiff(None, rep_dict[sub_key]['object'], difftype.MISS_FM_TAR))
	jfutil.debug(params['verbose'], 'Comparison complete')
	return event_diffs	

# THIS IS THE MAIN FUNCTION FOR THE --COMPARE-EVENT MODE
# THIS FUNCTION COMPARES TWO SAMPLES, AND COLLATES THE DIFFERENCES
# BETWEEN THE SAMPLES INTO DEFINED DIFFERENCE CATEGORIES
def compare_event(params, representative_sample, target_sample):

	jfutil.debug(params['verbose'], 'Comparing target event {} to representative sample {}'.format(params['search_name'], params['import_sample']))
	
	# INITIALIZE THE JSON CONTAINER FOR PROCESS DIFFERENCES
	event_diffs = []
	difftype = DiffType()
	rep_dict = load_into_dict(representative_sample)
	tar_dict = load_into_dict(target_sample)
	
	# FOR EACH PROCESS IN THE TAR SAMPLE
	for key in tar_dict:
		# IF THE PROCESS DOES NOT EXIST IN THE REP SAMPLE, ADD A 'MISSING FROM REP' DIFF TYPE
		if not key in rep_dict:
			event_diffs.append(EventDiff(tar_dict[key]['object'], None, difftype.MISS_FM_REP))
		else:
			# IF THE EVENT EXISTS IN BOTH SAMPLES, CALCULATE WHETHER IT OCCURS MORE IN THE REP OR TAR SAMPLES
			if float(tar_dict[key]['freq']) > float(rep_dict[key]['freq']): 
				event_diffs.append(EventDiff(tar_dict[key]['object'], rep_dict[key]['object'], difftype.HIGH_FQ_TAR))
			elif float(tar_dict[key]['freq']) < float(rep_dict[key]['freq']):
				event_diffs.append(EventDiff(tar_dict[key]['object'], rep_dict[key]['object'], difftype.HIGH_FQ_REP))
	
	# FOR EACH PROCESS IN THE REP SAMPLE
	for key in rep_dict:
		# IF THE PROCESS DOES NOT EXIST IN THE TAR SAMPLE, ADD A 'MISSING FROM TAR' DIFF TYPE
		if not key in tar_dict:
			event_diffs.append(EventDiff(None, rep_dict[key]['object'], difftype.MISS_FM_TAR))
	jfutil.debug(params['verbose'], 'Comparison complete')	
	return event_diffs
