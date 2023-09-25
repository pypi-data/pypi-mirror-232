from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .EncounterParticipant import EncounterParticipant
from .II_InstanceIdentifier import II_InstanceIdentifier
from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Location import Location
from .ResponsibleParty import ResponsibleParty
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class EncompassingEncounter(Component_Model):
    """EncompassingEncounter"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self.effectiveTime = Element.Component(IVL_TS_IntervalOfTime, "effectiveTime", data, required=True, as_list=False)
        self.dischargeDispositionCode = Element.Component(CE_CodedWithEquivalents, "dischargeDispositionCode", data, as_list=False)
        self.responsibleParty = Element.Component(ResponsibleParty, "responsibleParty", data, as_list=False)
        self.encounterParticipant = Element.Component(EncounterParticipant, "encounterParticipant", data)
        self.location = Element.Component(Location, "location", data, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="ENC")
        self.moodCode = Element.Attribute("moodCode", data, fixed="EVN")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "effectiveTime": IVL_TS_IntervalOfTime.to_dict(),
            "dischargeDispositionCode": CE_CodedWithEquivalents.to_dict(),
            "responsibleParty": ResponsibleParty.to_dict(),
            "encounterParticipant": EncounterParticipant.to_dict(),
            "location": Location.to_dict(),
            "classCode": "ENC",
            "moodCode": "EVN"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "effectiveTime": IVL_TS_IntervalOfTime.to_dict_req(),
            "classCode": "ENC",
            "moodCode": "EVN"
        }
