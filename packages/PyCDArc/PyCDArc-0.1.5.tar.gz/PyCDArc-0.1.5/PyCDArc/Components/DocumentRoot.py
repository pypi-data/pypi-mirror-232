from .ClinicalDocument import ClinicalDocument
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class DocumentRoot(Component_Model):
    """DocumentRoot"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.xMLNSPrefixMap = Element.Attribute("xMLNSPrefixMap", data)
        self.xSlSchemaLocation = Element.Attribute("xSlSchemaLocation", data)
        self.clinicalDocument = Element.Component(ClinicalDocument, "clinicalDocument", data, as_list=False)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "xMLNSPrefixMap": "",
            "xSlSchemaLocation": "",
            "clinicalDocument": ClinicalDocument.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "clinicalDocument": ClinicalDocument.to_dict()
        }
