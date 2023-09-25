from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .Component3 import Component3
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class StructuredBody(Component_Model):
    """StructuredBody"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.confidentialityCode = Element.Component(CE_CodedWithEquivalents, "confidentialityCode", data, as_list=False)
        self.languageCode = Element.Component(CS_CodedSimpleValue, "languageCode", data, as_list=False)
        self.component = Element.Component(Component3, "component", data, required=True)
        self.classCode = Element.Attribute("classCode", data, fixed="DOCBODY")
        self.moodCode = Element.Attribute("moodCode", data, fixed="EVN")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "confidentialityCode": CE_CodedWithEquivalents.to_dict(),
            "languageCode": CS_CodedSimpleValue.to_dict(),
            "component": Component3.to_dict(),
            "classCode": "DOCBODY",
            "moodCode": "EVN"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "component": Component3.to_dict_req(),
            "classCode": "DOCBODY",
            "moodCode": "EVN"
        }
