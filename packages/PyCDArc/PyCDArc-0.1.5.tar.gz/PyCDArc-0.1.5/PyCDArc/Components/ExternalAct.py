from .CD_ConceptDescriptor import CD_ConceptDescriptor
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .ED_EncapsulatedData import ED_EncapsulatedData
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class ExternalAct(Component_Model):
    """ExternalAct"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.code = Element.Component(CD_ConceptDescriptor, "code", data, as_list=False)
        self._text = Element.Component(ED_EncapsulatedData, "text", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, default="ACT")
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
            "classCode": "",
            "moodCode": "EVN"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "id": II_InstanceIdentifier.to_dict_req(),
            "text": ED_EncapsulatedData.to_dict_req(),
            "moodCode": "EVN"
        }
