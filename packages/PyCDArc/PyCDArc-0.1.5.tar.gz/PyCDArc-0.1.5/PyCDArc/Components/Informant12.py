from .AssignedEntity import AssignedEntity
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .RelatedEntity import RelatedEntity
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Informant12(Component_Model):
    """Informant12"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.assignedEntity = Element.Component(AssignedEntity, "assignedEntity", data, as_list=False)
        self.relatedEntity = Element.Component(RelatedEntity, "relatedEntity", data, as_list=False)
        self.contextControlCode = Element.Attribute("contextControlCode", data, fixed="OP")
        self.typeCode = Element.Attribute("typeCode", data, fixed="INF")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "assignedEntity": AssignedEntity.to_dict(),
            "relatedEntity": RelatedEntity.to_dict(),
            "contextControlCode": "OP",
            "typeCode": "INF"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "assignedEntity": AssignedEntity.to_dict_req(),
            "relatedEntity": RelatedEntity.to_dict_req(),
            "contextControlCode": "OP",
            "typeCode": "INF"
        }
