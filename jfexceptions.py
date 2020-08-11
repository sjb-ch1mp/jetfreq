# THIS MODULE CONTAINS ALL THE DEFINED EXCEPTIONS FOR JETFREQ.PY
class Error(Exception):
	pass

# EXCEPTION FOR THE INCORRECT USAGE OF FLAGS
class IncorrectUsageError(Error):
	def __init__(self, context):
		self.context = context

# EXCEPTION FOR JETFREQ.PY BEING USED WITHOUT ANY ARGUMENTS
class NoArgsError(Error):
	def __init__(self, message):
		self.message = message

# EXCEPTION FOR AN UNDEFINED FLAG BEING USED
class NoSuchArgumentError(Error):
	def __init__(self, flag):
		self.flag = flag

# EXCEPTION FOR A PARAMETERIZED FLAG BEING USED WITHOUT A VALUE
class MissingValueError(Error):
	def __init__(self, flag, name):
		self.flag = flag
		self.name = name

# EXCEPTION FOR A FLAG BEING USED MORE THAN ONCE
class DoubleArgumentError(Error):
	def __init__(self, flag):
		self.flag = flag

# EXCEPTION FOR A FLAG THAT IS NOT APPLICABLE IN THE GIVEN MODE
class FlagsNotApplicableError(Error):
	def __init__(self, mode, flags):
		self.mode = mode
		self.flags = flags

# CATCH ALL EXCEPTION FOR AN ERROR FROM THE CARBON BLACK API
class APIQueryError(Error):
	def __init__(self, message):
		self.message = message

# EXCEPTION FOR MISSING PARAMETERS IN THE JETFREQ CONFIGURATION FILE
class MissingConfigurationError(Error):
	def __init__(self):
		self.message = "You need to configure jetfreq by adding the Carbon Black Server name and API Key to ./conf/jetfreq.cfg"

# EXCEPTION FOR A JSON FORMAT THAT IS NOT EXPECTED (E.G. MISSING KEY)
class UnexpectedResponseError(Error):
	def __init__(self, data):
		self.data = data

# EXCEPTION FOR NO RESULTS BEING RETURNED FOR A QUERY
class NoResultsError(Error):
	def __init__(self, query):
		self.query = query

# EXCEPTION FOR NO EVENTS BEING FOUND FOR A QUERY
class NoEventsFoundError(Error):
	def __init__(self, query):
		self.query = query

# EXCEPTION FOR --BY-PROCESS OR --COMPARE-PROCESS MODE MISSING EVENT TYPE FLAGS
class ProcessModeMissingEventTypeError(Error):
	def __init__(self, mode):
		self.mode = mode

# EXCEPTION FOR --COMPARE-PROCESS OR --COMPARE-EVENT MODE MISSING A SAMPLE FILE PATH
class CompareModeMissingSampleFileError(Error):
	def __init__(self, mode):
		self.mode = mode

# EXCEPTION FOR THE THRESHOLD FLAGS BEING USED INCORRECTLY
class IncorrectUseOfThresholdError(Error):
	def __init__(self, threshold):
		self.threshold = threshold

# EXCEPTION FOR A FLAG BEING USED THAT IS NOT APPLICABLE FOR THE GIVEN MODE
class IncorrectFlagUsageForModeError(Error):
	def __init__(self, mode, flags):
		self.mode = mode
		self.flags = flags

# EXCEPTION FOR --BY-EVENT OR --COMPARE-EVENT MODE MISSING A MANDATORY FLAG
class ByEventModeFlagRequiredError(Error):
	def __init__(self, mode):
		self.mode = mode

# EXCEPTION FOR THE WRONG KIND OF SAMPLE FILE BEING IMPORTED FOR --COMPARE MODES
class IncorrectSampleForModeError(Error):
	def __init__(self, file_path, mode):
		self.file_path = file_path
		self.mode = mode

# EXCEPTION FOR NO DIFFERENCES BEING FOUND BETWEEN SAMPLES FOR --COMPARE MODES
class NoDiffsFoundError(Error):
	def __init__(self, target_event, sample):
		self.target_event = target_event
		self.sample = sample

# EXCEPTION FOR EQUAL THRESHOLD VALUES (E.G. -t 50 -T 50)
class NonsensicalThresholdValuesError(Error):
	def __init__(self, greater_than, less_than):
		self.greater_than = greater_than
		self.less_than = less_than
