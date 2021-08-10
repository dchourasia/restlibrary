import json, traceback
from jsonpath_ng.ext import parser
from jsonpath_ng.ext.filter import Filter


class json_merge:

    deleteNotifiers = ['<<<DELETE>>>', '@@DELETE@@', '___DELETE___']
    def merge(base, head):

        try:
            if head.__class__.__name__.lower() in ('dict', 'dotdict') :
                for k, v1 in head.items():
                    if k in base:
                        v2 = base[k]
                        if v1.__class__.__name__.lower() in ('list', 'dict', 'dotdict') and v1.__class__.__name__.lower() == v2.__class__.__name__.lower():
                            base[k] = json_merge.merge(base[k], head[k])
                        elif type(v1) is str and v1.upper() in json_merge.deleteNotifiers:
                            del base[k]
                        else:
                            base[k] = v1
                    elif k[0] == '$': #check if it is a json path
                        base = json_merge.addOrUpdateValueAtGivenJsonPath(base, k, v1)
                    else:
                        base[k] = v1
            elif head.__class__.__name__.lower() == 'list':
                if len(head) and len(base):
                    for index, item in enumerate(head):
                        if index > len(base) - 1:
                            base.append(head[index])
                        elif item.__class__.__name__ in ('list', 'dict', 'dotdict') and item.__class__.__name__ == base[index].__class__.__name__:
                            base[index] = json_merge.merge(base[index], head[index])
                        elif type(item) is str and item.upper() in json_merge.deleteNotifiers:
                            del base[index]
                        else:
                            base[index] = item
                elif len(head):
                    base = head
            else:
                base = head
        except Exception as e:
            print(traceback.format_exc())
            raise e

        return base

    def addOrUpdateValueAtGivenJsonPath(jsonDict, jsonPath, value):
        try:
            isDeleteCase = type(value) is str and value.upper() in json_merge.deleteNotifiers
            if json_merge.checkIfNodeExistsAtGivenJsonPath(jsonDict, jsonPath) and not isDeleteCase:
                jsonPathExpression = parser.ExtentedJsonPathParser().parse(jsonPath.replace(' && ', ' & '))
                jsonDict = jsonPathExpression.update(jsonDict, value)
            else:
                parent, key = json_merge.getParentAndKeyFromJsonPath(jsonPath, jsonDict)
                if parent and key and json_merge.checkIfNodeExistsAtGivenJsonPath(jsonDict, parent):
                    jsonPathExpression = parser.ExtentedJsonPathParser().parse(parent.replace(' && ', ' & '))
                    matches = jsonPathExpression.find(jsonDict)
                    for index, match in enumerate(matches):
                        #print(match.full_path)
                        localJsonPathExpression = parser.ExtentedJsonPathParser().parse('$.' + str(match.full_path).replace(' && ', ' & '))
                        item = match.value

                        if isDeleteCase:
                            if item.__class__.__name__ in ('dict', 'dotdict') and key in item:
                                del item[key]
                            elif  type(item) is list and int(key) < len(item):
                                del item[int(key)]
                        else:
                            if item.__class__.__name__ in ('dict', 'dotdict') or (type(item) is list and int(key) < len(item) - 1):
                                item[key] = value
                            elif type(item) is list and int(key) >= len(item) - 1:
                                item.append(value)

                        jsonDict = localJsonPathExpression.update(jsonDict, item)
                        jsonDump  = json.dumps(jsonDict)
                        a=1
                        #jsonDict = json_merge.update_ex(jsonPathExpression, jsonDict, replacedChildDict)
                else:
                    print('No node exists at given json path ', jsonPath)
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            print('Could not update node at given json path ', jsonPath)
        return jsonDict

    def update_ex(jsonPathExpression, data, val):
        if 'right' in jsonPathExpression.__dict__ and type(jsonPathExpression.right) is Filter:
            for datum in jsonPathExpression.left.find(data):
                #jsonPathExpression.right.update(datum.value, val)
                if type(datum.value) is list:
                    for index, item in enumerate(datum.value):
                        shouldUpdate = len(jsonPathExpression.right.expressions) == len(list(filter(lambda x: x.find(item), jsonPathExpression.right.expressions)))
                        if shouldUpdate:
                            if hasattr(val, '__call__'):
                                val.__call__(datum.value[index], datum.value, index)
                            else:
                                datum.value[index] = val
            return data
        return jsonPathExpression.update(data, val)
    def getParentAndKeyFromJsonPath(jsonPath, jsonDict=None):
        parent, key = None, None
        if jsonPath[-1] == ']':#its a list
            parts= jsonPath.split('[')
            key = parts[-1].replace(']', '')
            if '?' not in key and ':' not in key:
                try:
                    intKey = int(key)
                    parent = '['.join(parts[:len(parts) - 1])
                except:
                    a=1
            elif jsonDict:
                jsonPathExpression = parser.ExtentedJsonPathParser().parse(jsonPath.replace(' && ', ' & '))
                matches = jsonPathExpression.find(jsonDict)
                if len(matches):
                    print(matches[0].full_path)
                    jsonPath = '$.' + str(matches[0].full_path)
                    parts = jsonPath.split('[')
                    key = parts[-1].replace(']', '')
                    try:
                        intKey = int(key)
                        parent = '['.join(parts[:len(parts) - 1])
                        parent = parent[:-1] if parent.endswith('.') else parent
                    except:
                        a=1
        elif '.' in jsonPath:
            parts = jsonPath.split('.')
            key = parts[-1]
            parent = '.'.join(parts[:len(parts) - 1])
        parent = parent[:-1] if parent.endswith('.') else parent
        return (parent, key)

    def checkIfNodeExistsAtGivenJsonPath(jsonDict, jsonPath):
        nodeExists = False
        try:  # first try with ng
            jsonPathExpression = parser.ExtentedJsonPathParser().parse(jsonPath.replace(' && ', ' & '))
            matches = jsonPathExpression.find(jsonDict)
            if matches.__len__():
                nodeExists = True
        except:
            a=1
        return nodeExists






