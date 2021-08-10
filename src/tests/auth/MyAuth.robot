*** Settings ***
Library         OperatingSystem
Library         Collections
Library         String
Library         DateTime

*** Keywords ***

set my auth token
    [Arguments]  ${request info}
    # here is the example how you can update the url to include custom auth token for your request
    ${request info.url}=    Set Variable    ${request info.url}&token=customAuthToken

    # here is the example how you can update the request headers to include custom auth token for your request
    Set To Dictionary   ${request info.requestHeaders}      customAuthHeaderName=customAuthToken

    # return final requestInfo object after all the updates
    [Return]  ${request info}
