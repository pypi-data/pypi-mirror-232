from .AssignedEntity import AssignedEntity
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Performer1(Component_Model):
    """Performer1"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.functionCode = Element.Component(CE_CodedWithEquivalents, "functionCode", data, as_list=False)
        self.time = Element.Component(IVL_TS_IntervalOfTime, "time", data, as_list=False)
        self.assignedEntity = Element.Component(AssignedEntity, "assignedEntity", data, required=True, as_list=False)
        self.typeId = Element.Attribute("typeCode", data, required=True)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "functionCode": CE_CodedWithEquivalents.to_dict(),
            "time": IVL_TS_IntervalOfTime.to_dict(),
            "assignedEntity": AssignedEntity.to_dict(),
            "typeCode": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "assignedEntity": AssignedEntity.to_dict_req(),
            "typeCode": ""
        }
