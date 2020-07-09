#################################################
#################################################
# ________     _____________                    #
# ______(_)______  /___  __/_________________ _ #
# _____  /_  _ \  __/_  /_ __  ___/  _ \  __ `/ #
# ____  / /  __/ /_ _  __/ _  /   /  __/ /_/ /  #
# ___  /  \___/\__/ /_/    /_/    \___/\__, /   #
# /___/                                  /_/    #
#                                               #
#      @author: samuel.brookes@aph.gov.au       #
#                                               #
#################################################
#################################################

import json
import sys
import jfexceptions
import jfutil
import jfnet
import jfanalyze

try:
        params = jfutil.process_params(sys.argv)
        jfutil.debug(params['verbose'], 'Parameters parsed as {}'.format(params))

        # check for help flag
        if params['help'] == True:
                jfutil.show_help()
                exit()

        # check that param combinations are valid
        if params['by_modload']  == True:
                if params['regmods'] == True or params['filemods'] == True or params['childprocs'] == True or params['netconns'] == True:
                        flags = ''
                        if params['regmods'] == True:
                                flags += 'r'
                        if params['filemods'] == True:
                                flags += 'f'
                        if params['childprocs'] == True:
                                flags += 'c'
                        if params['netconns'] == True:
                                flags += 'd'
                        raise jfexceptions.FlagsNotApplicableError('by_modload', flags)

        jfutil.debug(params['verbose'], 'Parameters loaded. Searching for {} {}.'.format('modload' if params['by_modload'] == True else 'process', params['search_name']))

        # get the data for the process or modload
        data = None
        if params['by_modload'] == False:
                data = jfnet.get_data_for_process(params)
        else:
                data = jfnet.get_data_for_modload(params)

        # write to file or dump to stdout
#       if params['write_file'] != None:
#               jfutil.out_file(data, params)
#       else:
#               print(format_report(data, params))

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
