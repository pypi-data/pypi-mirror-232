# IMPORT CIRCOLARI
from . import Organization
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class OrganizationPartOf(Component_Model):
    """OrganizationPartOf"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self.statusCode = Element.Component(CS_CodedSimpleValue, "statusCode", data, as_list=False)
        self.effectiveTime = Element.Component(IVL_TS_IntervalOfTime, "effectiveTime", data, as_list=False)
        self.wholeOrganization = Element.Component(Organization.Organization, "wholeOrganization", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="PART")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "statusCode": CS_CodedSimpleValue.to_dict(),
            "effectiveTime": IVL_TS_IntervalOfTime.to_dict(),
            "wholeOrganization": "Organization.Organization rec",
            "classCode": "PART"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "id": II_InstanceIdentifier.to_dict_req(),
            "classCode": "PART"
        }
