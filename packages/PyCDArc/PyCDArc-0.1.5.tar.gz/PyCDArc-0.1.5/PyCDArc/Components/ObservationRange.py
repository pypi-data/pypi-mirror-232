from .CD_ConceptDescriptor import CD_ConceptDescriptor
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .ED_EncapsulatedData import ED_EncapsulatedData
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .ST_String import ST_String
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class ObservationRange(Component_Model):
    """ObservationRange"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.code = Element.Component(CD_ConceptDescriptor, "code", data, as_list=False)
        self._text = Element.Component(ED_EncapsulatedData, "text", data, as_list=False)
        self._value = Element.Component(ST_String, "value", data, as_list=False)
        self.interpretationCode = Element.Component(CE_CodedWithEquivalents, "interpretationCode", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, default="OBS")
        self.moodCode = Element.Attribute("moodCode", data, fixed="EVN.CRT")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "code": CD_ConceptDescriptor.to_dict(),
            "text": ED_EncapsulatedData.to_dict(),
            "value": ST_String.to_dict(),
            "interpretationCode": CE_CodedWithEquivalents.to_dict(),
            "classCode": "",
            "moodCode": "EVN.CRT"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "code": CD_ConceptDescriptor.to_dict(),
            "text": ED_EncapsulatedData.to_dict(),
            "value": ST_String.to_dict(),
            "moodCode": "EVN.CRT"
        }
