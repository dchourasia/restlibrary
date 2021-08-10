from .libcommons import libcommons
import os
import json, traceback
from .JsonCompareEx import compareEx
from .data_manager import data_manager
from robot.errors import ExecutionFailed
from .JSONSchemaValidator import JSONSchemaValidator

verificationLib = "verification_manager"
ResponseBodyVerificationFailureError = 'Response body verification failed'
ResponseHeaderVerificationFailureError = 'Response header verification failed'
StatusCodeVerificationFailureError = 'Status code verification failed'
ResponseSchemaVerificationFailureError = 'JSON Schema verification failed'

class verification_manager:

    def Verify_Response_Against_Baselines(self, requestInfo):
        try:
            try:
                libcommons.run_keyword('Verify Status Code', requestInfo)
            except ExecutionFailed as err:
                raise Exception([err])

            exceptions = []
            if requestInfo.expectedResponseBody:
                try:
                    libcommons.run_keyword('Verify Response Body', requestInfo)
                except ExecutionFailed as err: #this except block is same as "Run Keyword And Continue On Failure"
                    if not err.dont_continue:
                        err.continue_on_failure = True
                    #raise err
                    exceptions.append(err)

            if requestInfo.expectedResponseSchema:
                try:
                    libcommons.run_keyword('Verify JSON Schema', requestInfo)
                except ExecutionFailed as err: #this except block is same as "Run Keyword And Continue On Failure"
                    if not err.dont_continue:
                        err.continue_on_failure = True
                    #raise err
                    exceptions.append(err)

            if len(requestInfo.expectedResponseHeaders):
                try:
                    libcommons.run_keyword('Verify Response Headers', requestInfo)
                except ExecutionFailed as err: #this except block is same as "Run Keyword And Continue On Failure"
                    if not err.dont_continue:
                        err.continue_on_failure = True
                    #raise err
                    exceptions.append(err)
            if len(exceptions):
                raise Exception(exceptions)
        except Exception as e:
            if set([str(x) for x in e.args[0]]).issubset(set([ResponseBodyVerificationFailureError, ResponseHeaderVerificationFailureError, StatusCodeVerificationFailureError, ResponseSchemaVerificationFailureError])):
                print([str(x) for x in e.args[0]])
            else:
                print(traceback.format_exc())
            raise e
        return requestInfo

    def Verify_JSON_Schema(self, requestInfo):
        try:
            if type(requestInfo.expectedResponseSchema) is str and libcommons.path_exists(requestInfo.expectedResponseSchema):
                requestInfo.expectedResponseSchema = open(requestInfo.expectedResponseSchema).read()
            libcommons.run_keyword('log', "${requestInfo.expectedResponseSchema}")
            requestInfo.schemaDiffList = JSONSchemaValidator.ValidateSchema(requestInfo.expectedResponseSchema, requestInfo.responseBody)

            if len(requestInfo.schemaDiffList):
                libcommons.run_keyword('Check If JSON Schema Verification Is Successful', requestInfo)
        except Exception as e:
            if str(e) == ResponseSchemaVerificationFailureError:
                print(str(e))
            else:
                print(traceback.format_exc())
            raise e

    def Check_If_JSON_Schema_Verification_Is_Successful(self, requestInfo):
            print('Total ', len(requestInfo.schemaDiffList), ' schema difference(s) found, below are the details:')
            requestInfo.schemaDiffList = json.dumps(requestInfo.schemaDiffList, indent=4)
            print(requestInfo.schemaDiffList)
            raise Exception(ResponseSchemaVerificationFailureError)

    def Verify_Status_Code(self, requestInfo):
        try:
            libcommons.run_keyword("should be equal as strings", requestInfo.response.status_code, requestInfo.expectedStatusCode)
        except Exception as e:
            raise Exception(StatusCodeVerificationFailureError)

    def Verify_Response_Body(self, requestInfo):
        try:
            if type(requestInfo.expectedResponseBody) is str and libcommons.path_exists(requestInfo.expectedResponseBody):
                requestInfo.expectedResponseBody = open(requestInfo.expectedResponseBody).read()
            if requestInfo.responseDataType == 'json':
                requestInfo.expectedResponseBody = data_manager.process_data(requestInfo.expectedResponseBody, 'json')
                libcommons.run_keyword('log', "${requestInfo.expectedResponseBody}")
                requestInfo.diffList = compareEx(requestInfo.expectedResponseBody, requestInfo.responseBody, comparisionType=requestInfo.responseVerificationType, verificationScheme=requestInfo.verificationScheme, ignoreNodes=requestInfo.ignoreNodes)
                if len(requestInfo.diffList):
                    libcommons.run_keyword('Check If ResponseBody Verification Is Successful', requestInfo)


            elif requestInfo.responseDataType == 'text':
                requestInfo.expectedResponseBody = data_manager.process_data(requestInfo.expectedResponseBody)
                if not requestInfo.expectedResponseBody == requestInfo.responseBody:
                    libcommons.run_keyword('Check If ResponseBody Verification Is Successful', requestInfo)
        except Exception as e:
            if str(e) == ResponseBodyVerificationFailureError:
                print(str(e))
            else:
                print(traceback.format_exc())
            raise e



    def Check_If_ResponseBody_Verification_Is_Successful(self, requestInfo):
            if requestInfo.responseDataType == 'json':
                print('Total ', len(requestInfo.diffList), ' difference(s) found between response and baseline, below are the details:')
                requestInfo.diffs = json.dumps(requestInfo.diffList, indent=4)
            elif requestInfo.responseDataType == 'text':
                print('Expected and actual response did not match, below are the details:')
                requestInfo.diffs = json.dumps({"type" : "Value Mismatch", "expected" : requestInfo.expectedResponseBody, "actual" : requestInfo.responseBody})
            print(requestInfo.diffs)
            raise Exception(ResponseBodyVerificationFailureError)

    def Verify_Response_Headers(self, requestInfo):
        try:
            requestInfo.expectedResponseHeaders = data_manager.process_data(requestInfo.expectedResponseHeaders, 'json')
            libcommons.run_keyword('log', "${requestInfo.expectedResponseHeaders}")
            requestInfo.headersDiffList = compareEx(requestInfo.expectedResponseHeaders, requestInfo.responseHeaders, comparisionType='Partial')
            if len(requestInfo.headersDiffList):
                libcommons.run_keyword('Check If ResponseHeader Verification Is Successful', requestInfo)
        except Exception as e:
            if str(e) == ResponseHeaderVerificationFailureError:
                print(str(e))
            else:
                print(traceback.format_exc())
            raise e


    def Check_If_ResponseHeader_Verification_Is_Successful(self, requestInfo):
            print('Total ', len(requestInfo.headersDiffList), ' difference(s) found between response headers and baseline, below are the details:')
            requestInfo.headersDiffList = json.dumps(requestInfo.headersDiffList, indent=4)
            print(requestInfo.headersDiffList)
            raise Exception(ResponseHeaderVerificationFailureError)






