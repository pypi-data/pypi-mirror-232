from .AD_PostalAddress import AD_PostalAddress
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .SubjectPerson import SubjectPerson
from .TEL_TelecomincationAddress import TEL_TelecomincationAddress
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class RelatedSubject(Component_Model):
    """RelatedSubject"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self.addr = Element.Component(AD_PostalAddress, "addr", data)
        self.telecom = Element.Component(TEL_TelecomincationAddress, "telecom", data)
        self.subject = Element.Component(SubjectPerson, "subject", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, default="PRS")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "addr": AD_PostalAddress.to_dict(),
            "telecom": TEL_TelecomincationAddress.to_dict(),
            "subject": SubjectPerson.to_dict(),
            "classCode": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "code": CE_CodedWithEquivalents.to_dict()
        }
