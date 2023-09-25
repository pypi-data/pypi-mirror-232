from .CD_ConceptDescriptor import CD_ConceptDescriptor
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .ED_EncapsulatedData import ED_EncapsulatedData
from .II_InstanceIdentifier import II_InstanceIdentifier
from .INT_IntegerNumber import INT_IntegerNumber
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class ParentDocument(Component_Model):
    """ParentDocument"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data, required=True)
        self.code = Element.Component(CD_ConceptDescriptor, "code", data, as_list=False)
        self._text = Element.Component(ED_EncapsulatedData, "text", data, as_list=False)
        self.setId = Element.Component(II_InstanceIdentifier, "setId", data, as_list=False)
        self.versionNumber = Element.Component(INT_IntegerNumber, "versionNumber", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="DOCCLIN")
        self.moodCode = Element.Attribute("moodCode", data, fixed="EVN")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "code": CD_ConceptDescriptor.to_dict(),
            "text": ED_EncapsulatedData.to_dict(),
            "setId": II_InstanceIdentifier.to_dict(),
            "versionNumber": INT_IntegerNumber.to_dict(),
            "classCode": "DOCCLIN",
            "moodCode": "EVN"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "id": II_InstanceIdentifier.to_dict_req(),
            "classCode": "DOCCLIN",
            "moodCode": "EVN"
        }
