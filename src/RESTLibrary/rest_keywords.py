from .request_info import request_info
from .libcommons import libcommons
from .data_manager import data_manager

class rest_keywords:
    '''
    RESTLibrary provides a feature-rich and extensible infrastructure which is required for making any REST/HTTP call along with all the possible range of features which one might need for doing end-to-end REST API automation using robotframework. 
    All the repetitive tasks which API automation developer has to perform frequently are taken care as part of standard features of the library, like JSON comparison, benchmarking, file upload, file download, authentication, logging/reporting, response channelization, runtime variable resolution etc.
    
    The library exposes a single keyword - Make HTTP Request, which has all the possible parameters to take care of all the features required for end-to-end REST API Automation.

    '''
    def __init__(self, username='', password='', authType="NoAuth", username_var='username', password_var='password'):
        self.username = username if username else libcommons.get_variable('${' + username_var + '}')
        self.password = password if password else libcommons.get_variable('${' + password_var + '}')
        self.authType = authType
        self.username_var = username_var
        self.password_var = password_var

    def Make_HTTP_Request(self, requestId, url, method='GET', requestHeaders={}, requestBody='', requestDataType='json', responseDataType='json', authType='', expectedStatusCode=200, expectedResponseBody='', username='', password='', files={}, responseVerificationType='full', expectedResponseHeaders={}, expectedResponseSchema=None, verificationScheme=[], downloadFilePath=None, timeout=None, ignoreNodes=[]):
        '''
         requestid : an alphanumeric value which helps identify an HTTP request uniquely
         url : entire URI which needs to be invoked, including query parameters.
         method : HTTP method/verb to be used for the REST call, default is GET, other supported values are HEAD, POST, PUT, PATCH and DELETE
         requestHeaders : a dictionary of all the headers which need to be passed with HTTP request, default is empty dictionary which means no headers.
         requestBody : payload/data to be posted along with the request, it can be either a file-path or content itself
         timeout : request timeout in seconds
         authType : Type of authentication to be used, default is NoAuth, means no authentication (default can be changed while importing the library with authType=<myDefaultAuthType\> parameter), other supported value is Basic.
         You can also choose not to use authType variable and provide auth token on your own while making the request in request headers or url based on your API.
         username : username to be used for authentication while making the request, you can also declare a global/suite/test variable ${username} beforehand rather than passing it with each request. username passed with request will override the global variable.
         password : password to be used for authentication while making the request, you can also declare a global/suite/test variable ${password} beforehand rather than passing it with each request. password passed with request will override the global variable.
        # Response Channelization
        sponse Channelization (RC) is special and unique feature of RESTLibrary, which lets you extract and channelize the data from response of one API call to next API call with least efforts and in scalable manner.
         It can channelize data from response body and response headers both.
         In case of response body channelization you can either channelize selective data or entire body itself based on your need.
         While channelizing entire body you also have an option to update it if needed.

        ## RC Syntax (RC === Response Channelization)
        <<<rc, src_request_id, rcType, selector>>>
        An RC block is always written between <<< and >>> tokens.
        Here are the details about 4 comma separated parameters inside RC block
        rc : this is name of the keyword, so it's value will always be rc
        src_request_id : this is id of the source request from which you want to extract and channelize the data
        rcType : this variable denotes whether you want to extract data from response body or response headers, supported values are body and header
        selector : using this variable you can specify what data you want to extract. It can have many values based on rcType.

        |  rcType | selector  |  examples 							    |comments
        |---------|-----------|-----------------------------------------|-------------------------------------------------------------------------------------------|
        |body     |jsonPath   |$.id       								|selecting id																				|
        |         |           |$.items[?(@.name="user1")].id   			|selecting id of the item which has name as user1											|
        |         |json       |{"name" : "user1_updated"}   			|will return entire response body with updated name											|
        |         |           |{"$.items[*].name" : "user1_updated"}   	|will return entire response body with updated name of every item in the json				|
        |         |           |{"$.items[*].name" : "<<<DELETE\>>>"}   	|will return entire response body after deleting name node from every item in the json		|
        |         |           |{}      									|will return entire response body as is without any changes									|
        |header   |headerName |etag   									|will return etag header value from the response headers of the src request					|
        |---------|-----------|-----------------------------------------|--------------------------------------------------------------------------------------------

        # Runtime Variable Resolution
        This is again a unique feature of RESTLibrary, which allows you to embed robot variables and RCs inside json files (and any other files as well which have text content type), which you might use for storing request payloads and baselines.
        RESTLibrary will ensure to resolve these variables/RCs at runtime when the request is being processed.

        # Datetime Stamping
        RESTLibrary has a special variable : <<<NOW\>>>
        This variable automatically gets replced by the current datetime stamp
        datetime format is %d%m%y%H%M%S%f, this always generates a 18 digit number, which is entirely unique
        You can embed this variable anywhere in the request body, headers, json payload or benchmark files
        This can be used to generate unique data values without any extra efforts.

        expectedStatusCode : This parameter facilitates verification of http status code, it's default value is 200
        expectedResponseBody : Expected response body or the baseline which you expect the HTTP request to return, it can either be a file path or in-place json.
         * You can also use regular expressions in json node values, if you just want to verify pattern rather than actual value.
         * You can use <<<SKIP\>>> as the node value if you want to skip the verification of a specific node
        responseVerificationType : This parameter influences the json comparison of response body and benchmark. It's default value is 'FULL', other supported value is 'PARTIAL'.
         * In case of 'FULL' verification both the JSONs are thoroughly compared from both the sides and any differences found are reported in the robot report
         * in case of 'PARTIAL' verification, you can provide partial json with few nodes in expectedResponseBody which you intend to verify (all the nodes in HTTP response will not be verified, only nodes provided in the expectedResponseBody will be verified)
        expectedResponseHeaders : Expected response headers which you expect the HTTP request to return, it should be a dictionary
        * It is always 'PARTIAL' comparison, it will only compare the headers which you supply as expectedResponseHeaders
        * You can use regular expressions here as well, if you just want to verify pattern
        expectedResponseSchema : JSON Schema to validate the structure of HTTP response (if you just want to verify the response json structure):
        * You can use any JSONSchemaGenerator utility to generate the schema, for example : https://www.jsonschema.net/home
        * You can either provide the jsonschema file path or the schema itself as the parameter value
        * It uses JSONSchema Draft-7
        verificationScheme : this parameter is useful to specify how we want our baseline to get compared with response. It's a list of schemes, each scheme is a json object with predefined structure.
        * NotSorted Verification : If there is a list of objects in your response and objects are listed in random order, then using NotSorted scheme you can enforce an orderless comparison with benchmark
           * Syntax Example - verificationScheme=[{"path": "$.data","type": "NotSorted","key": "email"}]
           * path is the jsonpath of the list node, type is the type of scheme and key is a node-name which has a unique value in each object of the list, you can also provide a composite key with comma separated node-names
        * Sort : This will sort a list of objects in your response based on given key before comparing it with benchmark
          * Syntax Example - verificationScheme=[{"path": "$.data","type": "Sort","key": "email"}]
          * path is the jsonpath of the list node, type is the type of scheme and key is a node-name which has a unique value in each object of the list, you can also provide a composite key with comma separated node-names
          * key can be skipped if you have a list of values rather than objects
        * you can provide multiple schemes separated by comma as the parameter value
        ignoreNodes : using this parameter you can completely ignore a set of nodes from the benchmark comparison, this is a quick way to ignore multiple nodes
          * it's a list of jsonpaths of the nodes which you want to ignore
          * Syntax example : ignoreNodes=["$.id", "$.data[*].links"]

         requestDataType : type of content which is being posted to server, default is JSON, other supported values are TEXT and FILE
         responseDataType : type of content which is expected to be returned in response, default is JSON, other supported values are TEXT and FILE

        downloadFilePath : full path of the file including filename, where you want the file to get downloaded
        files : this is where you provide details of the files which need to be uploaded, it is a dictionary
        * below formats are supported:
          * {'fieldName' : 'filePath/fileContent'}
          * {'fieldName' : ['fileName', 'filePath']}
          * {'fieldName' : ['fileName', 'filePath', 'content-type']}
          * {'fieldName' : ['fileName', 'filePath', 'content-type', {custom_headers}]}
        * you should choose the format which your REST API has implemented, your dev team can provide more info
        * you can add any number of files to the dictionary if your API supports multi-file upload
        '''
        authType = authType if authType else self.authType
        username = username if username else self.username
        password = password if password else self.password

        requestInfo = request_info().Create_Request_Info(requestId, url, method=method, requestHeaders=requestHeaders, requestBody=requestBody, authType=authType, requestDataType=requestDataType, responseDataType=responseDataType, expectedStatusCode=expectedStatusCode, expectedResponseBody=expectedResponseBody, username=username, password=password, files=files, responseVerificationType=responseVerificationType, expectedResponseHeaders=expectedResponseHeaders, expectedResponseSchema=expectedResponseSchema, verificationScheme=verificationScheme, username_var=self.username_var, password_var=self.password_var, downloadFilePath=downloadFilePath, timeout=timeout, ignoreNodes=ignoreNodes)
        libcommons.robotBuiltIn.set_suite_variable("${requestInfo}", requestInfo)
        requestInfo = libcommons.run_keyword('Generate Http Request', "${requestInfo}")
        libcommons.robotBuiltIn.set_suite_variable("${requestInfo}", requestInfo)
        requestInfo = libcommons.run_keyword('Process Http Request', "${requestInfo}")
        libcommons.robotBuiltIn.set_suite_variable("${requestInfo}", requestInfo)
        data_manager.statusStore[requestInfo.requestId] = requestInfo.responseStatusCode
        requestInfo = libcommons.run_keyword('Verify Response Against Baselines', "${requestInfo}")
        return requestInfo

    def Execute_RC(self, input):
        '''
        input : lets you evaluate all the RC macros, including multiple RCs and NOW immediately and run the response channelization, you can store the value in any variable and use it as required
                                    <<<NOW>>>___SomeText__<<<RC, src request id, body, json path>>>
                                    <<<NOW>>>
                                    <<<RC, src request id, body, json path>>>
                                    <<<RC, src request id, header, header name>>>
                                  we can also have an Entire Response Channelization where entire response of the src request will be channelized after merging with the patch json, patch can be a file path or json conrent
                                  using this we can add, delete and update the nodes from src json response. (deletion can be achieved using <<<delete>>> value)
                                    <<<RC, src request id, body, patch json>>>
        Returns:
            returns the value after running the response channelization, it could be a single node value or entire json, depending on whether it is normal RC or entire
        '''
        result = input
        result = data_manager.process_data(input)
        return result