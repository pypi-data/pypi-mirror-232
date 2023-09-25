from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class ST_String(Component_Model):
    """ST_String"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        try:
            self.text = data["text"]
        except:
            raise InvalidGivenValue("Text Needed")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "text": "",
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "text": "",
        }
