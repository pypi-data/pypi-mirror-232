from .AD_PostalAddress import AD_PostalAddress
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Organization import Organization
from .Person import Person
from .TEL_TelecomincationAddress import TEL_TelecomincationAddress
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class AssociatedEntity(Component_Model):
    """AssociatedEntity"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self.addr = Element.Component(AD_PostalAddress, "addr", data)
        self.telecom = Element.Component(TEL_TelecomincationAddress, "telecom", data)
        self.associatedPerson = Element.Component(Person, "associatedPerson", data, as_list=False)
        self.scopingOrganization = Element.Component(Organization, "scopingOrganization", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, required=True)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "addr": AD_PostalAddress.to_dict(),
            "telecom": TEL_TelecomincationAddress.to_dict(),
            "associatedPerson": Person.to_dict(),
            "scopingOrganization": Organization.to_dict(),
            "classCode": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "code": CE_CodedWithEquivalents.to_dict(),
            "classCode": ""
        }
