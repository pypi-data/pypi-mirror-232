from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .EncompassingEncounter import EncompassingEncounter
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Component1(Component_Model):
    """Component1"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.encompassingEncounter = Element.Component(EncompassingEncounter, "encompassingEncounter", data, required=True, as_list=False)
        self.typeCode = Element.Attribute("typeCode", data, fixed="COMP")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "encompassingEncounter": EncompassingEncounter.to_dict(),
            "typeCode": "COMP"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "encompassingEncounter": EncompassingEncounter.to_dict_req(),
            "typeCode": "COMP"
        }
