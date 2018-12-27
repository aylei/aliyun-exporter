from aliyunsdkcore.request import RpcRequest
class QueryProjectMetaRequest(RpcRequest):

    def __init__(self):
        RpcRequest.__init__(self, 'Cms', '2018-03-08', 'QueryProjectMeta','cms')

    def get_Labels(self):
        return self.get_query_params().get('Labels')

    def set_Labels(self,Labels):
        self.add_query_param('Labels',Labels)

    def get_PageNumber(self):
        return self.get_query_params().get('PageNumber')

    def set_PageNumber(self,PageNumber):
        self.add_query_param('PageNumber',PageNumber)

    def get_PageSize(self):
        return self.get_query_params().get('PageSize')

    def set_PageSize(self,PageSize):
        self.add_query_param('PageSize',PageSize)
