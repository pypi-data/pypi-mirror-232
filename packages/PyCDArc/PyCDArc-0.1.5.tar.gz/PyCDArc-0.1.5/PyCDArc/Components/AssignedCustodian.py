from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .CustodianOrganization import CustodianOrganization
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class AssignedCustodian(Component_Model):
    """AssignedCustodian"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.representedCustodianOrganization = Element.Component(CustodianOrganization, "representedCustodianOrganization", data, required=True, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="ASSIGNED")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "representedCustodianOrganization": CustodianOrganization.to_dict(),
            "classCode": "ASSIGNED"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "representedCustodianOrganization": CustodianOrganization.to_dict_req(),
            "classCode": "ASSIGNED"
        }
