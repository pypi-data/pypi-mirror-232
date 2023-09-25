from .BirthPlace import BirthPlace
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .Guardian import Guardian
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .LanguageCommunication import LanguageCommunication
from .PN_PersonName import PN_PersonName
from .TS_PointInTime import TS_PointInTime
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Patient(Component_Model):
    """Patient"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data, as_list=False)
        self._name = Element.Component(PN_PersonName, "name", data)
        self.administrativeGenderCode = Element.Component(CE_CodedWithEquivalents, "administrativeGenderCode", data, as_list=False)
        self.birthTime = Element.Component(TS_PointInTime, "birthTime", data, as_list=False)
        self.maritalStatusCode = Element.Component(CE_CodedWithEquivalents, "maritalStatusCode", data, as_list=True)
        self.religiousAfflitionCode = Element.Component(CE_CodedWithEquivalents, "religiousAfflitionCode", data, as_list=True)
        self.raceCode = Element.Component(CE_CodedWithEquivalents, "raceCode", data, as_list=True)
        self.ethnicGroupCode = Element.Component(CE_CodedWithEquivalents, "ethnicGroupCode", data, as_list=True)
        self.guardian = Element.Component(Guardian, "guardian", data)
        self.birthplace = Element.Component(BirthPlace, "birthplace", data, as_list=False)
        self.languageCommunication = Element.Component(LanguageCommunication, "languageCommunication", data)
        self.classCode = Element.Attribute("classCode", data, fixed="PSN")
        self.determinerCode = Element.Attribute("determinerCode", data, fixed="INSTANCE")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "name": PN_PersonName.to_dict(),
            "administrativeGenderCode": CE_CodedWithEquivalents.to_dict(),
            "birthTime": TS_PointInTime.to_dict(),
            "maritalStatusCode": CE_CodedWithEquivalents.to_dict(),
            "religiousAfflitionCode": CE_CodedWithEquivalents.to_dict(),
            "raceCode": CE_CodedWithEquivalents.to_dict(),
            "ethnicGroupCode": CE_CodedWithEquivalents.to_dict(),
            "guardian": Guardian.to_dict(),
            "birthplace": BirthPlace.to_dict(),
            "languageCommunication": LanguageCommunication.to_dict(),
            "classCode": "PSN",
            "determinerCode": "INSTANCE"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "name": PN_PersonName.to_dict_req(),
            "administrativeGenderCode": CE_CodedWithEquivalents.to_dict_req(),
            "birthTime": TS_PointInTime.to_dict_req(),
            "classCode": "PSN",
            "determinerCode": "INSTANCE"
        }
