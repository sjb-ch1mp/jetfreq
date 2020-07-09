import jfutil
import jfexceptions
import re
import json

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
	results = {}
	for key in modloads:
		perc = (modloads[key]/total_processes)*100
		if perc <= params['threshold']:
			results[key] = perc
	jfutil.debug(params['verbose'], "Percentage calculations complete")

	return results
