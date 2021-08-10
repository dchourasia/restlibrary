import requests
from .libcommons import libcommons
from .data_manager import data_manager
import traceback, json, os, time
from datetime import datetime

class request_processor:

    def Process_Http_Request(self, _requestInfo):
        try:
            if _requestInfo.method == "GET":
                _requestInfo.response = requests.get(_requestInfo.url, headers=_requestInfo.requestHeaders, timeout=_requestInfo.timeout)
            elif _requestInfo.method == "HEAD":
                _requestInfo.response = requests.head(_requestInfo.url, headers=_requestInfo.requestHeaders, timeout=_requestInfo.timeout)
            elif _requestInfo.method == "POST":
                _requestInfo.response = requests.post(_requestInfo.url, headers=_requestInfo.requestHeaders, data=_requestInfo.requestBody, files=_requestInfo.files, timeout=_requestInfo.timeout)
            elif _requestInfo.method == "PUT":
                _requestInfo.response = requests.put(_requestInfo.url, headers=_requestInfo.requestHeaders, data=_requestInfo.requestBody, files=_requestInfo.files, timeout=_requestInfo.timeout)
            elif _requestInfo.method == "PATCH":
                _requestInfo.response = requests.patch(_requestInfo.url, headers=_requestInfo.requestHeaders, data=_requestInfo.requestBody, files=_requestInfo.files, timeout=_requestInfo.timeout)
            elif _requestInfo.method == "DELETE":
                _requestInfo.response = requests.delete(_requestInfo.url, headers=_requestInfo.requestHeaders, data=_requestInfo.requestBody, files=_requestInfo.files, timeout=_requestInfo.timeout)

            try:
                if _requestInfo.response.json():
                    if not _requestInfo.responseDataType.lower() == 'file':
                        data_manager.responseStore[_requestInfo.requestId] = _requestInfo.response.json()
                        _requestInfo.responseBody = json.dumps(_requestInfo.response.json(), indent=4)
                        libcommons.run_keyword("log", "${_requestInfo.responseBody}")
                    else:
                        _requestInfo = self.download_file(_requestInfo)
            except:
                if _requestInfo.response.text and _requestInfo.responseDataType.lower() == 'file':
                    _requestInfo = self.download_file(_requestInfo)
                elif _requestInfo.response.text:
                    _requestInfo.responseBody = _requestInfo.response.text
                    libcommons.run_keyword("log", "${_requestInfo.responseBody}")


            data_manager.headerStore[_requestInfo.requestId] = _requestInfo.response.headers
            _requestInfo.responseHeaders = json.dumps(dict(_requestInfo.response.headers), indent=4)
            libcommons.run_keyword("log", "${_requestInfo.responseHeaders}")

            _requestInfo.responseStatusCode = _requestInfo.response.status_code
            libcommons.run_keyword("log", "${_requestInfo.responseStatusCode}")

        except Exception as e:
            print(traceback.format_exc())
            raise e
        return _requestInfo

    def download_file(self, _requestInfo):
        downloadFilePathFound = True
        try:
            if (_requestInfo.downloadFilePath):
                fileDir = os.path.dirname(_requestInfo.downloadFilePath)
                if os.path.exists(fileDir) and os.path.isdir(fileDir):
                    if os.path.exists(_requestInfo.downloadFilePath) and os.path.isfile(_requestInfo.downloadFilePath):
                        os.remove(_requestInfo.downloadFilePath)
                else:
                    downloadFilePathFound = False
        except Exception as e:
            print('could not download file on the given downloadFilePath')
            print(str(e))
            downloadFilePathFound = False

        if not _requestInfo.downloadFilePath or not downloadFilePathFound:
            _requestInfo.downloadFilePath = os.path.join(os.getcwd(),
                                                         str(datetime.now().strftime('%d%m%y%H%M%S%f')))

        open(_requestInfo.downloadFilePath, 'wb').write(_requestInfo.response.content)

        _requestInfo.responseBody = _requestInfo.downloadFilePath
        libcommons.run_keyword("log", "${_requestInfo.responseBody}")
        return _requestInfo