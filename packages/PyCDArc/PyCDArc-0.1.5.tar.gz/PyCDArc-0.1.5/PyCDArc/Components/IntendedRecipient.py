from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .EN_GenericName import EN_GenericName
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class IntendedRecipient(Component_Model):
    """IntendedRecipient"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self._name = Element.Component(EN_GenericName, "name", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="MMAT")
        self.determinerCode = Element.Attribute("determinerCode", data, fixed="KIND")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "name": EN_GenericName.to_dict(),
            "classCode": "MMAT",
            "determinerCode": "KIND"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "name": EN_GenericName.to_dict_req(),
            "classCode": "MMAT",
            "determinerCode": "KIND"
        }
