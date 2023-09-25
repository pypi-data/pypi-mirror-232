from .AssignedEntity import AssignedEntity
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Performer2(Component_Model):
    """Performer2"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.time = Element.Component(IVL_TS_IntervalOfTime, "time", data, as_list=False)
        self.modeCode = Element.Component(CE_CodedWithEquivalents, "modeCode", data, as_list=False)
        self.assignedEntity = Element.Component(AssignedEntity, "assignedEntity", data, required=True, as_list=False)
        self.typeCode = Element.Attribute("typeCode", data, fixed="PRF")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "time": IVL_TS_IntervalOfTime.to_dict(),
            "modeCode": CE_CodedWithEquivalents.to_dict(),
            "assignedEntity": AssignedEntity.to_dict(),
            "typeCode": "PRF"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "assignedEntity": AssignedEntity.to_dict_req(),
            "typeCode": "PRF"
        }
