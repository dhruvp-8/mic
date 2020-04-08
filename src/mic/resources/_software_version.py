import logging
import modelcatalog
from mic._utils import first_line_new, get_api
from mic._mappings import *
from modelcatalog import ApiException
#Version: number
RESOURCE = "ModelVersion Version"


def create():
    first_line_new(RESOURCE)
    request = {}



class SoftwareVersionCli:
    name = RESOURCE

    def __init__(self):
        pass

    @staticmethod
    def get():
        # create an instance of the API class
        api, username = get_api()
        api_instance = modelcatalog.SoftwareVersionApi(api)
        try:
            # List all Person entities
            api_response = api_instance.softwareversions_get(username=username)
            return api_response
        except ApiException as e:
            raise e

    @staticmethod
    def push(request):
        configuration, username = get_api()
        api_instance = modelcatalog.SoftwareVersionApi(modelcatalog.ApiClient(configuration=configuration))
        try:
            api_response = api_instance.softwareversions_post(username, model=request)
        except ApiException as e:
            logging.error("Exception when calling ModelVersionConfigurationSetupApi->modelconfigurationsetups_post: %s\n" % e)
            raise e
        return api_response