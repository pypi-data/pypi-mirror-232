from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .RelatedSubject import RelatedSubject
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Subject(Component_Model):
    """Subject"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.awarenessCode = Element.Component(CE_CodedWithEquivalents, "awarenessCode", data, as_list=False)
        self.relatedSubject = Element.Component(RelatedSubject, "relatedSubject", data, required=True, as_list=False)
        self.contextControlCode = Element.Attribute("contextControlCode", data, fixed="OP")
        self.typeCode = Element.Attribute("typeCode", data, fixed="SBJ")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "awarenessCode": CE_CodedWithEquivalents.to_dict(),
            "relatedSubject": RelatedSubject.to_dict(),
            "contextControlCode": "OP",
            "typeCode": "SBJ"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "relatedSubject": RelatedSubject.to_dict_req(),
            "contextControlCode": "OP",
            "typeCode": "SBJ"
        }
