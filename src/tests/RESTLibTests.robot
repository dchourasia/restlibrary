*** Settings ***
Library         json
Library         OperatingSystem
Library         Collections
Library         String
Library         DateTime
Library         RESTLibrary
Library         ${EXECDIR}/auth/customAuth.py
Library         ${EXECDIR}/auth/JWTAuth.py
Resource        ${EXECDIR}/auth/MyAuth.robot

*** Variables ***
${base-url}=        https://reqres.in/api
${username}=        resttest
${password}=        Password1
*** Test Cases ***

#****************************** Simple HTTP Request ************************************
Test # 101 - Make HTTP Request with simple url
    Make HTTP Request   get all users    https://reqres.in/api/users

Test # 102 - Make HTTP Request with query parameters in URL
    Make HTTP Request   get all users    https://reqres.in/api/users?page=1



#****************************** HTTP Request Variations ************************************
Test # 201 - Make GET request
#    default method is GET, so whenever you do not provide method, RESTLibrary automatically makes a GET request
    Make HTTP Request   get all users    https://reqres.in/api/users?page=1
Test # 202 - Make POST request
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody={"name":"deepak", "job":"automation developer"}      expectedStatusCode=201

Test # 203 - MAKE PUT request
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody={"name":"deepak", "job":"automation developer"}

Test # 204 - Make PATCH Request
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PATCH       requestBody={"name":"deepak", "job":"automation developer"}

Test # 205 - Make HEAD request
    Make HTTP Request   check if user exist    https://reqres.in/api/users/2    method=HEAD

Test # 206 - Make DELETE request
    Make HTTP Request   check if user exist    https://reqres.in/api/users/2    method=DELETE      expectedStatusCode=204

Test # 207 - Make POST request with in-place json payload
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody={"name":"deepak", "job":"automation developer"}      expectedStatusCode=201

Test # 208 - Make POST request with requestbody filepath
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody=${EXECDIR}/inputs/createUserStatic.json      expectedStatusCode=201

Test # 209 - Make HTTP request with request headers
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST    requestHeaders={'Content-Type' : 'application/json', 'Accept' : 'application/json'}       requestBody={"name":"deepak", "job":"automation developer"}      expectedStatusCode=201

Test # 210 - Make HTTP request with precreated headers dict
    &{headers}=     Create Dictionary       Content-Type=application/json       Accept=application/json
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST    requestHeaders=${headers}       requestBody={"name":"deepak", "job":"automation developer"}      expectedStatusCode=201

Test # 211 - Make HTTP request with request timeout
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST    timeout=15       requestBody={"name":"deepak", "job":"automation developer"}    expectedStatusCode=201


Test # 212 - Make POST request which accepts JSON and returns JSON
#    default requestDataType is JSON and default responseDataType is also JSON, so whenever you do not provide these parameters, RESTLibrary assumes that your API expects/returns JSON
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody={"name":"deepak", "job":"automation developer"}    expectedStatusCode=201

Test # 213 - Create User
      Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST    requestHeaders={'Content-Type' : 'application/json', 'Accept' : 'application/json'}       requestBody={"name":"deepak", "job":"automation developer"}    timeout=15    expectedStatusCode=201



#****************************** Authentication ************************************
Test # 301 - Make HTTP Request with default authType
#   default authType is NoAuth, means no authentication
    Make HTTP Request   get all users    https://reqres.in/api/users?page=1

Test # 302 - Make HTTP Request with Basic authType
    Make HTTP Request   get all users    https://reqres.in/api/users?page=1     authType=Basic      username=deepak     password=pass123

Test # 303 - Make HTTP Request with custom auth type (implemented using robot keyword located in a external resource file)
#    MyAuth resource file is imported in Settings section
    Make HTTP Request   my-first-request    ${base-url}/users?page=2        authType=MyAuth.set my auth token

Test # 304 - Make HTTP Request with custom auth type (implemented using robot keyword located in same suite file)
#   "set my auth token" keyword is implemented in keywords section of this file
    Make HTTP Request   my-first-request    ${base-url}/users?page=2        authType=set my auth token
    
Test # 305 - Make HTTP Request with custom auth type (implemented using python library)
#    customAuth library is imported in Settings section
    Make HTTP Request   my-first-request    ${base-url}/users?page=2        authType=customAuth.set authentication

Test # 306 - Make HTTP Request using globally defined username and password
    Make HTTP Request   get all users    https://reqres.in/api/users?page=1     authType=Basic

Test # 307 - jwt auth - custom authentication (python implementation example)
#    JWTAuth library is imported in Settings section
    ${jwtClientId}      ${jwtClientSecret}=     Set Variable        dchourasia              DTGRAS21453
    Set Test Variable   ${jwtClientId}      ${jwtClientSecret}
    Make HTTP Request   my-first-request    ${base-url}/users?page=2        authType=JWTAuth.set authentication
    
    
    
#****************************** Response Channelization ************************************
Test # 401 - Response channelization (RC) of id from one request to next - using simple jsonpath
    Make HTTP Request   get all users    https://reqres.in/api/users
    Make HTTP Request   get user details    https://reqres.in/api/users/<<<rc, get all users, body, $.data[0].id>>>

Test # 402 - Response channelization (RC) of id from one request to next - using complex jsonpath with filters and conditions
    Make HTTP Request   get all users    https://reqres.in/api/users
    Make HTTP Request   get user details    https://reqres.in/api/users/<<<rc, get all users, body, $.data[?(@.first_name == 'Emma' & @.last_name == 'Wong' & @.email =~ 'reqres')].id>>>

Test # 403 - pass RC as keyword parameter value
    Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1
    Get User By Id      userid=<<<rc, Get all the users, body, $.data[0].id>>>

Test # 404 - Entire Response Channelization from one request to next - with no updates
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {}>>>

Test # 405 - Entire Response Channelization from one request to next - with addition of few fields using json
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"data" : {"name" : "Deepak Chourasia", "job" : "Automation Developer"}}>>>

Test # 406 - Entire Response Channelization from one request to next - with updation of few existing fields using json
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"data" : {"first_name" : "Deepak", "last_name" : "Chourasia"}}>>>

Test # 407 - Entire Response Channelization from one request to next - with deletion of few existing fields using json
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"data" : {"first_name" : "<<<DELETE>>>", "last_name" : "<<<DELETE>>>"}}>>>

Test # 408 - Entire Response Channelization from one request to next - with addition of few fields using jsonpath
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"$.data.name" : "Deepak Chourasia", "$.data.job" : "Automation Developer"}>>>

Test # 409 - Entire Response Channelization from one request to next - with updation of few existing fields using jsonpath
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"$.data.first_name" : "Deepak", "$.data.last_name" : "Chourasia"}>>>

Test # 410 - Entire Response Channelization from one request to next - with deletion of few existing fields using jsonpath
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"$.data.first_name" : "<<<DELETE>>>", "$.data.last_name" : "<<<DELETE>>>"}>>>

Test # 411 - Entire Response Channelization from one request to next - with add/update/delete of fields using json/jsonpath
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"data" : {"name" : "Deepak Chourasia", "job" : "Automation Developer"}, "$.data.first_name" : "Deepak", "$.data.last_name" : "<<<DELETE>>>"}>>>

Test # 412 - Entire Response Channelization from one request to next - with add/update/delete of fields using json/jsonpath in external file
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, ${EXECDIR}/inputs/patch.json>>>

Test # 413 - Header Channelization from one request to next
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT    requestHeaders={'Etag' : '<<<rc, get user details, header, Etag>>>', 'Content-Type' : 'application/json', 'Accept' : 'application/json'}       requestBody=<<<rc, get user details, body, {}>>>

Test # 414 - End to end CRUD operations using RC
      # this example demonstrates a Partial benchmark verification using in-place json along with status code verification
      Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody={"name":"deepak", "job":"automation developer"}     expectedStatusCode=201      expectedResponseBody={"id" : "[0-9]{1,6}"}    responseVerificationType=Partial

      Make HTTP Request   get all users    https://reqres.in/api/users?page=1

      # here we are using RC to chennelize id of the newly created user dynamically from the "create user" response body, id is needed to get the user
      Make HTTP Request   get user details    https://reqres.in/api/users/<<<rc, get all users, body, $.data[0].id>>>     method=GET    requestHeaders={'Accept' : 'application/json'}

      # here we are using RC to channelize entire response body of "create user" along with a name update, we are also channelizing etag header
      Make HTTP Request   update the user    https://reqres.in/api/users/<<<rc, get all users, body, $.data[0].id>>>    method=PUT    requestHeaders={'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Etag' : '<<<rc, get user details, header, Etag>>>'}       requestBody=<<<rc, get user details, body, {"data" : {"first_name":"deepak", "last_name" : "chourasia"}}>>>

      # here again we are channelizing user id which is needed to delete the user
      Make HTTP Request   delete the user    https://reqres.in/api/users/<<<rc, get all users, body, $.data[0].id>>>     method=DELETE      expectedStatusCode=204



#****************************** Runtime Variable Resolution ************************************
Test # 501 - Runtime Variable Resolution of global variables
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody=${EXECDIR}/inputs/globalVars.json      expectedStatusCode=201

Test # 502 - Runtime Variable Resolution of suite variables
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody=${EXECDIR}/inputs/suiteVars.json      expectedStatusCode=201

Test # 503 - Runtime Variable Resolution of test variables
    ${name}     ${job}=     Set Variable      Deepak Chourasia      Automation Developer
    Set Test Variable   ${name}
    Set Test Variable  ${job}
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody=${EXECDIR}/inputs/testVars.json      expectedStatusCode=201

Test # 504 - Runtime Variable Resolution of keyword arguments
      Create User    Deepak       Automation Developer
      Create User    Evans        UX Designer
      Create User    Elizabeth    Software Developer
      Create User    Stephen      Project Manager
      
Test # 505 - Runtime Resolution of RC tags
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    ${name}=     Set Variable      Deepak Chourasia
    Set Test Variable   ${name}
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT    requestBody=${EXECDIR}/inputs/updateUser.json



#****************************** Datetime Stamping : NOW ************************************
Test # 601 - usage of NOW with in-place requestbody
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody={"name":"user_<<<NOW>>>", "job":"automation developer"}      expectedStatusCode=201

Test # 602 - usage of NOW in requestbody file
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody=${EXECDIR}/inputs/createUniqueUser.json      expectedStatusCode=201

Test # 603 - usage of NOW in request headers
    Make HTTP Request   get user details    https://reqres.in/api/users/2    requestHeaders={'sessionId' : 'session-<<<NOW>>>'}

Test # 604 - usage of NOW with entire response channelization
    Make HTTP Request   get user details    https://reqres.in/api/users/2
    Make HTTP Request   update the user    https://reqres.in/api/users/2    method=PUT       requestBody=<<<rc, get user details, body, {"currentDateTime" : "<<<NOW>>>", "$.data.first_name" : "Deepak", "$.data.last_name" : "<<<DELETE>>>"}>>>

Test # 605 - Create Unique Users
      # All these 4 requests will create users with unique name
      Create New User
      Create New User
      Create New User
      Create New User



#****************************** Baselining / Benchmarking ************************************
Test # 701 - HTTP request with default expectedStatusCode
#    default value of expectedStatusCode is 200
    Make HTTP Request   get user details    https://reqres.in/api/users/2

Test # 702 - HTTP request with expectedStatusCode
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST      expectedStatusCode=201       requestBody={"name":"deepak", "job":"automation developer"}

Test # 703 - HTTP request with expectedResponseBody filepath
    Make HTTP Request   get user details    https://reqres.in/api/users/2      expectedResponseBody=${EXECDIR}/baselines/getUser2.json

Test # 704 - HTTP request with in-place expectedResponseBody and 'PARTIAL' verification
    Make HTTP Request   get user details    https://reqres.in/api/users/2    responseVerificationType=Partial      expectedResponseBody={"data" : {"first_name" : "Janet", "last_name" : "Weaver"}}

Test # 705 - HTTP request with benchmarking using regular expressions
    Make HTTP Request   get user details    https://reqres.in/api/users/2    responseVerificationType=Partial      expectedResponseBody={"data" : {"email" : "[a-zA-Z]{1,100}.[a-zA-Z]{1,100}@reqres.in", "first_name" : "Janet", "last_name" : "Weaver"}}

Test # 706 - HTTP request with benchmarking with SKIP of few fields
    Make HTTP Request   get user details    https://reqres.in/api/users/2      expectedResponseBody=${EXECDIR}/baselines/getUser2_skip.json

Test # 707 - HTTP request with verification of response headers
    Make HTTP Request   get the user    https://reqres.in/api/users/2       expectedResponseHeaders={'Content-Type' : 'application/json; charset=utf-8', 'Connection' : 'keep-alive'}

Test # 708 - HTTP request with verification of response headers using regular expressions
    Make HTTP Request   get the user    https://reqres.in/api/users/2       expectedResponseHeaders={'Date' : '[a-zA-Z]{3}, [0-9]{2} [a-zA-Z]{3} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT'}

Test # 709 - HTTP request with JSON Schema validation
    Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1     expectedResponseSchema=${EXECDIR}/baselines/allusers_Schema.json

Test # 710 - HTTP request with benchmarking using 'NotSorted' verification scheme
    Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1     verificationScheme=[{"path": "$.data","type": "NotSorted","key": "email"}]      expectedResponseBody=${EXECDIR}/baselines/getAllUsersJumbled.json

Test # 711 - HTTP request with benchmarking using 'NotSorted' verification scheme using composite key
    Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1     verificationScheme=[{"path": "$.data","type": "NotSorted","key": "id, email"}]      expectedResponseBody=${EXECDIR}/baselines/getAllUsersJumbled.json

Test # 712 - HTTP request with benchmarking using 'SORT' verification scheme
    Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1     verificationScheme=[{"path": "$.data","type": "Sort","key": "email"}]      expectedResponseBody=${EXECDIR}/baselines/getAllUsersJumbled.json

Test # 713 - HTTP request with benchmarking using 'SORT' verification scheme using composite keys
    Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1     verificationScheme=[{"path": "$.data","type": "Sort","key": "id, email"}]      expectedResponseBody=${EXECDIR}/baselines/getAllUsersJumbled.json

Test # 714 - HTTP request with benchmarking using 'SORT' verification scheme without any keys
    Make HTTP Request   Get CKAN action tags    https://demo.ckan.org/api/3/action/tag_list         verificationScheme=[{"path": "$.result","type": "Sort"}]      expectedResponseBody=${EXECDIR}/baselines/ckan_tags.json

Test # 715 - HTTP request with benchmarking with ignoring few nodes using simple jsonpaths
      Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1     ignoreNodes=["$.total", "$.data[*].id"]      expectedResponseBody=${EXECDIR}/baselines/getAllUsersBenchmark.json     verificationScheme=[{"path": "$.data","type": "NotSorted","key": "email"}]

Test # 716 - HTTP request with benchmarking with ignoring few nodes using conditional jsonpaths
    Make HTTP Request   Get all the users    https://reqres.in/api/users?page=1     ignoreNodes=["$.total", "$.data[?(@.first_name == 'Byron' & @.last_name == 'Fields' & @.email =~ 'reqres')].id"]      expectedResponseBody=${EXECDIR}/baselines/getAllUsersBenchmark.json     verificationScheme=[{"path": "$.data","type": "NotSorted","key": "email"}]

Test # 717 - Get All Users
    Make HTTP Request   get all the users    ${base-url}/users?page=2        authType=NoAuth        expectedResponseBody=${EXECDIR}/baselines/allusers.json       verificationScheme=[{"path": "$.data","type": "NotSorted","key": "email"}]      responseVerificationType=Partial        expectedResponseSchema=${EXECDIR}/baselines/allusers_Schema.json

Test # 718 - Get User
      # this example demonstrates a Full benchmark comparison using a benchmark json file along with response header verification
      Make HTTP Request   get the user    https://reqres.in/api/users/<<<rc, Get all the users, body, $.data[0].id>>>     method=GET    requestHeaders={'Accept' : 'application/json'}      expectedResponseBody=${EXECDIR}/baselines/getUserBenchmark.json       expectedResponseHeaders={'Content-Type' : 'application/json; charset=utf-8'}    responseVerificationType=Partial

Test # 719 - Create User with all possible validations
      Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST    requestHeaders={'Content-Type' : 'application/json', 'Accept' : 'application/json'}
      ...   authType=Basic       requestBody={"name":"deepak", "job":"automation developer"}    expectedStatusCode=201    expectedResponseBody=${EXECDIR}/baselines/createUser.json
      ...   responseVerificationType=Partial       expectedResponseHeaders={'Content-Type' : 'application/json; charset=utf-8'}
      ...   expectedResponseSchema=${EXECDIR}/baselines/createUser_Schema.json


#****************************** Content Types - Text ************************************
Test # 801 - Make POST request with in-place text payload
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody=I am sending text    expectedStatusCode=201

Test # 802 - Make POST request with text payload filepath
    Make HTTP Request   create a new user    https://reqres.in/api/users    method=POST       requestBody=${EXECDIR}/inputs/sample.txt    expectedStatusCode=201


#****************************** File Upload / Download ************************************
Test # 803 - Download a pdf file by providing downloadFilePath
#    download file at given path, path should include filename as well, if there is already an existing file at given path then it will be deleted before the download
    Make HTTP Request   download the document    https://file-examples-com.github.io/uploads/2017/10/file-sample_150kB.pdf   responseDataType=File    downloadFilePath=${EXECDIR}/downloads/sample.pdf

Test # 804 - Download a pdf file without providing downloadFilePath
#    file will be downloaded in the execution directory (${EXECDIR}) with name as current datetime stamp (NOW) and no extension, for example 080821154007692691
    Make HTTP Request   download the document    https://file-examples-com.github.io/uploads/2017/10/file-sample_150kB.pdf   responseDataType=File

Test # 805 - Upload file
    Make HTTP Request   upload image    https://images.google.com/searchbyimage/upload    method=POST   requestDataType=File     files={'encoded_image' : ['sample.jpeg', '${EXECDIR}/inputs/sample.jpeg', 'image/jpeg']}



#****************************** Execute RC ************************************
Test # 901 - Instantly execute the Response Channelization (RC) tag
    Make HTTP Request   get all the users    ${base-url}/users?page=2
    Make HTTP Request   get user details    https://reqres.in/api/users/2

    ${first user id}=       Execute RC      <<<rc, get all the users, body, $.data[0].id>>>
    ${Emma Wong user id}=    Execute RC      <<<rc, get all users, body, $.data[?(@.first_name == 'Emma' & @.last_name == 'Wong' & @.email =~ 'reqres')].id>>>
    ${all user id list}=        Execute RC      <<<rc, get all the users, body, $.data[*].id>>>

    ${get user response body}=       Execute RC      <<<rc, get user details, body, {}>>>
    ${updated user response body}=      Execute RC      <<<rc, get user details, body, {"data" : {"name" : "Deepak Chourasia", "job" : "Automation Developer"}, "$.data.first_name" : "Deepak", "$.data.last_name" : "<<<DELETE>>>", "$.currentDate" : "<<<NOW>>>"}>>>

    ${user etag}=       Execute RC      <<<rc, get user details, header, Etag>>>


Test # 902 - pass rc as parameters
    Get User By Id      <<<rc, get all users, body, $.data[0].id>>>
    ${userid}=          Execute RC        <<<rc, get all users, body, $.data[1].id>>>
    Log  ${userid}

    ${user list}=     Execute RC      <<<rc, get all users, body, $.data[*]>>>
    @{user list}=       Evaluate     json.loads('''${user list}''')       json
    Log list        ${user list}



*** Keywords ***
get user by id
    [Arguments]    ${userid}
    Make HTTP Request   get user    ${base-url}/users/${userid}

set my auth token
    [Arguments]  ${request info}
    # here is the example how you can update the url to include custom auth token for your request
    ${request info.url}=    Set Variable    ${request info.url}&token=customAuthToken
    Log  ${request info.url}
    # here is the example how you can update the request headers to include custom auth token for your request
    Set To Dictionary   ${request info.requestHeaders}      customAuthHeaderName=customAuthToken
    Log  ${request info.requestHeaders}
    # return final requestInfo object after all the updates
    [Return]  ${request info}

Create User
    [Arguments]  ${name}    ${job}
    Make HTTP Request   create a new user    https://reqres.in/api/users       requestBody=${EXECDIR}/inputs/createUser.json    method=POST        expectedStatusCode=201

Create New User
    Make HTTP Request   create a new user    https://reqres.in/api/users       requestBody=${EXECDIR}/inputs/createUniqueUser.json    method=POST    requestHeaders={'Content-Type' : 'application/json', 'Accept' : 'application/json'}    expectedStatusCode=201



