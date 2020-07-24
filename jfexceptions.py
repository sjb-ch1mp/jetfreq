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

class DoubleArgumentError(Error):
	def __init__(self, flag):
		self.flag = flag

class FlagsNotApplicableError(Error):
	def __init__(self, mode, flags):
		self.mode = mode
		self.flags = flags

class APIQueryError(Error):
	def __init__(self, message):
		self.message = message

class MissingConfigurationError(Error):
	def __init__(self):
		self.message = "You need to configure jetfreq by adding the Carbon Black Server name and API Key to ./conf/jetfreq.cfg"

class UnexpectedResponseError(Error):
	def __init__(self, data):
		self.data = data

class NoResultsError(Error):
	def __init__(self, query):
		self.query = query

class NoEventsFoundError(Error):
	def __init__(self, query):
		self.query = query

class ProcessModeMissingEventTypeError(Error):
	def __init__(self, mode):
		self.mode = mode

class CompareModeMissingSampleFileError(Error):
	def __init__(self, mode):
		self.mode = mode

class IncorrectUseOfThresholdError(Error):
	def __init__(self, threshold):
		self.threshold = threshold

class IncorrectFlagUsageForModeError(Error):
	def __init__(self, mode, flags):
		self.mode = mode
		self.flags = flags

class ByEventModeFlagRequiredError(Error):
	def __init__(self, mode):
		self.mode = mode

class IncorrectSampleForModeError(Error):
	def __init__(self, file_path, mode):
		self.file_path = file_path
		self.mode = mode

class NoDiffsFoundError(Error):
	def __init__(self, target_event, sample):
		self.target_event = target_event
		self.sample = sample
