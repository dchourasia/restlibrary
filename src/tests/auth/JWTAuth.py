import base64, jwt
from robot.libraries.BuiltIn import BuiltIn

class JWTAuth:
    def set_authentication(self, _requestInfo):
        _builtIn = BuiltIn()
        jwtClientId = _builtIn.get_variable_value('${jwtClientId}')
        jwtClientSecret = _builtIn.get_variable_value('${jwtClientSecret}')
        if jwtClientId and jwtClientSecret:
            encodedSecret = base64.b64encode(bytes(jwtClientSecret, "utf-8"))
            jwtToken = jwt.encode({'clientID': jwtClientId}, encodedSecret, algorithm='HS256').decode('utf-8')
            _requestInfo.url += '&token=' + jwtToken if '?' in _requestInfo.url else '?token=' + jwtToken
        else:
            raise Exception('Please provide jwtClientId and jwtClientSecret while making HTTP Request')

        # return final requestInfo object after all the updates
        return _requestInfo