import json
import sys

## Exceptions

class Error(Exception):
	pass

class IncorrectUsageError(Error):
	def __init__(self, context):
		self.context = context

class IncorrectModuleError(Error):
	def __init__(self, module):
		self.module = module

class NoArgsError(Error):
	def __init__(self, message):
		self.message = message

class NoSuchArgumentError(Error):
	def __init__(self, flag):
		self.flag = flag

class MissingValueError(Error):
	def __init__(self, flag, name):
		self.flag = flag
		self.name = name

## Functions

def show_usage():
	print("\n== USAGE ==\nby process:\tpython jetfreq.py process_name -u user_name -s start_time -w output_file -n sample_size -t threshold -vrfcd")
	print("by modload:\tpython jetfreq.py dll_name -u user_name -s start_time -w output_file -n sample_size -t threshold -vm")
	print("show help:\tpython jetfreq.py -h")

def process_param_str(args):

	flags = {
		"u":{"name":"user_name","param":True,"exclusive":False},
		"s":{"name":"start_time","param":True,"exclusive":False},
		"w":{"name":"write_file","param":True,"exclusive":False},
		"n":{"name":"sample_size","param":True,"exclusive":False},
		"t":{"name":"threshold","param":True,"exclusive":False},
		"v":{"name":"verbose","param":False,"exclusive":False},
		"r":{"name":"regmods","param":False,"exclusive":False},
		"f":{"name":"filemods","param":False,"exclusive":False},
		"c":{"name":"childprocs","param":False,"exclusive":False},
		"d":{"name":"netconns","param":False,"exclusive":False},
		"m":{"name":"by_modload","param":False,"exclusive":False},
		"h":{"name":"help","param":False,"exclusive":True}
	}

	params = {
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
		"help":False
	}

	# check caller
	if args[0] == "jetfreq.py":
		args = args[1:len(args)]
	else:
		raise IncorrectModuleError(args[0])
	
	# check for no args
	if len(args) == 0:
		raise NoArgsError("jetfreq.py requires arguments")

	# check for help flag
	if args[0] == "-h":
		if len(args) > 1:
			raise IncorrectUsageError(" ".join(args))
		else:
			params["help"] = True
			return params
	
	# get search name
	if args[0].startswith('-'):
		raise IncorrectUsageError(" ".join(args))
	else:
		params['search_name'] = args[0]
		args = args[1:len(args)]

	# process args
	while len(args) > 0:
		if not args[0].startswith('-'):
			raise IncorrectUsageError(" ".join(args))
		else:
			# process clustered flags
			if len(args[0][1:len(args[0])]) > 1:
				cluster = args[0][1:len(args[0])]
				# print("CLUSTER = {}".format(cluster))
				for a in cluster:
					# print("...processing flag {}".format(a))
					if flags[a]:
						if a == 'h':
							raise IncorrectUsageError(" ".join(args))
						elif flags[a]['param'] == True:
							raise IncorrectUsageError(" ".join(args))
						else:
							params[flags[a]['name']] = True
					else:
						raise NoSuchArgumentError(a)
				args = args[1:len(args)]
			else:
				a = args[0][1:len(args[0])]
				if flags[a]:
					# process flags with params
					if flags[a]['param'] == True:
						if len(args) > 1:
							if args[1].startswith('-') and not flags[a]['name'] == 'start_time':
								raise MissingValueError(a, flags[a]['name'])
							else:								
								params[flags[a]['name']] = args[1]
						else:
							raise MissingValueError(a, flags[a]['name'])
						args = args[2:len(args)]
					# process flags without params
					else:
						if len(args) > 1 and not args[1].startswith('-'):
							raise IncorrectUsageError(" ".join(args))
						else:
							params[flags[a]['name']] = args[0]
						args = args[1:len(args)]
				else:
					raise IncorrectUsageError(" ".join(args))
	return params

## Main

try:
	params = process_param_str(sys.argv)
	
	# check for help flag
	if params['help'] == True:
		show_usage()
		exit()
	
	# check that param combinations are valid

	print(params)

except IncorrectUsageError as err:
	print("Incorrect usage at argument: {}".format(err.context))
except IncorrectModuleError as err:
	print("Module {} does not receive arguments".format(err.module))
except NoArgsError as err:
	print(err.message)
except NoSuchArgumentError as err:
	print("No such argument: {}".format(err.flag))
except MissingValueError as err:
	print("Flag \'{}\' ({}) requires a value".format(err.flag, err.name))