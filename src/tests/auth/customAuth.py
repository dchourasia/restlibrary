from RESTLibrary.libcommons import libcommons

class customAuth:
    def set_authentication(self, _requestInfo):
        # here is the example how you can update the url to include custom auth token for your request
        _requestInfo.url += '&token=customAuthToken' if '?' in _requestInfo.url else '?token=customAuthToken'
        print(_requestInfo.url)
        # here is the example how you can update the request headers to include custom auth token for your request
        _requestInfo.requestHeaders['customAuthHeaderName'] = 'customAuthToken'
        print("requestHeaders['customAuthHeaderName'] = ", _requestInfo.requestHeaders['customAuthHeaderName'])

        # return final requestInfo object after all the updates
        return _requestInfo

