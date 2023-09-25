from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .PlayingEntity import PlayingEntity
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class SpecimenRole(Component_Model):
    """SpecimenRole"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.specimenPlayingEntity = Element.Component(PlayingEntity, "specimenPlayingEntity", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="SPEC")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "specimenPlayingEntity": PlayingEntity.to_dict(),
            "classCode": "SPEC"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "id": II_InstanceIdentifier.to_dict(),
            "classCode": "SPEC"
        }
