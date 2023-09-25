from .AssignedAuthor import AssignedAuthor
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .TS_PointInTime import TS_PointInTime
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Author(Component_Model):
    """Author"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.functionCode = Element.Component(CE_CodedWithEquivalents, "functionCode", data, as_list=False)
        self.time = Element.Component(TS_PointInTime, "time", data, required=True, as_list=False)
        self.assignedAuthor = Element.Component(AssignedAuthor, "assignedAuthor", data, required=True, as_list=False)
        self.contextControlCode = Element.Attribute("contectControlCode", data, fixed="OP")
        self.typeCode = Element.Attribute("typeCode", data, fixed="AUT")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "functionCode": CE_CodedWithEquivalents.to_dict(),
            "time": TS_PointInTime.to_dict(),
            "assignedAuthor": AssignedAuthor.to_dict(),
            "contectControlCode": "OP",
            "typeCode": "AUT"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "time": TS_PointInTime.to_dict_req(),
            "assignedAuthor": AssignedAuthor.to_dict_req(),
            "contectControlCode": "OP",
            "typeCode": "AUT"
        }
