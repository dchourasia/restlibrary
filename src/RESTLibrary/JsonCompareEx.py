import json
import re, os, traceback
from jsonpath_ng.ext import parser
from .libcommons import libcommons
from .json_merge import json_merge
from .data_manager import data_manager

TypeMismatch = 'Type Mismatch'
NodeMissing = 'Node Missing'
CountMismatch = 'Item Count Mismatch'
ValueMismatch = 'Value Mismatch'
jsonNames = ['Benchmark', 'Response']
diffNodeNames = ['benchmark', 'response']
deleteNotifier = data_manager.openingChars + 'DELETE' + data_manager.closingChars
skipNotifier = '.*'
# we always assume benchmark is passed as first and response as second
class JsonCompareEx:
    def __init__(self, first, second, with_values=False, swapped=False, partial=False):
        try:
            self.difference = []
            self.seen = []
            self.swapped = swapped
            self.partial = partial
            global NodeMissing
            NodeMissing = f'Node Missing From {jsonNames[int(not self.swapped)]}'
            self.check(first, second, with_values=with_values)

        except Exception as e:
            print(traceback.format_exc())
            raise e

    def check(self, first, second, path='', with_values=False):
        try:
            if with_values and second != None:
                if not isinstance(first, type(second)) and first != skipNotifier and second != skipNotifier:
                    self.save_diff(path, TypeMismatch, type(first).__name__, type(second).__name__)

            if first.__class__.__name__.lower() in ('dict', 'dotdict'):
                if path and len(first) == 0 and self.partial and isinstance(second, dict) and len(second) > 0:
                    self.save_diff(path, CountMismatch, str(len(first)), str(len(second)))

                for key in first:
                    # the first part of path must not have trailing dot.
                    if len(path) == 0:
                        new_path = key
                    else:
                        new_path = "%s.%s" % (path, key)

                    if isinstance(second, dict):
                        if key in second:
                            sec = second[key]
                        else:
                            #  there are key in the first, that is not presented in the second
                            self.save_diff(new_path, NodeMissing)

                            # prevent further values checking.
                            sec = None

                        # recursive call
                        if sec != None:
                            self.check(first[key], sec, path=new_path, with_values=with_values)
                    else:
                        # second is not dict. every key from first goes to the difference
                        self.save_diff(new_path, NodeMissing)
                        self.check(first[key], second, path=new_path, with_values=with_values)

            # if object is list, loop over it and check.
            elif isinstance(first, list):
                if path and len(first) == 0 and self.partial and isinstance(second, list) and len(second) > 0:
                    self.save_diff(path, CountMismatch, str(len(first)), str(len(second)))

                for (index, item) in enumerate(first):
                    new_path = "%s[%s]" % (path, index)
                    # try to get the same index from second
                    sec = None
                    if second != None:
                        try:
                            sec = second[index]
                        except (IndexError, KeyError):
                            # goes to difference
                            self.save_diff(new_path, NodeMissing)

                    # recursive call
                    self.check(first[index], sec, path=new_path, with_values=with_values)

            # not list, not dict. check for equality (only if with_values is True) and return.
            else:
                if with_values and second != None:
                    if not self.compareValues(first, second):
                        self.save_diff(path, ValueMismatch, first, second)
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return

    def save_diff(self, path, type_, first=None, second=None):
        try:
            if path not in self.difference:
                self.seen.append(path)
                diff = {}
                diff['type'] = type_
                diff['path'] = path
                if first != None and second != None:
                    diff[diffNodeNames[int(self.swapped)]] = first
                    diff[diffNodeNames[int(not self.swapped)]] = second
                self.difference.append(diff)
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def compareValues(self, first, second):
        result = first == second
        if not result and type(first) is str:
            try:
                data = [first, second]
                benchIndex = int(self.swapped)
                respIndex = int(not self.swapped)
                try:
                    secondRegex = re.compile('^' + data[benchIndex] + '$')
                    matches = secondRegex.findall(data[respIndex])
                    if len(matches) == 1:
                        result = True
                except:
                    a = 1
            except Exception as e:
                print(traceback.format_exc())
                raise e
        if not result and (first == skipNotifier or second == skipNotifier):
            result = True
        return result

    def escapeSpecialCharsForRegex(self, data):
        result = data
        escapeChars = '\/^$|?*(){['
        if result:
            for char in escapeChars:
                result = result.replace(char, '\\' + char)
        return result
def getContentFromFile(filePath):
    try:
        if type(filePath) is str and libcommons.path_exists(filePath):
            filePath = open(filePath, 'r').read()
    except Exception as e:
        print(traceback.format_exc())
        raise e
    return filePath


def getJson(data):
    try:
        if data.__class__.__name__.lower() in ('dict', 'dotdict', 'list'):
            return data

        content = getContentFromFile(data)
        if content is None:
            raise Exception("Could not load content for " + data)
    except Exception as e:
        print(traceback.format_exc())
        raise e
    return json.loads(content)

def getExtendedDiffNode(node, extensionObj):
    res = node.copy()
    for key, val in extensionObj.items():
        res[key] = val

    return res
def processVerificationSchemes(json1, json2, verificationScheme, swapped=False):
    diffs = []
    try:
        if len(verificationScheme):

            NotSortedInstances = [x for x in verificationScheme if 'type' in x and x['type'].upper() == 'NOTSORTED']
            for scheme in NotSortedInstances:
                path = scheme['path']
                keys = scheme['key'].split(',')
                keys = [key.strip() for key in keys]

                jsonPathExpression = parser.ExtentedJsonPathParser().parse(path.replace(' && ', ' & '))
                matches = jsonPathExpression.find(json1)
                for index, match in enumerate(matches):
                    if type(match.value) is list and len(match.value):
                        localJsonPathExpression = parser.ExtentedJsonPathParser().parse(
                            '$.' + str(match.full_path).replace(' && ', ' & '))
                        benchmarkList = match.value
                        responseList = localJsonPathExpression.find(json2)

                        if len(responseList):
                            responseList = responseList[0].value
                            responseListUpdated = False
                            MissingNodeList = []
                            for benchIndex, benchItem in enumerate(benchmarkList[::-1]):
                                respIndex = [index for index, item in enumerate(responseList) if allKeysSameInBothItems(keys, item, benchItem)]
                                if len(respIndex):
                                    respIndex = respIndex[0]
                                    responseList.insert(0, responseList.pop(respIndex))
                                    responseListUpdated = True
                                else:
                                    MissingNodeList.append(len(benchmarkList) - benchIndex - 1)
                                    # print('item with ' + ' and '.join([key + ' = ' + benchItem[key] for key in keys]) + ' not found in response body for json path ', path)
                                    message = 'item with ' + ' and '.join([key + ' = \'' + benchItem[key] + '\'' for key in keys]) + ' not found in ' + diffNodeNames[int(not swapped)]
                                    # diffs.append(getExtendedDiffNode(benchItem, {'message': message}))
                                    print(message)

                            if len(MissingNodeList):
                                for idx, index in enumerate(MissingNodeList[::-1]):
                                    json1 = json_merge.addOrUpdateValueAtGivenJsonPath(json1, path.replace(' && ', ' & ') + '[' + str(index - idx) + ']', deleteNotifier)
                            if responseListUpdated:
                                localJsonPathExpression.update(json2, responseList)

            SortingInstances = [x for x in verificationScheme if 'type' in x and x['type'].upper() == 'SORT']
            for scheme in SortingInstances:
                path = scheme['path']
                keys = scheme['key'].split(',') if 'key' in scheme else []
                keys = [key.strip() for key in keys]

                jsonPathExpression = parser.ExtentedJsonPathParser().parse(path.replace(' && ', ' & '))
                matches = jsonPathExpression.find(json1)
                for index, match in enumerate(matches):
                    if type(match.value) is list and len(match.value):
                        ordered = match.value
                        if len(keys):
                            ordered = sorted(ordered, key=lambda x: ''.join([str(x[k]) for k in keys]))
                        else:
                            ordered = sorted(ordered)
                        jsonPathExpression.update(json1, ordered)

                matches = jsonPathExpression.find(json2)
                for index, match in enumerate(matches):
                    if type(match.value) is list and len(match.value):
                        ordered = match.value
                        if len(keys):
                            ordered = sorted(ordered, key=lambda x: ''.join([str(x[k]) for k in keys]))
                        else:
                            ordered = sorted(ordered)
                        jsonPathExpression.update(json2, ordered)




    except Exception as e:
        print(traceback.format_exc())
        raise e
    return json1, json2, diffs

def allKeysSameInBothItems(keys, item1, item2):
    same = True
    for key in keys:
        same = same and key in item1 and item1[key] == item2[key]
    return same

def processIgnoredNodes(json1, json2, ignoreNodes):
    for path in ignoreNodes:
        jsonPathExpression = parser.ExtentedJsonPathParser().parse(path.replace(' && ', ' & '))
        matches = jsonPathExpression.find(json1)
        if len(matches):
            for match in matches[::-1]:
                jsonPath = '$.' + str(match.full_path)
                json1 = json_merge.addOrUpdateValueAtGivenJsonPath(json1, jsonPath.replace(' && ', ' & '), data_manager.deleteNotifier)

        matches = jsonPathExpression.find(json2)
        if len(matches):
            for match in matches[::-1]:
                jsonPath = '$.' + str(match.full_path)
                json2 = json_merge.addOrUpdateValueAtGivenJsonPath(json2, jsonPath.replace(' && ', ' & '), data_manager.deleteNotifier)

    return json1, json2

def compareEx(json1, json2, comparisionType='full', verificationScheme=[], ignoreNodes=[], deferIgnoredNodeProcessing=False):
    diffs = []
    try:
        json1 = getJson(json1)  # benchmark
        json2 = getJson(json2)  # response

        if deferIgnoredNodeProcessing:
            json1, json2, diffs = processVerificationSchemes(json1, json2, verificationScheme)

        json1, json2 = processIgnoredNodes(json1, json2, ignoreNodes)

        if not deferIgnoredNodeProcessing:
            json1, json2, diffs = processVerificationSchemes(json1, json2, verificationScheme)



        diff1, diff2 = [], []
        diff1 = JsonCompareEx(json1, json2, True, False, comparisionType.lower() == 'partial').difference
        if not comparisionType.lower() == 'partial':
            diff2 = JsonCompareEx(json2, json1, False, True).difference

        if len(diff1):
            diffs += diff1
        if len(diff2):
            diffs += diff2
    except Exception as e:
        print(traceback.format_exc())
        raise e
    return diffs

