from kfsd.apps.endpoints.handlers.common.base import BaseHandler
from kfsd.apps.endpoints.serializers.general.data import DataModelSerializer
from kfsd.apps.models.tables.general.data import Data
from kfsd.apps.core.utils.dict import DictUtils


def gen_data_handler(instance):
    handler = DataHandler(instance.identifier, False)
    qsData = DataModelSerializer(instance=instance)
    handler.setModelQSData(qsData.data)
    handler.setModelQS(instance)
    return handler


class DataHandler(BaseHandler):
    def __init__(self, dataIdentifier, isDBFetch):
        BaseHandler.__init__(
            self,
            serializer=DataModelSerializer,
            modelClass=Data,
            identifier=dataIdentifier,
            isDBFetch=isDBFetch,
        )

    def isTemplate(self):
        return DictUtils.get(self.getModelQSData(), "is_template")

    def isJson(self):
        return DictUtils.get(self.getModelQSData(), "is_json")

    def getVarFormat(self):
        return DictUtils.get(self.getModelQSData(), "var_format")

    def getTxtBody(self):
        return DictUtils.get(self.getModelQSData(), "txt_body")

    def getJsonBody(self):
        return DictUtils.get(self.getModelQSData(), "json_body")
