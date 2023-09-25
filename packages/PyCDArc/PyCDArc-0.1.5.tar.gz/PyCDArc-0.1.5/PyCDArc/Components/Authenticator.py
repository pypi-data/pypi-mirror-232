from .AssignedEntity import AssignedEntity
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .TS_PointInTime import TS_PointInTime
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Authenticator(Component_Model):
    """Authenticator"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.time = Element.Component(TS_PointInTime, "time", data, required=False, as_list=False)
        self.signatureCode = Element.Component(CS_CodedSimpleValue, "signatureCode", data, required=True, as_list=False)
        self.assignedEntity = Element.Component(AssignedEntity, "assignedEntity", data, required=True, as_list=False)
        self.typeCode = Element.Attribute("typeCode", data, fixed="AUTHEN")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "time": TS_PointInTime.to_dict(),
            "signatureCode": CS_CodedSimpleValue.to_dict(),
            "assignedEntity": AssignedEntity.to_dict(),
            "typeCode": "AUTHEN"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "signatureCode": CS_CodedSimpleValue.to_dict_req(),
            "assignedEntity": AssignedEntity.to_dict_req(),
            "typeCode": "AUTHEN"
        }
