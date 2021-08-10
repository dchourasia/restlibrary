from .rest_keywords import rest_keywords
from .input_generator import input_generator
from .session_manager import session_manager
from .request_processor import request_processor
from .verification_manager import verification_manager
from .version import VERSION
__version__ = VERSION

class RESTLibrary(rest_keywords, input_generator, session_manager, request_processor, verification_manager):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__
