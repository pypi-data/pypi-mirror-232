# IMPORT CIRCOLARI
from . import EntryRelationship
from .Author import Author
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .ED_EncapsulatedData import ED_EncapsulatedData
from .II_InstanceIdentifier import II_InstanceIdentifier
from .Informant12 import Informant12
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Participant2 import Participant2
from .Performer2 import Performer2
from .Precondition import Precondition
from .Reference import Reference
from .Specimen import Specimen
from .Subject import Subject
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class ObservationMedia(Component_Model):
    """ObservationMedia"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data)
        self.languageCode = Element.Component(CS_CodedSimpleValue, "languageCode", data, as_list=False)
        self.value = Element.Component(ED_EncapsulatedData, "value", data, required=True, as_list=False)
        self.subject = Element.Component(Subject, "subject", data, as_list=False)
        self.specimen = Element.Component(Specimen, "specimen", data)
        self.perfomer = Element.Component(Performer2, "performer", data)
        self.author = Element.Component(Author, "author", data)
        self.informant = Element.Component(Informant12, "informant", data)
        self.participant = Element.Component(Participant2, "participant", data)
        self.entryRelationship = Element.Component(EntryRelationship.EntryRelationship, "entryRelationship", data)
        self.reference = Element.Component(Reference, "reference", data)
        self.precondition = Element.Component(Precondition, "precondition", data)
        self.classCode = Element.Attribute("classCode", data, required=True)
        self.iD1 = Element.Attribute("iD1", data)
        self.moodCode = Element.Attribute("moodCode", data, required=True)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "languageCode": CS_CodedSimpleValue.to_dict(),
            "value": ED_EncapsulatedData.to_dict(),
            "subject": Subject.to_dict(),
            "specimen": Specimen.to_dict(),
            "performer": Performer2.to_dict(),
            "author": Author.to_dict(),
            "informant": Informant12.to_dict(),
            "participant": Participant2.to_dict(),
            "entryRelationship": "EntryRelationship.EntryRelationship.to_dict() rec",
            "reference": Reference.to_dict(),
            "precondition": Precondition.to_dict(),
            "classCode": "",
            "iD1": "",
            "moodCode": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "value": ED_EncapsulatedData.to_dict_req(),
            "classCode": "",
            "moodCode": ""
        }
