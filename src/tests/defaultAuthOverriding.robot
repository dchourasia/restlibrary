*** Settings ***
Library         json
Library         OperatingSystem
Library         Collections
Library         String
Library         DateTime
Resource        ${EXECDIR}/auth/MyAuth.robot
Library         RESTLibrary     authType=MyAuth.set my auth token


*** Variables ***
${base-url}=        https://reqres.in/api
${username}=        resttest
${password}=        Password1

*** Test Cases ***

Get all users
#    this request will automatically use "MyAuth.set my auth token" as authType since we have initiated RESTLibrary with authType overriding
    Make HTTP Request   my-first-request    ${base-url}/users?page=2

Get all users with basic auth
#    this request will automatically use "MyAuth.set my auth token" as authType since we have initiated RESTLibrary with authType overriding
    Make HTTP Request   my-first-request    ${base-url}/users?page=2        authType=Basic