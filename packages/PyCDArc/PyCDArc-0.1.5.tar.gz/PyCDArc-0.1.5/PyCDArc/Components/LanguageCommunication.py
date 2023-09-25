from .BL_Boolean import BL_Boolean
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class LanguageCommunication(Component_Model):
    """LanguageCommunication"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.languageCode = Element.Component(CS_CodedSimpleValue, "languageCode", data, as_list=False)
        self.modeCode = Element.Component(CE_CodedWithEquivalents, "modeCode", data, as_list=False)
        self.proficiencyLevelCode = Element.Component(CE_CodedWithEquivalents, "proficiencyLevelCode", data, as_list=True)
        self.preferenceInd = Element.Component(BL_Boolean, "preferenceInd", data, as_list=False)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "languageCode": CS_CodedSimpleValue.to_dict(),
            "modeCode": CE_CodedWithEquivalents.to_dict(),
            "proficiencyLevelCode": CE_CodedWithEquivalents.to_dict(),
            "preferenceInd": BL_Boolean.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "languageCode": CS_CodedSimpleValue.to_dict_req()
        }
