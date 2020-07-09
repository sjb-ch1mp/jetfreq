import re
import jfexceptions

def debug(verbose, message):
	if verbose:
		print("jetfreq.py: {}".format(message))

def format_report(params, data):
	# format the data into a human-readable format
	pass

def out_file(params, data):
	# writes the report to a file
	pass

def show_usage():
	h = open("README.txt", "r")
	usage = ""
	capture = False
	for line in h:
		if capture == False and len(usage) > 0:
			break
		elif capture == True:
			usage += line
			if re.match(r'^show_help', line) != None: 
				capture = False
		elif re.match(r'^Usage:', line) != None:
			capture = True
	print("\nUSAGE:\n{}".format(usage))

def show_help():
	h = open("README.txt", "r")
	print(h.read())

def import_conf(params):
	conf = open('./conf/jetfreq.cfg', 'r')
	for line in conf:
		if line.startswith('#'):
			pass
		else:
			params[line.split('=')[0].lower().strip()] = line.split('=')[1].strip()
	conf.close()
	return params

def process_params(args):
	flags = {
		"u":{"name":"user_name","param":True,"assigned":False},
		"s":{"name":"start_time","param":True,"assigned":False},
		"w":{"name":"write_file","param":True,"assigned":False},
		"n":{"name":"sample_size","param":True,"assigned":False},
		"t":{"name":"threshold","param":True,"assigned":False},
		"v":{"name":"verbose","param":False,"assigned":False},
		"r":{"name":"regmods","param":False,"assigned":False},
		"f":{"name":"filemods","param":False,"assigned":False},
		"c":{"name":"childprocs","param":False,"assigned":False},
		"d":{"name":"netconns","param":False,"assigned":False},
		"x":{"name":"crossprocs","param":False,"assigned":False},
		"m":{"name":"by_modload","param":False,"assigned":False},
		"h":{"name":"help","param":False,"assigned":False}
	}

	params = {
		"server":None,
		"key":None,
		"search_name":None,
		"by_modload":False,
		"user_name":None,
		"start_time":"-72h",
		"write_file":None,
		"sample_size":10,
		"threshold":100,
		"verbose":False,
		"regmods":False,
		"filemods":False,
		"childprocs":False,
		"netconns":False,
		"crossprocs":False,
		"help":False
	}

	# check caller
	if args[0] == "jetfreq.py":
		args = args[1:len(args)]
	else:
		raise IncorrectModuleError(args[0])

	# check for no args
	if len(args) == 0:
		raise jfexceptions.NoArgsError("jetfreq.py requires arguments")

	# check for help flag
	if args[0] == "-h":
		if len(args) > 1:
			raise jfexceptions.IncorrectUsageError(" ".join(args))
		else:
			params["help"] = True
			return params

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
					if flags[a]:
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
				if flags[a]:
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
					raise jfexceptions.IncorrectUsageError(" ".join(args))
	
	# import server name and api_key
	params = import_conf(params)
	if params['server'] == None or len(params['server']) == 0 or params['key'] == None or len(params['key']) == 0:
		raise MissingConfigurationError()

	return params

def get_event_paths(events, col):
	paths = []
	for event in events:
		paths.append(event.split('|')[col])
	return paths
