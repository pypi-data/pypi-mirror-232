from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .SpecimenRole import SpecimenRole
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Specimen(Component_Model):
    """Specimen"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.specimenRole = Element.Component(SpecimenRole, "specimenRole", data, required=True, as_list=False)
        self.typeCode = Element.Attribute("typeCode", data, fixed="SPC")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "specimenRole": SpecimenRole.to_dict(),
            "typeCode": "SPC"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "specimenRole": SpecimenRole.to_dict_req(),
            "typeCode": "SPC"
        }
