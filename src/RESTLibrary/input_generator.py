from .data_manager import data_manager
from .libcommons import libcommons
from .session_manager import session_manager
import json
import traceback

class input_generator:
    def Generate_Request_Body(self, _requestInfo):
        #in case of files requestbody is expected as dict (by requestlib) and in other cases it expects string
        try:
            contentType = 'str'
            if isinstance(_requestInfo.requestBodyFilePath, str) and _requestInfo.requestBodyFilePath.startswith(data_manager.openingChars) and _requestInfo.requestBodyFilePath.endswith(data_manager.closingChars):
                _requestInfo.requestBodyFilePath = data_manager.process_data(_requestInfo.requestBodyFilePath)

            if isinstance(_requestInfo.requestBodyFilePath, str) and libcommons.path_exists(_requestInfo.requestBodyFilePath):
                with open(_requestInfo.requestBodyFilePath) as inputFile:
                    _requestInfo.requestBody = inputFile.read()
                _requestInfo.requestBody = data_manager.process_data(_requestInfo.requestBody, _requestInfo.requestDataType)
            elif _requestInfo.requestDataType.lower() == 'file':
                _requestInfo.requestBody = data_manager.process_data(_requestInfo.requestBodyFilePath, 'json' if data_manager.isJson(_requestInfo.requestBodyFilePath) else 'str',  _requestInfo.requestDataType)
                _requestInfo.files = data_manager.process_data(_requestInfo.files, 'json',  _requestInfo.requestDataType)
            else:
                if isinstance(_requestInfo.requestBodyFilePath, dict):
                    _requestInfo.requestBodyFilePath = json.dumps(_requestInfo.requestBodyFilePath)
                _requestInfo.requestBody = data_manager.process_data(_requestInfo.requestBodyFilePath, _requestInfo.requestDataType)
                _requestInfo.requestBodyFilePath = ""
            libcommons.run_keyword('log', "${_requestInfo.requestBody}")
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return _requestInfo

    def Generate_Request_Headers(self, _requestInfo):
        try:
            for name, value in _requestInfo.requestHeaders.items():
                _requestInfo.requestHeaders[name] = data_manager.process_data(value)
            libcommons.run_keyword('log', "${_requestInfo.requestHeaders}")
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return _requestInfo

    def Process_Files_To_Upload(self, _requestInfo):
        try:
            for k, v in _requestInfo.files.items():
                if isinstance(v, str) :
                    v = libcommons.sanitizeFilePath(v)
                    if libcommons.path_exists(v):
                        with open(v, 'rb') as f:
                            _requestInfo.files[k] = bytes(f.read())
                        libcommons.run_keyword('Log', 'Successfully added file ' + v)
                    else:
                        raise Exception('FILE NOT FOUND ', v)
                elif isinstance(v, (tuple, list)) and len(v) > 1 :
                    v[1] = libcommons.sanitizeFilePath(v[1])
                    if libcommons.path_exists(v[1]):
                        with open(v[1], 'rb') as f:
                            v[1] = bytes(f.read())
                        _requestInfo.files[k] = v
                        libcommons.run_keyword('Log', 'Successfully added file ' + v[0])
                    else:
                        raise Exception('FILE NOT FOUND ', v[1])

        except Exception as e:
            print(traceback.format_exc())
            raise e
        return _requestInfo



    def Generate_Url(self, _requestInfo):
        try:
            _requestInfo.url = data_manager.process_data(_requestInfo.url)
            libcommons.run_keyword('log', "${_requestInfo.url}")
        except Exception as e:
            print(traceback.format_exc())
            raise e

        return _requestInfo

    def Generate_HTTP_Request(self, _requestInfo):
        inpLib = "input_generator"
        sessionLib = "session_manager"

        try:
            _requestInfo = libcommons.run_keyword('Generate Url', "${_requestInfo}")

            _requestInfo = libcommons.run_keyword('Process Authentication', "${_requestInfo}")

            if _requestInfo.requestHeaders.__len__():
                _requestInfo = libcommons.run_keyword('Generate Request Headers', "${_requestInfo}")

            if len(_requestInfo.files):
                _requestInfo = libcommons.run_keyword('Process Files To Upload', "${_requestInfo}")

            if _requestInfo.requestBody or _requestInfo.requestBodyFilePath or len(_requestInfo.files):
                _requestInfo = libcommons.run_keyword('Generate Request Body', "${_requestInfo}")


        except Exception as e:
            print(traceback.format_exc())
            raise e
        return _requestInfo



