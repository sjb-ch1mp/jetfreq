import re
import json
import jfutil
import jfexceptions

# Run-the-gauntlet style condition check for parameter combinations
def check_params(params):
	# BY_EVENT and COMPARE_EVENT modes do not have event type flags
	if params['mode'] == 'BY_EVENT' or params['mode'] == 'COMPARE_EVENT':
		flags = jfutil.get_event_type_flags(params)
		if len(flags) > 1:
			raise jfexceptions.IncorrectFlagUsageForModeError(params['mode'], flags)
		if len(flags) == 0:
			raise jfexceptions.ByEventModeFlagRequiredError(params['mode'])
		if 'x' in flags:
			raise jfexceptions.FlagsNotApplicableError(params['mode'], 'x')
	
	# BY_PROCESS and COMPARE_PROCESS modes require at least one event type flag
	if params['mode'] == 'BY_PROCESS' or params['mode'] == 'COMPARE_PROCESS':
		if params['regmods'] == False and params['filemods'] == False and params['childprocs'] == False and params['netconns'] == False and params['crossprocs'] == False and params['modloads'] == False:
			raise jfexceptions.ProcessModeMissingEventTypeError(params['mode'])
	
	# COMPARE modes require a representative sample file to be identified
	if params['import_sample'] == None and (params['mode'] == 'COMPARE_PROCESS' or params['mode'] == 'COMPARE_EVENT'):
		raise jfexceptions.CompareModeMissingSampleFileError(params['mode'])

	# incompatible flags
	if re.match(r'COMPARE_', params['mode']) == None and not params['import_sample'] == None:
		raise jfexceptions.FlagsNotApplicableError(params['mode'], 'i')

	return params

# Import sys.argv[] and convert it into a JSON holding all parameters
def process_params(args):
	flags = {
		"u":{"name":"user_name","param":True,"assigned":False},
		"h":{"name":"host_name","param":True,"assigned":False},
		"s":{"name":"start_time","param":True,"assigned":False},
		"e":{"name":"end_time","params":True,"assigned":False},
		"n":{"name":"sample_size","param":True,"assigned":False},
		"t":{"name":"threshold","param":True,"assigned":False},
		"i":{"name":"import_sample","param":True,"assigned":False},
		"w":{"name":"write_file","param":False,"assigned":False},
		"v":{"name":"verbose","param":False,"assigned":False},
		"r":{"name":"regmods","param":False,"assigned":False},
		"f":{"name":"filemods","param":False,"assigned":False},
		"c":{"name":"childprocs","param":False,"assigned":False},
		"d":{"name":"netconns","param":False,"assigned":False},
		"x":{"name":"crossprocs","param":False,"assigned":False},
		"m":{"name":"modloads","param":False,"assigned":False},
		"by-process":{"name":"BY_PROCESS","param":False,"assigned":False},
		"by-event":{"name":"BY_EVENT","param":False,"assigned":False},
		"help":{"name":"SHOW_HELP","param":False,"assigned":False},
		"compare-process":{"name":"COMPARE_PROCESS","param":False,"assigned":False},
		"compare-event":{"name":"COMPARE_EVENT","param":False,"assigned":False}
	}

	params = {
		"server":None,
		"key":None,
		"search_name":None,
		"mode":'BY_PROCESS',
		"user_name":None,
		"host_name":None,
		"import_sample":None,
		"start_time":"-72h",
		"write_file":False,
		"sample_size":10,
		"threshold":"100",
		"verbose":False,
		"regmods":False,
		"filemods":False,
		"childprocs":False,
		"netconns":False,
		"crossprocs":False,
		"modloads":False
	}
	
	# remove module argument
	args = args[1:len(args)]

	# check for no args
	if len(args) == 0:
		raise jfexceptions.NoArgsError("jetfreq.py requires arguments")

	# check for mode flag
	if args[0].startswith('--'):	
		a = args[0][2:len(args[0])]
		if a in flags:
			params["mode"] = flags[a]['name']
			if params["mode"] == "SHOW_HELP":
				return params
			else:
				args = args[1:len(args)]
		else:
			raise jfexceptions.IncorrectUsageError(" ".join(args))
	else:
		params["mode"] == flags["by-process"]['name']

	# get search name
	if args[0].startswith('-'):
		raise jfexceptions.IncorrectUsageError(" ".join(args))
	else:
		params['search_name'] = args[0]
		args = args[1:len(args)]

	# process args
	while len(args) > 0:
		if not args[0].startswith('-'):
			raise jfexceptions.IncorrectUsageError(" ".join(args))
		else:
			# process clustered flags
			if len(args[0][1:len(args[0])]) > 1:
				cluster = args[0][1:len(args[0])]
				for a in cluster:
					if a in flags:
						if a == 'h':
							raise jfexceptions.IncorrectUsageError(" ".join(args))
						elif flags[a]['param'] == True:
							raise jfexceptions.IncorrectUsageError(" ".join(args))
						elif flags[a]['assigned'] == True:
							raise jfexceptions.DoubleArgumentError(a)
						else:
							params[flags[a]['name']] = True
							flags[a]['assigned'] = True
					else:
						raise jfexceptions.NoSuchArgumentError(a)
				args = args[1:len(args)]
			else:
				a = args[0][1:len(args[0])]
				if a in flags:
					# process flags with params
					if flags[a]['param'] == True:
						if len(args) > 1:
							if args[1].startswith('-') and not flags[a]['name'] == 'start_time':
								raise jfexceptions.MissingValueError(a, flags[a]['name'])
							elif flags[a]['assigned'] == True:
								raise jfexceptions.DoubleArgumentError(a)
							else:								
								params[flags[a]['name']] = args[1]
								flags[a]['assigned'] = True
						else:
							raise jfexceptions.MissingValueError(a, flags[a]['name'])
						args = args[2:len(args)]
					# process flags without params
					else:
						if len(args) > 1 and not args[1].startswith('-'):
							raise jfexceptions.IncorrectUsageError(" ".join(args))
						elif flags[a]['assigned'] == True:
							raise jfexceptions.DoubleArgumentError(a)
						else:
							params[flags[a]['name']] = True
							flags[a]['assigned'] = True
						args = args[1:len(args)]
				else:
					raise jfexceptions.NoSuchArgumentError(a)
	
	# import server name and api_key
	params = jfutil.import_conf(params)
	if params['server'] == None or len(params['server']) == 0 or params['key'] == None or len(params['key']) == 0:
		raise jfexceptions.MissingConfigurationError()
	
	return check_params(params)	
