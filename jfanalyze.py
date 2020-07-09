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

def analyze(params, data):

	total_processes = len(data)
	
	jfutil.debug(params['verbose'], "Conducting analysis for {}".format(params['search_name']))

	# do count
	modloads = {}
	for process in data:
		if 'modloads' in process:
			for modload in process['modloads']:
				if modload in modloads:
					modloads[modload] = modloads[modload] + 1
				else:
					modloads[modload] = 1
	jfutil.debug(params['verbose'], 'Count complete')

	# calculate frequencies	and exclude processes that exceed threshold
	events = []
	for key in modloads:
		perc = round((modloads[key]/float(total_processes))*100, 4)
		if perc <= float(params['threshold']):
			events.append(EventFreq(key, perc))
	jfutil.debug(params['verbose'], "Percentage calculations complete")
	
	events = sort_events(events)
	
	return events
