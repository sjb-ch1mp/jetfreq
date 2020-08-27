# THIS MODULE CONTAINS ALL FUNCTIONS ASSOCIATED WITH COMMUNICATING 
# WITH THE CARBON BLACK RESPONSE SERVER

import json
import ssl
import httplib
import jfexceptions
import jfutil

# THIS FUNCTION TAKES THE PARAMETERS PASSED TO JETFREQ AND FORMATS
# THE SEARCH QUERY FOR CARBON BLACK APPROPRIATELY
def format_query(params):
	query = ""
	
	# IF THE MODE IS AN 'EVENT' MODE, ONLY ONE EVENT TYPE IS ADDED TO THE QUERY
	if params['mode'] == 'BY_EVENT' or params['mode'] == 'COMPARE_EVENT':
	 	if params['modloads'] == True:
			query += "modload%3A{}".format(params['search_name'])
		elif params['regmods'] == True:
			query += "regmod%3A{}".format(params['search_name'])
		elif params['childprocs'] == True:
			query += "childproc_name%3A{}".format(params['search_name'])
		elif params['filemods'] == True:
			query += "filemod%3A{}".format(params['search_name'])
		elif params['netconns'] == True:
			query += "domain%3A{}".format(params['search_name'])
		query += "%20start%3A{}".format(params['start_time'])
	else:
		# IF THE MODE IS A 'PROCESS' MODE, ADD THE PROCESS SEARCH NAME ONLY
		query += "process_name%3A{}%20start%3A{}".format(params['search_name'], params['start_time'])
	
	# IF A USER OR EXCLUDE-USER HAS BEEN INCLUDED, APPEND IT TO THE QUERY
	if params['user_name'] != None:
		query += "%20username%3A{}".format(params['user_name'])
	elif params['exclude_user'] != None:
		query += "%20-username%3A{}".format(params['exclude_user'])
	
	# IF A HOST OR EXLUDE-HOST HAS BEEN INCLUDED, APPEND IT TO THE QUERY
	if params['host_name'] != None:
		query += "%20hostname%3A{}".format(params['host_name'])
	elif params['exclude_host'] != None:
		query += "%20-hostname%3A{}".format(params['exclude_host'])

	jfutil.debug(params['verbose'], "Query formatted \'{}\'".format(query))

	return query

# THIS FUNCTION SENDS A QUERY OVER HTTPS TO THE CARBON BLACK SERVER
def send_query(params, url):
	try:
		conn = httplib.HTTPSConnection(params['server'], context=ssl._create_unverified_context())
		conn.request("GET", url, None, headers={'X-Auth-Token':params['key']})
		return conn.getresponse()
	except Exception as err:
		jfutil.debug(True, "Query \'{}\' failed\n{}".format(url, str(err)))
		exit()

# THIS IS THE MAIN FUNCTION FOR FETCHING DATA FOR A GIVEN EVENT
def get_data_for_event(params):
	# FORMAT THE URL, INCLUDING THE QUERY
	query = format_query(params)
	url = "/api/v1/process?cb.urlver=1&rows={}&start=0&q={}".format(params['sample_size'], query)
	jfutil.debug(params['verbose'], 'Attempting to send query to Carbon Black server')
	jfutil.debug(params['verbose'], 'Server: {}'.format(params['server']))
	jfutil.debug(params['verbose'], 'API Key: {}'.format(params['key']))
	jfutil.debug(params['verbose'], 'URL: {}'.format(url))
	
	# SEND THE QUERY TO THE CARBON BLACK SERVER AND STORE THE RESULT
	response = send_query(params, url)
	jfutil.debug(params['verbose'], 'Response: \'{} {}\''.format(response.status, httplib.responses[response.status]))
	
	# STORE THE PATH, PROCESS ID AND SEGMENT ID FOR EACH PROCESS RETURNED BY THE QUERY
	data = json.loads(response.read())
	process_list = []
	jfutil.debug(True, 'Processing response from {}'.format(params['server']))
	try: 
		if 'results' in data:
			for result in data['results']:
				process_list.append({
					'path':jfutil.homogenize_path(result['path'], 'dir', params['homogenize']),
					'process_id':result['id'],
					'segment_id':result['segment_id']
				})
	except KeyError:
		raise jfexceptions.UnexpectedResponseError(data)
	
	# IF THERE ARE ANY RESULTS, RETURN THE LIST OF PROCESSES
	if len(process_list) > 0:
		return process_list
	else:
		raise jfexceptions.NoResultsError(query)

# THIS IS THE MAIN FUNCTION FOR FETCHING DATA FOR A GIVEN PROCESS
def get_data_for_process(params):
	# FORMAT THE URL, INCLUDING THE QUERY
	query = format_query(params)
	url = "/api/v1/process?cb.urlver=1&rows={}&start=0&q={}".format(params['sample_size'], query)
	jfutil.debug(params['verbose'], 'Attempting to send query to Carbon Black server')
	jfutil.debug(params['verbose'], 'Server: {}'.format(params['server']))
	jfutil.debug(params['verbose'], 'API Key: {}'.format(params['key']))
	jfutil.debug(params['verbose'], 'URL: {}'.format(url))
	
	# SEND THE QUERY TO THE CARBON BLACK SERVER AND STORE THE RESULT
	response = send_query(params, url)
	jfutil.debug(params['verbose'], 'Response: \'{} {}\''.format(response.status, httplib.responses[response.status]))
	
	# FOR EACH PROCESS RETURNED IN THE RESULTS, STORE THE PROCESS ID AND SEGMENT ID
	data = json.loads(response.read())
	id_list = []
	jfutil.debug(True, 'Processing response from {}'.format(params['server']))
	try:
		if 'results' in data:
			for result in data['results']:
				id_list.append({
					'process_id':result['id'],
					'segment_id':result['segment_id']
				})
	except KeyError:
		raise jfexceptions.UnexpectedResponseError(data)
	
	# FOR EACH PROCESS ID AND SEGMENT ID PAIR...
	events = []
	if len(id_list) > 0:
		jfutil.debug(True, 'Fetching event details for {} processes'.format(len(id_list)))
		event_cnt = 0
		for i in id_list:
			# USE THE IDS TO FORMAT A REST API URL AND FETCH THAT PROCESSES EVENT DETAILS
			event_cnt = event_cnt + 1
			event = {}
			jfutil.debug(params['verbose'], "Getting events for result {}".format(event_cnt))
			url = "/api/v1/process/{}/0/event".format(i['process_id'])
			response = send_query(params, url)
			data = json.loads(response.read())
			
			# IF THE USER REQUESTED MODLOADS...
			if params['modloads'] == True:
				# AND THERE ARE MODLOADS IN THE SEARCH RESULTS...
				if 'modload_complete' in data['process']:
					# EXTRACT THE PATHS OF THE EVENTS AND STORE THEM IN THE MODLOADS LIST
					event['modloads'] = jfutil.get_event_paths(data['process']['modload_complete'], 2, 'dir', params['homogenize'])
				else:
					jfutil.debug(params['verbose'], "Result {} has no modloads".format(event_cnt))
			# IF THE USER REQUESTED FILEMODS...
			if params['filemods'] == True:
				# AND THERE ARE FILEMODS IN THE SEARCH RESULTS...
				if 'filemod_complete' in data['process']:
					# EXTRACT THE PATHS OF THE EVENTS AND STORE THEM IN THE FILEMODS LIST
					event['filemods'] = jfutil.get_event_paths(data['process']['filemod_complete'], 2, 'dir', params['homogenize'])
				else:
					jfutil.debug(params['verbose'], "Result {} has no filemods".format(event_cnt))
			# IF THE USER REQUESTED REGMODS...
			if params['regmods'] == True:
				# AND THERE ARE REGMODS IN THE SEARCH RESULTS...
				if 'regmod_complete' in data['process']:
					# EXTRACT THE PATHS OF THE EVENTS AND STORE THEM IN THE REGMODS LIST
					event['regmods'] = jfutil.get_event_paths(data['process']['regmod_complete'], 2, 'reg', params['homogenize'])
				else:
					jfutil.debug(params['verbose'], "Result {} has no regmods".format(event_cnt))
			# IF THE USER REQUESTED CHILDPROCS...
			if params['childprocs'] == True:
				# AND THERE ARE CHILDPROCS IN THE SEARCH RESULTS...
				if 'childproc_complete' in data['process']:
					# EXTRACT THE PATHS OF THE EVENTS AND STORE THEM IN THE CHILDPROCS LIST
					event['childprocs'] = jfutil.get_event_paths(data['process']['childproc_complete'], 3, 'dir', params['homogenize'])
				else:
					jfutil.debug(params['verbose'], "Result {} has no childprocs".format(event_cnt))
			# IF THE USER REQUESTED CROSSPROCS...
			if params['crossprocs'] == True:
				# AND THERE ARE CROSSPROCS IN THE SEARCH RESULTS...
				if 'crossproc_complete' in data['process']:
					# EXTRACT THE PATHS OF THE EVENTS AND STORE THEM IN THE CROSSPROCS LIST
					event['crossprocs'] = jfutil.get_event_paths(data['process']['crossproc_complete'], 4, 'dir', params['homogenize'])
				else:
					jfutil.debug(params['verbose'], "Result {} has no crossprocs".format(event_cnt))
			# IF THE USER REQUESTED NETCONNS...
			if params['netconns'] == True:
				# AND THERE ARE NETCONNS IN THE SEARCH RESULTS...
				if 'netconn_complete' in data['process']:
					# EXTRACT THE DOMAINS OF THE EVENTS AND STORE THEM IN THE NETCONNS LIST
					event['netconns'] = jfutil.get_event_paths(data['process']['netconn_complete'], 4, 'dir', params['homogenize'])
				else:
					jfutil.debug(params['verbose'], "Result {} has no netconns".format(event_cnt))
			# IF ANY REQUESTED EVENTS HAVE BEEN EXTRACTED FROM THIS PROCESS, ADD THEM TO THE EVENT LIST
			if 'modloads' in event or 'filemods' in event or 'regmods' in event or 'childprocs' in event or 'crossprocs' in event or 'netconns' in event:
				events.append(event)
	else:
		raise jfexceptions.NoResultsError(query)
	# IF ANY EVENTS WERE FOUND, RETURN THE EVENTS LIST
	if len(events) > 0:	
		return events
	else:
		raise jfexceptions.NoEventsFoundError(query)
