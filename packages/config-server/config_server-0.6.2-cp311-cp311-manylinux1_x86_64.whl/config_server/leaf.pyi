from config_server.node import ConfigNode as ConfigNode
from pydantic import RootModel

class ConfigLeaf(RootModel, ConfigNode):
    def edit_data_dict(self, data_dict: dict) -> None: ...
