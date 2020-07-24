import json
import ssl
import httplib
import jfexceptions
import jfutil

def format_query(params):
	query = ""

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
		query += "process_name%3A{}%20start%3A{}".format(params['search_name'], params['start_time'])

	if params['user_name'] != None:
		query += "%20username%3A{}".format(params['user_name'])
	if params['host_name'] != None:
		query += "%20hostname%3A{}".format(params['host_name'])

	jfutil.debug(params['verbose'], "Query formatted \'{}\'".format(query))

	return query

def send_query(params, url):
	try:
		conn = httplib.HTTPSConnection(params['server'], context=ssl._create_unverified_context())
		conn.request("GET", url, None, headers={'X-Auth-Token':params['key']})
		return conn.getresponse()
	except Exception as err:
		jfutil.debug(True, "Query \'{}\' failed\n{}".format(url, str(err)))
		exit()

def get_data_for_event(params):
	query = format_query(params)
	url = "/api/v1/process?cb.urlver=1&rows={}&start=0&q={}".format(params['sample_size'], query)

	jfutil.debug(params['verbose'], 'Attempting to send query to Carbon Black server')
	jfutil.debug(params['verbose'], 'Server: {}'.format(params['server']))
	jfutil.debug(params['verbose'], 'API Key: {}'.format(params['key']))
	jfutil.debug(params['verbose'], 'URL: {}'.format(url))

	response = send_query(params, url)

	jfutil.debug(params['verbose'], 'Response: \'{} {}\''.format(response.status, httplib.responses[response.status]))
	
	data = json.loads(response.read())
	process_list = []
	try: 
		if 'results' in data:
			for result in data['results']:
				process_list.append({
					'path':jfutil.homogenize_path(result['path']),
					'process_id':result['id'],
					'segment_id':result['segment_id']
				})
	except KeyError:
		raise jfexceptions.UnexpectedResponseError(data)
	
	if len(process_list) > 0:
		return process_list
	else:
		raise jfexceptions.NoResultsError(query)

def get_data_for_process(params):

	# build array of process_ids
	query = format_query(params)
	url = "/api/v1/process?cb.urlver=1&rows={}&start=0&q={}".format(params['sample_size'], query)

	jfutil.debug(params['verbose'], 'Attempting to send query to Carbon Black server')
	jfutil.debug(params['verbose'], 'Server: {}'.format(params['server']))
	jfutil.debug(params['verbose'], 'API Key: {}'.format(params['key']))
	jfutil.debug(params['verbose'], 'URL: {}'.format(url))

	response = send_query(params, url)

	jfutil.debug(params['verbose'], 'Response: \'{} {}\''.format(response.status, httplib.responses[response.status]))
	
	# get ids to drill down 
	data = json.loads(response.read())
	id_list = []
	try:
		if 'results' in data:
			for result in data['results']:
				id_list.append({
					'process_id':result['id'],
					'segment_id':result['segment_id']
				})
	except KeyError:
		raise jfexceptions.UnexpectedResponseError(data)
	
	# get modloads for events
	events = []
	if len(id_list) > 0:
		jfutil.debug(params['verbose'], 'Fetching details for {} results'.format(len(id_list)))
		event_cnt = 0
		for i in id_list:
			event_cnt = event_cnt + 1
			event = {}
			jfutil.debug(params['verbose'], "Getting events for result {}".format(event_cnt))
			url = "/api/v1/process/{}/{}/event".format(i['process_id'], i['segment_id'])
			response = send_query(params, url)
			data = json.loads(response.read())

			if params['modloads'] == True:
				if 'modload_complete' in data['process']:
					event['modloads'] = jfutil.get_event_paths(data['process']['modload_complete'], 2)
				else:
					jfutil.debug(params['verbose'], "Result {} has no modloads".format(event_cnt))

			if params['filemods'] == True:
				if 'filemod_complete' in data['process']:
					event['filemods'] = jfutil.get_event_paths(data['process']['filemod_complete'], 2)
				else:
					jfutil.debug(params['verbose'], "Result {} has no filemods".format(event_cnt))

			if params['regmods'] == True:
				if 'regmod_complete' in data['process']:
					event['regmods'] = jfutil.get_event_paths(data['process']['regmod_complete'], 2)
				else:
					jfutil.debug(params['verbose'], "Result {} has no regmods".format(event_cnt))

			if params['childprocs'] == True:
				if 'childproc_complete' in data['process']:
					event['childprocs'] = jfutil.get_event_paths(data['process']['childproc_complete'], 3)
				else:
					jfutil.debug(params['verbose'], "Result {} has no childprocs".format(event_cnt))

			if params['crossprocs'] == True:
				if 'crossproc_complete' in data['process']:
					event['crossprocs'] = jfutil.get_event_paths(data['process']['crossproc_complete'], 4)
				else:
					jfutil.debug(params['verbose'], "Result {} has no crossprocs".format(event_cnt))

			if params['netconns'] == True:
				if 'netconn_complete' in data['process']:
					event['netconns'] = jfutil.get_event_paths(data['process']['netconn_complete'], 4)
				else:
					jfutil.debug(params['verbose'], "Result {} has no netconns".format(event_cnt))
			
			if 'modloads' in event or 'filemods' in event or 'regmods' in event or 'childprocs' in event or 'crossprocs' in event or 'netconns' in event:
				events.append(event)
	else:
		raise jfexceptions.NoResultsError(query)
	
	if len(events) > 0:	
		return events
	else:
		raise jfexceptions.NoEventsFoundError(query)
