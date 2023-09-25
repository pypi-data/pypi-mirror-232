from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .LabeledDrug import LabeledDrug
from .Material import Material
from .Organization import Organization
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class ManufacturedProduct(Component_Model):
    """ManufacturedProduct"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.manufacturedLabeledDrug = Element.Component(LabeledDrug, "manufacturedLabeledDrug", data, as_list=False)
        self.manufacturedMaterial = Element.Component(Material, "manufacturedMaterial", data, as_list=False)
        self.manufacturerOrganization = Element.Component(Organization, "manufacturerOrganization", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="MANU")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "manufacturedLabeledDrug": LabeledDrug.to_dict(),
            "manufacturedMaterial": Material.to_dict(),
            "manufacturerOrganization": Organization.to_dict(),
            "classCode": "MANU"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "manufacturedLabeledDrug": LabeledDrug.to_dict_req(),
            "classCode": "MANU"
        }
