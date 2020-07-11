#!/path/to/python

import json
import sys
import jfexceptions
import jfutil
import jfnet
import jfanalyze
import jfparser

try:	
	if __name__ == "__main__":
		params = jfparser.process_params(sys.argv)
	else:
		raise jfexceptions.IncorrectModuleError(__name__)
	
	# check for help flag
	if params['help'] == True:
		jfutil.show_help()
		exit()

#FIXME : FIXME : Disabling by_modload for the time being : FIXME : FIXME 
	if params['by_modload'] == True:
		jfutil.debug(True, "Sorry, the by_modload feature (-m) is still under development")
		exit()
#FIXME : FIXME : FIXME : FIXME : FIXME : FIXME : FIXME : FIXME : FIXME
	
	jfutil.debug(params['verbose'], 'Parameters parsed as {}'.format(params))
	
	# check that param combinations are valid
	if params['by_modload']	 == True:
		if params['regmods'] == True or params['filemods'] == True or params['childprocs'] == True or params['netconns'] == True or params['crossprocs']:
			flags = ''
			if params['regmods'] == True:
				flags += 'r'
			if params['filemods'] == True:
				flags += 'f'
			if params['childprocs'] == True:
				flags += 'c'
			if params['netconns'] == True:
				flags += 'd'
			if params['crossprocs'] == True:
				flags += 'x'
			raise jfexceptions.FlagsNotApplicableError('by_modload', flags)
	
	jfutil.debug(True, 'Parameters loaded. Searching for {} {}.'.format('modload' if params['by_modload'] == True else 'process', params['search_name']))
	
	# get the data for the process or modload	
	data = None
	if params['by_modload'] == False:
		data = jfnet.get_data_for_process(params)
	else:
		data = jfnet.get_data_for_modload(params)
	
	# calculate the frequencies of each event type
	event_freqs = jfanalyze.analyze_by_process(params, data) if params['by_modload'] == False else jfanalyze.analyze_by_modload(params, data)
	
	# dump or write
	if params['write_file'] == True:
		file_path = jfutil.out_file_by_process(params, event_freqs) if params['by_modload'] == False else jfutil.out_file_by_modload(params, event_freqs)
	else:
		report = jfutil.format_report_by_process(params, event_freqs) if params['by_modload'] == False else jfutil.format_report_by_modload(params, event_freqs)
		jfutil.debug(True, report)

except jfexceptions.IncorrectUsageError as err:
	jfutil.debug(True, "Incorrect usage at argument: {}".format(err.context))
	jfutil.show_usage()
except jfexceptions.IncorrectModuleError as err:
	jfutil.debug(True, "{} is the incorrect module".format(err.module))
except jfexceptions.NoArgsError as err:
	jfutil.debug(True, err.message)
	jfutil.show_usage()
except jfexceptions.NoSuchArgumentError as err:
	jfutil.debug(True, "No such argument: {}".format(err.flag))
	jfutil.show_usage()
except jfexceptions.MissingValueError as err:
	jfutil.debug(True, "Flag \'{}\' ({}) requires a value".format(err.flag, err.name))
	jfutil.show_usage()
except jfexceptions.FlagsNotApplicableError as err:
	jfutil.debug(True, "Flags -{} not applicable in {} mode".format(err.flags, err.mode))
	jfutil.show_usage()
except jfexceptions.DoubleArgumentError as err:
	jfutil.debug(True, "Flag -{} not allowed twice".format(err.flag))
	jfutil.show_usage()
except jfexceptions.MissingConfigurationError as err:
	jfutil.debug(True, err.message)
except jfexceptions.UnexpectedResponseError as err:
	jfutil.debug(True, "The JSON returned had an unexpected format:\n{}".format(err.data))
except jfexceptions.NoResultsError as err:
	jfutil.debug(True, "There were no results for query \'{}\'".format(err.query))
except jfexceptions.NoEventsFoundError as err:
	jfutil.debug(True, "There were no events found for process returned by query \'{}\'".format(err.query))
