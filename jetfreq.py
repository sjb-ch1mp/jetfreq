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
		raise jfexceptions.IncorrectModuleError()
	
	# check for help flag
	if params['mode'] == 'SHOW_HELP':
		jfutil.show_help()
		exit()
	
	jfutil.debug(params['verbose'], "Running in {} mode".format(params['mode']))	
	jfutil.debug(params['verbose'], 'Parameters parsed as {}'.format(params))
	
	
	banner = ["      _     __  ___            ","     (_)__ / /_/ _/______ ___ _",
		"    / / -_) __/ _/ __/ -_) _ `/"," __/ /\__/\__/_//_/  \__/\_, /",
		"|___/                     /_/"]
	jfutil.debug(True, banner)

	# get the data for the process or modload	
	representative_sample = None
	target_sample = None
	data = None
	event_freqs = None
	if params['mode'] == 'BY_PROCESS':
		jfutil.debug(True if params['verbose'] == False else False, 'Fetching data from {}'.format(params['server']))
		data = jfnet.get_data_for_process(params)
		jfutil.debug(True if params['verbose'] == False else False, 'Analyzing the search results')
		event_freqs = jfanalyze.analyze_by_process(params, data)
	elif params['mode'] == 'BY_EVENT':
		jfutil.debug(True if params['verbose'] == False else False, 'Fetching data from {}'.format(params['server']))
		data = jfnet.get_data_for_event(params)
		jfutil.debug(True if params['verbose'] == False else False, 'Analyzing the search results')
		event_freqs = jfanalyze.analyze_by_event(params, data)
	elif params['mode'] == 'COMPARE_PROCESS':
		jfutil.debug(True if params['verbose'] == False else False, 'Importing the sample file')
		representative_sample = jfutil.import_sample(params)
		jfutil.debug(True if params['verbose'] == False else False, 'Fetching data from {}'.format(params['server']))
		target_sample = jfnet.get_data_for_process(params)
		jfutil.debug(True if params['verbose'] == False else False, 'Analyzing the search results')
		target_sample = jfanalyze.analyze_by_process(params, target_sample)
		jfutil.debug(True if params['verbose'] == False else False, 'Comparing results to sample file')
		event_freqs = jfanalyze.compare_process(params, representative_sample, target_sample)
	elif params['mode'] == 'COMPARE_EVENT':
		jfutil.debug(True if params['verbose'] == False else False, 'Importing the sample file')
		representative_sample = jfutil.import_sample(params)
		jfutil.debug(True if params['verbose'] == False else False, 'Fetching data from {}'.format(params['server']))
		target_sample = jfnet.get_data_for_event(params)
		jfutil.debug(True if params['verbose'] == False else False, 'Analyzing the search results')
		target_sample = jfanalyze.analyze_by_event(params, target_sample)
		jfutil.debug(True if params['verbose'] == False else False, 'Comparing results to sample file')
		event_freqs = jfanalyze.compare_event(params, representative_sample, target_sample)
	
	# dump or write
	if params['write_file'] == True:
		file_path = None
		if params['mode'] == 'BY_PROCESS':
			file_path = jfutil.out_file_by_process(params, event_freqs)
		elif params['mode'] == 'BY_EVENT':
			file_path = jfutil.out_file_by_event(params, event_freqs)
		elif params['mode'] == 'COMPARE_PROCESS':
			file_path = jfutil.out_file_compare_process(params, event_freqs)
		elif params['mode'] == 'COMPARE_EVENT':
			file_path = jfutil.out_file_compare_event(params, event_freqs)
		jfutil.debug(True, 'File successfully written to {}'.format(file_path))
	else:
		if params['mode'] == 'BY_PROCESS':
			report = jfutil.format_report_by_process(params, event_freqs)
		elif params['mode'] == 'BY_EVENT':
			report = jfutil.format_report_by_event(params, event_freqs)
		elif params['mode'] == 'COMPARE_PROCESS':
			report = jfutil.format_report_compare_process(params, event_freqs)
		elif params['mode'] == 'COMPARE_EVENT':
			report = jfutil.format_report_compare_event(params, event_freqs)
		jfutil.debug(True, report)

except jfexceptions.IncorrectUsageError as err:
	jfutil.debug(True, "Incorrect usage at argument: {}".format(err.context))
	jfutil.show_usage()
except jfexceptions.IncorrectModuleError as err:
	jfutil.debug(True, "Module {} does not receive arguments".format(err.module))
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
except jfexceptions.ProcessModeMissingEventTypeError as err:
	jfutil.debug(True, "{} mode requires an event type to be specified".format(err.mode))
	jfutil.show_usage()
except jfexceptions.IncorrectUseOfThresholdError as err:
	jfutil.debug(True, "Threshold parameter requires a comparator to be specified: {}".format(err.threshold))
	jfutil.show_usage()
except jfexceptions.IncorrectFlagUsageForModeError as err:
	jfutil.debug(True, "Mode {} can only take a single event type flag: {}".format(err.mode, err.flags))
	jfutil.show_usage()
except jfexceptions.ByEventModeFlagRequiredError as err:
	jfutil.debug(True, "Mode {} requires an event_type to be specified with an event_type flag, e.g. -m|f|c|d|r".format(err.mode))
	jfutil.show_usage()
except jfexceptions.IncorrectSampleForModeError as err:
	sample_mode = 'BY_EVENT' if err.mode == 'COMPARE_PROCESS' else 'BY_PROCESS'
	jfutil.debug(True, "The file {} contains data for a {} search, but jetfreq is being run in {} mode.".format(err.file_path, sample_mode, err.mode))
except jfexceptions.CompareModeMissingSampleFileError as err:
	jfutil.debug(True, 'Import file must be specified (-i) when running jetfreq in {} mode'.format(err.mode))
	jfutil.show_usage()
except jfexceptions.NoDiffsFoundError as err:
	jfutil.debug(True, 'Target sample ({}) and representative sample ({}) are the same'.format(err.target_event, err.sample))
