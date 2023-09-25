from .CD_ConceptDescriptor import CD_ConceptDescriptor
from .ST_String import ST_String
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class CE_CodedWithEquivalents(Component_Model):
    """CE_CodedWithEquivalents"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.code = Element.Attribute("code", data, required=True)
        self.codeSystem = Element.Attribute("codeSystem", data, required=True)
        self.codeSystemVersion = Element.Attribute("codeSystemVersion", data)
        self.displayName = Element.Attribute("displayName", data)
        self.codeSystemName = Element.Attribute("codeSystemName", data)
        self.originalText = Element.Component(ST_String, "originalText", data)
        self.translaction = Element.Component(CD_ConceptDescriptor, "translaction", data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "code": "",
            "codeSystem": "",
            "codeSystemVersion": "",
            "displayName": "",
            "codeSystemName": "",
            "originalText": ST_String.to_dict(),
            "translaction": CD_ConceptDescriptor.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "code": "",
            "codeSystem": ""
        }
