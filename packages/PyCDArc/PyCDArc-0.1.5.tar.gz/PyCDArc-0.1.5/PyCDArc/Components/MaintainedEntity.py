from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Person import Person
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class MaintainedEntity(Component_Model):
    """MaintainedEntity"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.effectiveTime = Element.Component(IVL_TS_IntervalOfTime, "effectiveTime", data, as_list=False)
        self.maintainingPerson = Element.Component(Person, "maintainingPerson", data, required=True, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="MNT")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "effectiveTime": IVL_TS_IntervalOfTime.to_dict(),
            "maintainingPerson": Person.to_dict(),
            "classCode": "MNT"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "maintainingPerson": Person.to_dict_req(),
            "classCode": "MNT"
        }
