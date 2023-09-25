from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class SC_StringCode(Component_Model):
    """SC_StringCode"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        try:
            self.text = data["text"]
        except:
            raise InvalidGivenValue("Text Needed")

        self.code = Element.Attribute("code", data)
        self.codeSystem = Element.Attribute("codeSystem", data)
        self.codeSystemName = Element.Attribute("codeSystemName", data)
        self.codeSystemVersion = Element.Attribute("codeSystemVersion", data)
        self.displayName = Element.Attribute("displayName", data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "text": "",
            "code": "",
            "codeSystem": "",
            "codeSystemName": "",
            "codeSystemVersion": "",
            "displayName": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "text": ""
        }
