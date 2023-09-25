from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .PN_PersonName import PN_PersonName
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Person(Component_Model):
    """Person"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self._name = Element.Component(PN_PersonName, "name", data)
        self.classCode = Element.Attribute("classCode", data, fixed="PSN")
        self.determinerCode = Element.Attribute("determinerCode", data, fixed="INSTANCE")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "name": PN_PersonName.to_dict(),
            "classCode": "PSN",
            "determinerCode": "INSTANCE"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "name": PN_PersonName.to_dict_req(),
            "classCode": "PSN",
            "determinerCode": "INSTANCE"
        }
