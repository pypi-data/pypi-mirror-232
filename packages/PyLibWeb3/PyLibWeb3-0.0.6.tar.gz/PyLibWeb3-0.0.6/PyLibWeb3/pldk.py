class PyLibConfiguration:
    def __init__(self):
        self.versions = {}

    def configuration(self, version_required, version_of_library, name_of_library):
        if name_of_library in self.versions:
            return self.versions[name_of_library], version_required, name_of_library
        else:
            self.versions[name_of_library] = version_of_library
            return version_of_library, version_required, name_of_library

class PyLibraAPI:
    def loaded():
        return True

# Crear una instancia del PyLibConfiguration
pylib = PyLibConfiguration()
