from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .ED_EncapsulatedData import ED_EncapsulatedData
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Entity(Component_Model):
    """Entity"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self.desc = Element.Component(ED_EncapsulatedData, "desc", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, default="ENT")
        self.determinerCode = Element.Attribute("determinerCode", data, fixed="INSTANCE")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "desc": ED_EncapsulatedData.to_dict(),
            "classCode": "",
            "determinerCode": "INSTANCE"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "id": II_InstanceIdentifier.to_dict_req(),
            "desc": ED_EncapsulatedData.to_dict_req(),
            "determinerCode": "INSTANCE"
        }
