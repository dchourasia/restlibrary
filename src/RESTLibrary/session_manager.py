from .libcommons import libcommons
import json
import base64
import traceback

UserNamePasswordMissingException = 'username or password not provided'

class session_manager:
    xciStore = {}
    jwtStore = {}
    casTgtStore = {}

    def Process_Authentication(self, _requestInfo):
        try:

            if _requestInfo.authType.upper() == "BASIC":
                    self.Check_If_Username_And_Password_Provided(_requestInfo)
                    _requestInfo.requestHeaders['Authorization'] = 'Basic ' + str(base64.b64encode((_requestInfo.username + ':' + _requestInfo.password).encode('ascii')).decode('utf-8'))
                    print(_requestInfo.requestHeaders['Authorization'])

            elif _requestInfo.authType.upper() == "NOAUTH":
                if 'Authorization' in _requestInfo.requestHeaders:
                    del _requestInfo.requestHeaders['Authorization']
            else:
                # custom auth handling
                _requestInfo = libcommons.run_keyword(_requestInfo.authType, _requestInfo)

        except Exception as e:
            if UserNamePasswordMissingException in e.args[0]:
                print(e.args[0])
            else:
                print(traceback.format_exc())
            raise e
        return _requestInfo

    def Check_If_Username_And_Password_Provided(self, _requestInfo):
        if _requestInfo.username is None or _requestInfo.password is None:
            raise Exception('username or password not provided, please set the variables ${' + _requestInfo.username_var + '} and ${' + _requestInfo.password_var + '} beforehand or provide username and password parameters while making HTTP request.')

