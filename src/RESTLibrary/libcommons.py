from robot.libraries.BuiltIn import BuiltIn
import os


class libcommons:
    robotBuiltIn = BuiltIn()


    def get_variable(name):
        return libcommons.robotBuiltIn.get_variable_value(name)

    def run_keyword(name, *kwargs, library=None, resource=None):
        if library:
            libcommons.robotBuiltIn.import_library(library)
        if resource:
            libcommons.robotBuiltIn.import_resource(resource)
        return libcommons.robotBuiltIn.run_keyword(name, *kwargs)

    def path_exists(path):
        result=False
        try:
            result = os.path.exists(libcommons.sanitizeFilePath(path))
        except:
            a=1
        return result

    def sanitizeFilePath(path):
        if path:
            path = path.replace('\t', '\\t').replace('\r', '\\r')
        return path



