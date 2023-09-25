from .AD_PostalAddress import AD_PostalAddress
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Organization import Organization
from .Patient import Patient
from .TEL_TelecomincationAddress import TEL_TelecomincationAddress
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class PatientRole(Component_Model):
    """PatientRole"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data, required=True)
        self.addr = Element.Component(AD_PostalAddress, "addr", data)
        self.telecom = Element.Component(TEL_TelecomincationAddress, "telecom", data)
        self.patient = Element.Component(Patient, "patient", data, as_list=False)
        self.providerOrganization = Element.Component(Organization, "providerOrganization", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="PAT")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "addr": AD_PostalAddress.to_dict(),
            "telecom": TEL_TelecomincationAddress.to_dict(),
            "patient": Patient.to_dict(),
            "providerOrganization": Organization.to_dict(),
            "classCode": "PAT"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "id": II_InstanceIdentifier.to_dict_req(),
            "patient": Patient.to_dict_req(),
            "classCode": "PAT"
        }
