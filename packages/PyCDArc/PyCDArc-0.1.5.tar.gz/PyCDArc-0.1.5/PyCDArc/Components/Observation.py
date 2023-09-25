# IMPORT CIRCOLARI
from . import EntryRelationship
from .Author import Author
from .CD_ConceptDescriptor import CD_ConceptDescriptor
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .ED_EncapsulatedData import ED_EncapsulatedData
from .II_InstanceIdentifier import II_InstanceIdentifier
from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .Informant12 import Informant12
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Participant2 import Participant2
from .Performer2 import Performer2
from .Precondition import Precondition
from .Reference import Reference
from .ReferenceRange import ReferenceRange
from .ST_String import ST_String
from .Specimen import Specimen
from .Subject import Subject
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Observation(Component_Model):
    """Observation"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.code = Element.Component(CD_ConceptDescriptor, "code", data, required=True, as_list=False)
        self.derivationExpr = Element.Component(ST_String, "derivationExpr", data, as_list=False)
        self._text = Element.Component(ED_EncapsulatedData, "text", data, as_list=False)
        self.statusCode = Element.Component(CS_CodedSimpleValue, "statusCode", data, as_list=False)
        self.effectiveTime = Element.Component(IVL_TS_IntervalOfTime, "effectiveTime", data, as_list=False)
        self.priorityCode = Element.Component(CE_CodedWithEquivalents, "priorityCode", data, as_list=False)
        self.repeatNumber = Element.Component(IVL_TS_IntervalOfTime, "repeatNumber", data)  # dovrebbe essere IVLINT
        self.languageCode = Element.Component(CS_CodedSimpleValue, "languageCode", data, as_list=False)
        self.value = Element.Component(CS_CodedSimpleValue, "value", data)
        self.interpretationCode = Element.Component(CE_CodedWithEquivalents, "interpretationCode", data)
        self.methodCode = Element.Component(CE_CodedWithEquivalents, "methodCode", data)
        self.targetSiteCode = Element.Component(CD_ConceptDescriptor, "targetSiteCode", data)
        self.subject = Element.Component(Subject, "subject", data, as_list=False)
        self.specimen = Element.Component(Specimen, "specimen", data)
        self.performer = Element.Component(Performer2, "performer", data)
        self.author = Element.Component(Author, "author", data)
        self.informant = Element.Component(Informant12, "Name", data)
        self.participant = Element.Component(Participant2, "participant", data)
        self.entryRelationship = Element.Component(EntryRelationship.EntryRelationship, "entryRelationship", data)
        self.reference = Element.Component(Reference, "reference", data)
        self.precondition = Element.Component(Precondition, "precondition", data)
        self.referenceRange = Element.Component(ReferenceRange, "referenceRange", data)
        self.classCode = Element.Attribute("classCode", data, required=True)
        self.moodCode = Element.Attribute("moodCode", data, required=True)
        self.negationInd = Element.Attribute("negationInd", data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "code": CD_ConceptDescriptor.to_dict(),
            "derivationExpr": ST_String.to_dict(),
            "text": ED_EncapsulatedData.to_dict(),
            "statusCode": CS_CodedSimpleValue.to_dict(),
            "effectiveTime": IVL_TS_IntervalOfTime.to_dict(),
            "priorityCode": CE_CodedWithEquivalents.to_dict(),
            "repeatNumber": IVL_TS_IntervalOfTime.to_dict(),
            "languageCode": CS_CodedSimpleValue.to_dict(),
            "value": CS_CodedSimpleValue.to_dict(),
            "interpretationCode": CE_CodedWithEquivalents.to_dict(),
            "methodCode": CE_CodedWithEquivalents.to_dict(),
            "targetSiteCode": CD_ConceptDescriptor.to_dict(),
            "subject": Subject.to_dict(),
            "specimen": Specimen.to_dict(),
            "performer": Performer2.to_dict(),
            "author": Author.to_dict(),
            "Name": Informant12.to_dict(),
            "participant": Participant2.to_dict(),
            "entryRelationship": "EntryRelationship.EntryRelationship.to_dict() rec",
            "reference": Reference.to_dict(),
            "precondition": Precondition.to_dict(),
            "referenceRange": ReferenceRange.to_dict(),
            "classCode": "",
            "moodCode": "",
            "negationInd": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "code": CD_ConceptDescriptor.to_dict_req(),
            "classCode": "",
            "moodCode": ""
        }
