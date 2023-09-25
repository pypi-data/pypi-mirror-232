from .Author import Author
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .Component5 import Component5
from .Entry import Entry
from .II_InstanceIdentifier import II_InstanceIdentifier
from .Informant12 import Informant12
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .ST_String import ST_String
from .Subject import Subject
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Section(Component_Model):
    """Section"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data, as_list=False)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, as_list=False)
        self.title = Element.Component(ST_String, "title", data, as_list=False)
        self._text = Element.Component(ST_String, "text", data, as_list=False)
        self.confidentialityCode = Element.Component(CE_CodedWithEquivalents, "confidentialityCode", data, as_list=False)
        self.languageCode = Element.Component(CS_CodedSimpleValue, "languageCode", data, as_list=False)
        self.subject = Element.Component(Subject, "sibject", data, as_list=False)
        self.author = Element.Component(Author, "author", data)
        self.informant = Element.Component(Informant12, "informant", data)
        self.entry = Element.Component(Entry, "entry", data)
        self.component = Element.Component(Component5, "component", data)
        self.classCode = Element.Attribute("classCode", data, fixed="DOCSECT")
        self.iD1 = Element.Attribute("iD1", data)
        self.moodCode = Element.Attribute("moodCode", data, fixed="EVN")

        # manca test omesso per definizione

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "id": II_InstanceIdentifier.to_dict(),
            "code": CE_CodedWithEquivalents.to_dict(),
            "title": ST_String.to_dict(),
            "text": ST_String.to_dict(),
            "confidentialityCode": CE_CodedWithEquivalents.to_dict(),
            "languageCode": CS_CodedSimpleValue.to_dict(),
            "sibject": Subject.to_dict(),
            "author": Author.to_dict(),
            "informant": Informant12.to_dict(),
            "entry": Entry.to_dict(),
            "component": "Component5.to_dict() rec",
            "classCode": "DOCSECT",
            "iD1": "",
            "moodCode": "EVN"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "code": CE_CodedWithEquivalents.to_dict_req(),
            "title": ST_String.to_dict_req(),
            "text": ST_String.to_dict(),
            "classCode": "DOCSECT",
            "moodCode": "EVN"
        }
