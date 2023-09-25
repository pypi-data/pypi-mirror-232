from .AssignedCustodian import AssignedCustodian
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Custodian(Component_Model):
    """Custodian"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.assignedCustodian = Element.Component(AssignedCustodian, "assignedCustodian", data, required=True, as_list=False)
        self.typeCode = Element.Attribute("typeCode", data, fixed="CST")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "assignedCustodian": AssignedCustodian.to_dict(),
            "typeCode": "CST"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "assignedCustodian": AssignedCustodian.to_dict_req(),
            "typeCode": "CST"
        }
