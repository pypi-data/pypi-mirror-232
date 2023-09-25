from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .MaintainedEntity import MaintainedEntity
from .SC_StringCode import SC_StringCode
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class AuthoringDevice(Component_Model):
    """AthoringDevice"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self.manufacturerModelName = Element.Component(SC_StringCode, "manufacturerModelName", data, as_list=False)
        self.softwareName = Element.Component(SC_StringCode, "softwareName", data, as_list=False)
        self.asMaintainedEntity = Element.Component(MaintainedEntity, "asMaintainedEntity", data)
        self.classCode = Element.Attribute("classCode", data, fixed="DEV")
        self.determinerCode = Element.Attribute("determinerCode", data, fixed="INSTANCE")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "manufacturerModelName": SC_StringCode.to_dict(),
            "softwareName": SC_StringCode.to_dict(),
            "asMaintainedEntity": MaintainedEntity.to_dict(),
            "classCode": "DEV",
            "determinerCode": "INSTANCE"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "code": CE_CodedWithEquivalents.to_dict_req(),
            "classCode": "DEV",
            "determinerCode": "INSTANCE"
        }
