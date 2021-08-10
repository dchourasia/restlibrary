import json
import re
from .libcommons import libcommons
from jsonpath_ng.ext import parser
from .jsonpath import jsonpath
from .json_merge import json_merge
import sys, uuid
import traceback
import time
from datetime import datetime

from pathlib import Path
class data_manager:
    pathMap = {}
    statusStore = {}
    responseStore = {}
    headerStore = {}
    openingChars = '<<<'
    closingChars = '>>>'
    deleteNotifier = openingChars + 'DELETE' + closingChars


    DynamicMethodInvocationRegex = re.compile(r'(?<=' + openingChars + ')(.*?)(?=' + closingChars + ')')
    RobotVariablesResolutionRegex = re.compile(r'(?<=\${)(.*?)(?=})')
    deleteEscape = '___DELETE___'
    deleteNode = '___DELETE_Node___'
    def process_data(data, contentType='str', requestDataType='json'):
        try:
            strData = str(data)
            if contentType.lower() in ('json', 'str') and ((data_manager.openingChars in strData and data_manager.closingChars in strData) or "${" in strData):
                if contentType.lower() == 'json':
                    try:
                        if isinstance(data, str):
                            data = json.loads(data)
                    except:
                        data = data_manager.process_data(data, 'str', requestDataType)
                        if isinstance(data, str):
                            data = json.loads(data)

                    data = data_manager.processJsonData(data)
                    if not requestDataType == 'file':
                        data = json.dumps(data, indent=4)#always returns string in normal case, returns dict only when file upload
                elif contentType.lower() == 'str':
                    data = data_manager.resolveAllDynamicReferences(data)
                    try:
                        data = json.dumps(json.loads(data), indent=4)
                    except:
                        a=1

        except Exception as e:
            print(traceback.format_exc())
            raise e
        return data

    def processJsonData(data):
        type = data.__class__.__name__
        try:
            if type.lower() in ('dict', 'dotdict') :
                keysToBeDeleted = []
                for k, v in data.items():
                    if v.__class__.__name__ == 'list' or v.__class__.__name__ == 'dict':
                        data[k] = data_manager.processJsonData(v)
                    elif v.__class__.__name__ == 'str':
                        data[k] = data_manager.resolveAllDynamicReferences(v)
                        if data[k] == data_manager.deleteNode:
                            keysToBeDeleted.append(k)
                for k in keysToBeDeleted:
                    del data[k]
            elif type == 'list':
                for index, item in enumerate(data):
                    data[index] = data_manager.processJsonData(item)

            elif type == 'str':
                data = data_manager.resolveAllDynamicReferences(data)
            elif type == 'bytes':
                try:
                    strData = data.decode("utf-8")
                    strData = data_manager.resolveAllDynamicReferences(strData)
                    data = bytes(strData, encoding='utf-8')
                except Exception:
                    #print('attempt RC in case of file content is text based')
                    print(sys.exc_info())
                    a=1
        except Exception as e:
            print(traceback.format_exc())
            raise e

        return data

    def resolveAllDynamicReferences(data): # this should be invoked from everywhere
        try:
            if data:
                if "${" in data:
                    data = data_manager.updateRobotVariablesInBinaryData(data)

                    # first process for nonRC methods
                if data_manager.openingChars in data and data_manager.closingChars in data:
                    data = data.replace('\n', '')
                    data = data_manager.processResponseChannelization(data, 'rc')

                #now process rc methods
                if data_manager.openingChars in data and data_manager.closingChars in data:
                    data = data_manager.processResponseChannelization(data)

                #resolve deleteEscape
                if data_manager.deleteEscape in data:
                    data = data.replace(data_manager.deleteEscape, data_manager.openingChars + 'DELETE' + data_manager.closingChars)
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return data


    def processResponseChannelization(data, excludeMethod=None, skipFirstOpeningChar=False):
        try:
            if data_manager.openingChars in data and data_manager.closingChars in data:
                expectedMatches = 0
                matches = data_manager.DynamicMethodInvocationRegex.findall(data)
                if skipFirstOpeningChar:
                    matches = data_manager.DynamicMethodInvocationRegex.findall(data[data.index(data_manager.openingChars) + len(data_manager.openingChars):])
                else:
                    expectedMatches = data.count(data_manager.openingChars)
                if matches:
                    for match in matches:
                        methodName = match.split(',')[0].strip().lower()
                        if (excludeMethod and methodName != excludeMethod) or not excludeMethod:
                            processedData = data_manager.invokeMethod(match)
                            if processedData != None:
                                if processedData.__class__.__name__.lower() in ('list', 'dict', 'dotdict'):
                                    processedData = json.dumps(processedData)
                                data = data.replace(data_manager.openingChars + match + data_manager.closingChars, str(processedData))

                if expectedMatches > len(matches):
                    return data_manager.processResponseChannelization(data, excludeMethod=excludeMethod, skipFirstOpeningChar=True)
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return data

    def updateRobotVariablesInBinaryData(data):
        try:
            variables = libcommons.robotBuiltIn.get_variables()
            # print(variables.__len__())
            # for variable, value in variables.items():
            #     print(variable, ' == ', value)
            matches = data_manager.RobotVariablesResolutionRegex.findall(data)
            for match in matches:
                variable = '${' + match + '}'
                value = libcommons.get_variable(variable)
                if value != None:
                    data = data.replace(variable, str(value))
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return data

    def invokeMethod(DynamicMethodInvocationSignature):
        try:
            supportedMethods = {key.lower(): key for key in data_manager.__dict__}
            parts = DynamicMethodInvocationSignature.split(',')
            methodName = parts[0].strip().lower()
            result = None
            if methodName in supportedMethods:
                formattedParts = ["'''" + parts[i].strip().replace("'", r"\'") + "'''" for i in range(1, len(parts))]
                toBeEvaled = data_manager.__name__ + '.' + supportedMethods[methodName] + '(' + ','.join(formattedParts) + ')'
                print(toBeEvaled)
                result = eval(toBeEvaled)
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return  result


    def RC(*kwargs):
        result = None
        try:
            srcRequestId = kwargs[0]
            rcType = kwargs[1].lower()
            if rcType == 'body':
                expectedData = 'singleNodeValue' if len(kwargs) > 2 and '$' in kwargs[2] and not kwargs[2].strip().startswith('{') and not kwargs[2].strip().startswith('[') and not libcommons.path_exists(kwargs[2]) else 'entireResponseBody'
                jsonToBeParsed = data_manager.responseStore.get(srcRequestId)
                if expectedData == 'singleNodeValue':
                    jsonPath = kwargs[2]
                    try: #first try with ng
                        #jsonPathExpression = parse(jsonPath)
                        jsonPathExpression = parser.ExtentedJsonPathParser().parse(jsonPath.replace(' && ', ' & '))
                        matches = jsonPathExpression.find(jsonToBeParsed)
                        result = matches[0].value if matches.__len__() == 1 else ([match.value for match in matches] if matches.__len__() > 1 else None)
                        if result is not None:
                            print(result)
                        else:
                            print('No matches found for given json path, please review:', jsonPath)
                    except: #then with jsonpath
                        print('using jsonpath')
                        jsonPathExpression = jsonPath
                        matches = jsonpath(jsonToBeParsed, jsonPathExpression)
                        if isinstance(matches, list) and matches.__len__():
                            print(matches[0])
                            result = matches[0]
                        elif isinstance(matches, bool) and not matches:
                            print('No matches found for given json path, please review:', jsonPath)
                elif expectedData == 'entireResponseBody':
                    if len(kwargs) > 2:
                        jsonToBeMerged = kwargs[2]
                        if len(kwargs) > 3:
                            jsonToBeMerged = ','.join(kwargs[2:len(kwargs)])
                        if libcommons.path_exists(jsonToBeMerged):
                            jsonToBeMerged = open(libcommons.sanitizeFilePath(jsonToBeMerged)).read()
                        jsonToBeMerged = data_manager.process_data(jsonToBeMerged, 'json')
                        import copy
                        baseJson = copy.deepcopy(jsonToBeParsed)
                        result = json_merge.merge(baseJson, json.loads(jsonToBeMerged))
                        result = json.dumps(result, indent=4)
                    else:
                        result = json.dumps(jsonToBeParsed, indent=4)


            elif rcType == 'header':
                responseHeaders = data_manager.headerStore[srcRequestId]
                headerToBeRetrived = kwargs[2]
                result = responseHeaders[headerToBeRetrived]
        except Exception as e:
            if isinstance(e, KeyError):
                print('No request found with id: ', srcRequestId)
                print(str(e))
            else:
                print(traceback.format_exc())
            raise e

        return result

    def Now(*kwargs):
        return datetime.now().strftime('%d%m%y%H%M%S%f')

    def skip(*kwargs):
        return '.*'

    def uuid(*kwargs):
        return uuid.uuid4()

    def isJson(data):
        isJson = False
        try:
            if isinstance(data, str):
                json.loads(data)
                isJson = True
            elif isinstance(data, (list, dict, tuple)):
                isJson = True
        except:
            #print('Do nothing')
            a=1
        return isJson
    def delete(*kwargs): # this method does not do anything
        #return data_manager.openingChars + 'DELETE' + data_manager.closingChars
        return data_manager.deleteEscape

    def delete_node(*kwargs): # this method does not do anything
        #return data_manager.openingChars + 'DELETE' + data_manager.closingChars
        return data_manager.deleteNode

