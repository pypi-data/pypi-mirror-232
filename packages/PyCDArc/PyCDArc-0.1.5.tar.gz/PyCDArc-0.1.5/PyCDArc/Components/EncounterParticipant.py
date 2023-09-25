from .AssignedEntity import AssignedEntity
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class EncounterParticipant(Component_Model):
    """EncounterParticipant"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.time = Element.Component(II_InstanceIdentifier, "time", data, as_list=False)
        self.assignedEntity = Element.Component(AssignedEntity, "assignedEntity", data, required=True, as_list=False)
        self.typeCode = Element.Attribute("typeCode", data, required=True)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "time": II_InstanceIdentifier.to_dict(),
            "assignedEntity": AssignedEntity.to_dict(),
            "typeCode": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "assignedEntity": AssignedEntity.to_dict_req(),
            "typeCode": ""
        }
