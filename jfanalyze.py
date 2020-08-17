# THIS MODULE CONTAINS ALL FUNCTIONS RESPONSIBLE FOR PROCESSING
# PARAMETERS AND FLAGS PASSED TO JETFREQ ON THE COMMAND LINE

import re
import json
import jfutil
import jfexceptions

# THIS FUNCTION CONDUCTS A 'RUN-THE-GAUNTLET' STYLE INTEGRITY CHECK 
# OF THE PARAMETERS AND ABORTS JETFREQ IF ANY CONDITIONS FAIL
def check_params(params):
	# IF JETFREQ IS RUN IN AN 'EVENT' MODE, CHECK THERE IS EXACTLY ONE EVENT TYPE FLAG (EXCLUDING CROSSPROCS)
	if params['mode'] == 'BY_EVENT' or params['mode'] == 'COMPARE_EVENT':
		flags = jfutil.get_event_type_flags(params)
		if len(flags) > 1:
			raise jfexceptions.IncorrectFlagUsageForModeError(params['mode'], flags)
		if len(flags) == 0:
			raise jfexceptions.ByEventModeFlagRequiredError(params['mode'])
		if 'x' in flags:
			raise jfexceptions.FlagsNotApplicableError(params['mode'], 'x')
	
	# IF JETFREQ IS RUN IN A 'PROCESS' MODE, CHECK THERE IS ONE OR MORE EVENT TYPE FLAGS
	if params['mode'] == 'BY_PROCESS' or params['mode'] == 'COMPARE_PROCESS':
		if params['regmods'] == False and params['filemods'] == False and params['childprocs'] == False and params['netconns'] == False and params['crossprocs'] == False and params['modloads'] == False:
			raise jfexceptions.ProcessModeMissingEventTypeError(params['mode'])
	
	# IF JETFREQ IS RUN IN A 'COMPARE' MODE, CHECK THAT A SAMPLE FILE HAS BEEN IDENTIFIED
	if params['import_sample'] == None and (params['mode'] == 'COMPARE_PROCESS' or params['mode'] == 'COMPARE_EVENT'):
		raise jfexceptions.CompareModeMissingSampleFileError(params['mode'])

	# IF JETFREQ IS NOT RUN IN A 'COMPARE' MODE, CHECK THAT A SAMPLE FILE HAS NOT BEEN IDENTIFIED
	if re.match(r'COMPARE_', params['mode']) == None and not params['import_sample'] == None:
		raise jfexceptions.FlagsNotApplicableError(params['mode'], 'i')

	# CHECK THAT A USER NAME HAS BEEN INCLUDED OR EXCLUDED, BUT NOT BOTH
	if not params['user_name'] == None and not params['exclude_user'] == None:
		params['exclude_user'] == None

	# CHECK THAT A HOST NAME HAS BEEN INCLUDED OR EXCLUDED, BUT NOT BOTH
	if not params['host_name'] == None and not params['exclude_host'] == None:
		params['exclude_host'] == None
	
	# CHECK THAT THE GREATER-THAN AND LESS-THAN THRESHOLD VALUES ARE NOT EQUAL
	if params['threshold_gt'] == params['threshold_lt']:
		raise jfexceptions.NonsensicalThresholdValuesError(params['threshold_gt'], params['threshold_lt'])
	
	# DO NOT TRUNCATE IF WRITING
	if params['write_file'] and params['truncate']:
		params['truncate'] = False
		jfutil.debug(True, 'JetFreq does not truncate when writing to file. Ignoring -k flag.')

	return params

# THIS FUNCTION IMPORTS THE SYS.ARGV[] ARRAY AND TRANSFORMS IT INTO A JSON OBJECT
# THAT CAN BE PASSED BETWEEN FUNCTIONS IN JETFREQ
def process_params(args):
	# DEFINE THE FLAGS THAT ARE USED IN JETFREQ, INCLUDING THEIR NAME,
	# WHETHER THEY REQUIRE A PARAMETER AND TRACK THEIR USE
	flags = {
		"u":{"name":"user_name","param":True,"assigned":False},
		"U":{"name":"exclude_user","param":True,"assigned":False},
		"h":{"name":"host_name","param":True,"assigned":False},
		"H":{"name":"exclude_host","param":True,"assigned":False},
		"s":{"name":"start_time","param":True,"assigned":False},
		"n":{"name":"sample_size","param":True,"assigned":False},
		"t":{"name":"threshold_lt","param":True,"assigned":False},
		"T":{"name":"threshold_gt","param":True,"assigned":False},
		"i":{"name":"import_sample","param":True,"assigned":False},
		"w":{"name":"write_file","param":False,"assigned":False},
		"v":{"name":"verbose","param":False,"assigned":False},
		"r":{"name":"regmods","param":False,"assigned":False},
		"f":{"name":"filemods","param":False,"assigned":False},
		"c":{"name":"childprocs","param":False,"assigned":False},
		"d":{"name":"netconns","param":False,"assigned":False},
		"x":{"name":"crossprocs","param":False,"assigned":False},
		"m":{"name":"modloads","param":False,"assigned":False},
		"k":{"name":"truncate","param":False,"assigned":False},
		"by-process":{"name":"BY_PROCESS","param":False,"assigned":False},
		"by-event":{"name":"BY_EVENT","param":False,"assigned":False},
		"help":{"name":"SHOW_HELP","param":False,"assigned":False},
		"compare-process":{"name":"COMPARE_PROCESS","param":False,"assigned":False},
		"compare-event":{"name":"COMPARE_EVENT","param":False,"assigned":False}
	}

	# INITIALIZE THE 'PARAMS' JSON OBJECT TO HOLD THE PARAMETERS
	params = {
		"server":None,
		"key":None,
		"search_name":None,
		"mode":'BY_PROCESS',
		"user_name":None,
		"exclude_user":None,
		"host_name":None,
		"exclude_host":None,
		"import_sample":None,
		"start_time":"-672h",
		"write_file":False,
		"sample_size":50,
		"threshold_lt":100,
		"threshold_gt":0,
		"verbose":False,
		"truncate":False,
		"regmods":False,
		"filemods":False,
		"childprocs":False,
		"netconns":False,
		"crossprocs":False,
		"modloads":False
	}
	
	# REMOVE THE FIRST ARGUMENT FROM SYS.ARGV[] (ALWAYS './jetfreq.py')
	args = args[1:len(args)]

	# CHECK THAT THE ARGUMENT LIST IS NOT EMPTY
	if len(args) == 0:
		raise jfexceptions.NoArgsError("jetfreq.py requires arguments")

	# IF THE FIRST ARGUMENT IS A MODE FLAG...
	if args[0].startswith('--'):	
		a = args[0][2:len(args[0])]
		# AND THE MODE EXISTS...
		if a in flags:
			# ASSIGN THE VALUE TO THE 'MODE' PARAMETER
			params["mode"] = flags[a]['name']
			# IF THE MODE IS --HELP, EXIT FUNCTION
			if params["mode"] == "SHOW_HELP":
				return params
			else:
				# TRIM THE ARGUMENT LIST
				args = args[1:len(args)]
		else:
			raise jfexceptions.IncorrectUsageError(" ".join(args))
	# OTHERWISE, ASSIGN THE DEFAULT MODE
	else:
		params["mode"] == flags["by-process"]['name']

	# IF THE MODE IS A 'PROCESS' MODE, THE NEXT ARGUMENT MUST BE THE SEARCH NAME
	if params['mode'] == 'BY_PROCESS' or params['mode'] == 'COMPARE_PROCESS':
		if args[0].startswith('-'):
			raise jfexceptions.IncorrectUsageError(" ".join(args))
		else:
			params['search_name'] = args[0]
			args = args[1:len(args)]
	# IF THE MODE IS AN 'EVENT' MODE, THE NEXT ARGUMENT MUST BE THE EVENT TYPE FLAG, FOLLOWED BY THE SEARCH NAME
	else:
		if not args[0].startswith('-'):
			raise jfexceptions.IncorrectUsageError(" ".join(args))
		else:
			# IF THE FLAGS ARE NOT CLUSTERED (I.E. THERE IS ONLY ONE FLAG)...
			if len(args[0][1:len(args[0])]) > 1:
				raise jfexceptions.IncorrectUsageError(" ".join(args))
			else:
				# AND THERE ARE AT LEAST TWO ARGUMENTS (I.E. AN EVENT TYPE AND A SEARCH NAME)...
				if len(args) == 1: 
					raise jfexceptions.IncorrectUsageError(" ".join(args))
				else:
					# AND THE CURRENT FLAG IS NOT FOLLOWED BY ANOTHER FLAG (I.E. IT MUST BE THE SEARCH NAME)...
					if args[1].startswith('-'):
						raise jfexceptions.IncorrectUsageError(" ".join(args[1:len(args)]))
					else:
						# ADD THE EVENT TYPE AND THE SEARCH NAME TO 'PARAMS' AND TRIM ARG LIST
						params[flags[args[0][1:len(args[0])]]['name']] = True
						params['search_name'] = args[1]
						args = args[2:len(args)]

	# FOR EACH REMAINING ELEMENT IN THE ARG LIST...
	while len(args) > 0:
		# ALL FLAGS MUST START WITH A '-' CHAR
		if not args[0].startswith('-'):
			raise jfexceptions.IncorrectUsageError(" ".join(args))
		else:
			# IF THE FLAGS ARE CLUSTERED (I.E. MORE THAN ONE FLAG)...
			if len(args[0][1:len(args[0])]) > 1:
				cluster = args[0][1:len(args[0])]
				# FOR EACH FLAG IN THE CLUSTER...
				for a in cluster:
					if a in flags:
						# IF THE FLAG DOES NOT REQUIRE A VALUE...
						if flags[a]['param'] == True:
							raise jfexceptions.IncorrectUsageError(" ".join(args))
						# AND THE FLAG HAS NOT ALREADY BEEN USED...
						elif flags[a]['assigned'] == True:
							raise jfexceptions.DoubleArgumentError(a)
						else:
							# UPDATE THE VALUE IN 'PARAMS'
							params[flags[a]['name']] = True
							flags[a]['assigned'] = True
					else:
						raise jfexceptions.NoSuchArgumentError(a)
				# TRIM THE ARGS LIST
				args = args[1:len(args)]
			else:
				a = args[0][1:len(args[0])]
				if a in flags:
					# IF THE FLAG REQUIRES A VALUE...
					if flags[a]['param'] == True:
						# AND A POTENTIAL VALUE EXISTS...
						if len(args) > 1:
							# AND THE POTENTIAL VALUE IS NOT ANOTHER FLAG...
							if args[1].startswith('-') and not flags[a]['name'] == 'start_time':
								raise jfexceptions.MissingValueError(a, flags[a]['name'])
							# AND THE FLAG HAS NOT YET BEEN USED...
							elif flags[a]['assigned'] == True:
								raise jfexceptions.DoubleArgumentError(a)
							else:
								# ASSIGN THE VALUE IN 'PARAMS'
								params[flags[a]['name']] = args[1]
								flags[a]['assigned'] = True
						else:
							raise jfexceptions.MissingValueError(a, flags[a]['name'])
						# TRIM THE ARGS LIST
						args = args[2:len(args)]
					# IF THE FLAG DOES NOT REQUIRE A VALUE...
					else:
						# AND THE NEXT FLAG IS NOT A VALUE...
						if len(args) > 1 and not args[1].startswith('-'):
							raise jfexceptions.IncorrectUsageError(" ".join(args))
						# AND THE FLAG HAS NOT YET BEEN USED...
						elif flags[a]['assigned'] == True:
							raise jfexceptions.DoubleArgumentError(a)
						else:
							# ASSIGN THE VALUE IN 'PARAMS'
							params[flags[a]['name']] = True
							flags[a]['assigned'] = True
						# TRIM THE ARGS LIST
						args = args[1:len(args)]
				else:
					raise jfexceptions.NoSuchArgumentError(a)
	
	# IF THE USER HAS EXPLICITLY CALLED ONE OF THE THRESHOLD FLAGS, REMOVE THE DEFAULT VALUE FOR THE OTHER
	if flags['t']['assigned'] == True and flags['T']['assigned'] == False:
		params['threshold_gt'] = None
	elif flags['T']['assigned'] == True and flags['t']['assigned'] == False:
		params['threshold_lt'] = None
	
	# IMPORT THE SERVER NAME AND API KEY VALUE FROM THE JETFREQ CONFIG FILE
	params = jfutil.import_conf(params)
	if params['server'] == None or len(params['server']) == 0 or params['key'] == None or len(params['key']) == 0:
		raise jfexceptions.MissingConfigurationError()
	
	return check_params(params)
