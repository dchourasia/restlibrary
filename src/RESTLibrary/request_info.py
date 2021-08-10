from .libcommons import libcommons
from .data_manager import data_manager

import traceback, json

class request_info:
    def Create_Request_Info(self, requestId, url, method, requestHeaders, requestBody, authType, requestDataType, responseDataType, expectedStatusCode, expectedResponseBody, username, password, files, responseVerificationType, expectedResponseHeaders, expectedResponseSchema, verificationScheme, username_var, password_var, downloadFilePath, timeout, ignoreNodes):
        try:
            self.requestId = data_manager.process_data(requestId)
            self.url = url
            self.method = method.upper()
            if type(requestHeaders) is str:
                requestHeaders = json.loads(requestHeaders)
            self.requestHeaders = requestHeaders
            self.requestBody = requestBody
            self.requestBodyFilePath = requestBody
            self.authType = authType.replace('\\', '/').strip()
            self.requestDataType = requestDataType
            self.responseDataType = responseDataType
            self.expectedStatusCode = expectedStatusCode
            self.expectedResponseBody = expectedResponseBody
            self.expectedResponseHeaders = expectedResponseHeaders
            self.expectedResponseSchema = expectedResponseSchema
            self.verificationScheme = verificationScheme if type(verificationScheme) is list else json.load(open(verificationScheme)) if libcommons.path_exists(verificationScheme) else json.loads(verificationScheme)
            self.responseVerificationType = responseVerificationType.lower()
            self.username = username
            self.password = password
            self.username_var = username_var
            self.password_var = password_var
            self.files = files
            self.downloadFilePath = downloadFilePath
            self.timeout = float(timeout) if timeout is not None else timeout
            self.ignoreNodes = ignoreNodes
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return self


