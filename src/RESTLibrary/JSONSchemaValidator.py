import json
import jsonschema
import sys
from .libcommons import libcommons

class JSONSchemaValidator:
    '''
   JSONSchemaValidator validates json schema against the json data file provided as parameter.
   '''

    schema_file_path = ''
    data_file_path = ''

    def get_node_path(path):
        '''
        get_node_path is function used to extract the json node path.
        '''
        str_path = ''
        for i in path:
            str_path = str_path + '/' + str(i)
        return str_path

    def ValidateSchema(schema, data):
        '''
        ValidateSchema is a function which validates schema file against the json data file provided as parameter to this function.
        It looks for the schema file in the same directory.
        '''
        __schema_str = None
        __data_str = None
        __flag = False
        __schema_flag = True
        __json_flag = True
        __err_arr = []
        try:
            if libcommons.path_exists(schema):
                with open(schema) as schema_file:
                    __schema_str = json.load(schema_file)
            elif type(schema) is str:
                __schema_str = json.loads(schema)
            elif schema.__class__.__name__ in ('dict', 'dotdict'):
                __schema_str = schema
        except Exception as e:
            __json_flag = False
            #print("JSON Data file not found", '-->', e.filename)
            print(str(e))
        try:
            if libcommons.path_exists(data):
                with open(data) as data_file:
                    __data_str = json.load(data_file)
            elif type(data) is str:
                __data_str = json.loads(data)
            elif data.__class__.__name__ in ('dict', 'dotdict'):
                __data_str = data
        except Exception as e:
            __schema_flag = False
            #print("JSON Schema file not found", '-->', se.filename)
            print(str(e))

        flag = __schema_flag and __json_flag
        if flag:
            try:
                error_count = 1
                validation = jsonschema.Draft7Validator(__schema_str)
                for error in sorted(validation.iter_errors(__data_str), key=str):
                    msg_str = ''
                    if error_count == 1:
                        #print('Schema Verification failed, following are the details:')
                        error_count = error_count + 1
                    if 'required' in error.message:
                        msg_str = 'Msg: Following node has a property missing from Schema.'
                    if msg_str == '':
                        __err_arr.append(
                            {'type': 'Schema Mismatch', 'path': JSONSchemaValidator.get_node_path(error.absolute_path),
                             'error': ''.join(error.message)})
                    else:
                        __err_arr.append(
                            {'type': 'Node missing', 'path': JSONSchemaValidator.get_node_path(error.absolute_path),
                             'error': ''.join(error.message)})

                #__err_arr = json.dumps(__err_arr, indent=4)
                return __err_arr
            except jsonschema.SchemaError as sExp:
                print('Bad Definition - Schema Definition Exception', sExp)
