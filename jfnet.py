import json
import ssl
import httplib
import jfexceptions
import jfutil

def format_query(params):
	query = ""
	if params['by_modload'] == True:
	 	jfutil.debug(True, 'Function not yet available')
		exit()
	else:
		query += "process_name%3A{}%20start%3A{}".format(params['search_name'], params['start_time'])
		if params['user_name'] != None:
			query += "%20username%3A{}".format(params['user_name'])
	jfutil.debug(params['verbose'], "Query formatted \'{}\'".format(query))
	return query

def send_query(params, url):
	try:
		jfutil.debug(params['verbose'], "Attempting to send query to {} with API Token {}".format(params['server'], params['key']))
		conn = httplib.HTTPSConnection(params['server'], context=ssl._create_unverified_context())
		conn.request("GET", url, None, headers={'X-Auth-Token':params['key']})
		jfutil.debug(params['verbose'], "Query successful \'{}\'".format(url))
		return conn.getresponse()
	except Exception as err:
		jfutil.debug(True, "Query \'{}\' failed\n{}".format(url, str(err)))
		exit()

def get_data_for_modload(params):
	pass

def get_data_for_process(params):

	# build array of process_ids
	query = format_query(params)
	url = "/api/v1/process?cb.urlver=1&rows={}&start=0&q={}".format(params['sample_size'], query)
	response = send_query(params, url)
	jfutil.debug(params['verbose'], 'Response from {} is \'{} {}\''.format(params['server'], response.status, httplib.responses[response.status]))
	
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
		for i in id_list:
			event = {}
			jfutil.debug(params['verbose'], "Getting events for {}".format(i['process_id']))
			url = "/api/v1/process/{}/{}/event".format(i['process_id'], i['segment_id'])
			response = send_query(params, url)
			data = json.loads(response.read())

			if 'modload_complete' in data['process']:
				event['modloads'] = jfutil.get_event_paths(data['process']['modload_complete'], 2)
			else:
				jfutil.debug(params['verbose'], "Process {} has no modloads".format(i['process_id']))
#
#FIXME : Disabling import of regmods, filemods, childprocs, crossprocs and netconns until modloads is completed
#
#			if params['filemods'] == True:
#				if 'filemod_complete' in data['process']:
#					event['filemods'] = data['process']['filemod_complete']
#				else:
#					jfutil.debug(params['verbose'], "Process {} has no filemods".format(i['process_id']))
#
#			if params['regmods'] == True:
#				if 'regmod_complete' in data['process']:
#					event['regmods'] = data['process']['regmod_complete']
#				else:
#					jfutil.debug(params['verbose'], "Process {} has no regmods".format(i['process_id']))
#
#			if params['childprocs'] == True:
#				if 'childproc_complete' in data['process']:
#					event['childprocs'] = data['process']['childproc_complete']
#				else:
#					jfutil.debug(params['verbose'], "Process {} has no childprocs".format(i['process_id']))
#
#			if params['crossprocs'] == True:
#				if 'crossproc_complete' in data['process']:
#					event['crossprocs'] = data['process']['crossproc_complete']
#				else:
#					jfutil.debug(params['verbose'], "Process {} has no crossprocs".format(i['process_id']))
#
#			if params['netconns'] == True:
#				if 'netconn_complete' in data['process']:
#					event['netconns'] = data['process']['netconn_complete']
#				else:
#					jfutil.debug(params['verbose'], "Process {} has no netconns".format(i['process_id']))
#FIXME
			
			if 'modloads' in event or 'filemods' in event or 'regmods' in event or 'childprocs' in event or 'crossprocs' in event or 'netconns' in event:
				events.append(event)
	else:
		raise jfexceptions.NoResultsError(query)
	
	if len(events) > 0:	
		return events
	else:
		raise jfexceptions.NoEventsFoundError(query)
