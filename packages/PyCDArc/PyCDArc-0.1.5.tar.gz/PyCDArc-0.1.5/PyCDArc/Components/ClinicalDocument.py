from .Authenticator import Authenticator
from .Author import Author
from .Authorization import Authorization
from .CE_CodedWithEquivalents import CE_CodedWithEquivalents
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .Component1 import Component1
from .Component2 import Component2
from .Custodian import Custodian
from .DataEnterer import DataEnterer
from .DocumentationOf import DocumentationOf
from .II_InstanceIdentifier import II_InstanceIdentifier
from .INT_IntegerNumber import INT_IntegerNumber
from .InFulfillmentOf import InFulfillmentOf
from .Informant12 import Informant12
from .InformationRecipient import InformationRecipient
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .LegalAuthenticator import LegalAuthenticator
from .Participant1 import Participant1
from .RecordTarget import RecordTarget
from .RelatedDocument import RelatedDocument
from .ST_String import ST_String
from .TS_PointInTime import TS_PointInTime
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class ClinicalDocument(Component_Model):
    """ClinicalDocument"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, required=True, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.id = Element.Component(II_InstanceIdentifier, "id", data, required=True, as_list=False)
        self.code = Element.Component(CE_CodedWithEquivalents, "code", data, required=True, as_list=False)
        self.title = Element.Component(ST_String, "title", data, as_list=False)
        self.effectiveTime = Element.Component(TS_PointInTime, "effectiveTime", data, required=True, as_list=False)
        self.confidentialityCode = Element.Component(CE_CodedWithEquivalents, "confidentialityCode", data, required=True, as_list=False)
        self.languageCode = Element.Component(CS_CodedSimpleValue, "languageCode", data, as_list=False)
        self.setId = Element.Component(II_InstanceIdentifier, "setId", data, as_list=False)
        self.versionNumber = Element.Component(INT_IntegerNumber, "versionNumber", data, as_list=False)
        self.copyTime = Element.Component(TS_PointInTime, "copyTime", data, as_list=False)
        self.recordTarget = Element.Component(RecordTarget, "recordTarget", data, required=True)
        self.author = Element.Component(Author, "author", data, required=True)
        self.dataEnterer = Element.Component(DataEnterer, "dataEnterer", data, as_list=False)
        self.informant = Element.Component(Informant12, "informant", data)

        self.custodian = Element.Component(Custodian, "custodian", data, required=True, as_list=False)
        self.informationRecipient = Element.Component(InformationRecipient, "informationRecipient", data)
        self.legalAuthenticator = Element.Component(LegalAuthenticator, "legalAuthenticator", data, as_list=False)
        self.authenticator = Element.Component(Authenticator, "authenticator", data)
        self.participant = Element.Component(Participant1, "participant", data)
        self.inFulfillmentOf = Element.Component(InFulfillmentOf, "inFulfillmentOf", data)
        self.documentationOf = Element.Component(DocumentationOf, "documentationOf", data)
        self.relatedDocument = Element.Component(RelatedDocument, "relatedDocument", data)
        self.authorization = Element.Component(Authorization, "authorization", data)
        self.componentOf = Element.Component(Component1, "componentOf", data, as_list=False)
        self.component = Element.Component(Component2, "component", data, required=True, as_list=False)
        # self.classCode = Element.Attribute("classCode", data, fixed="DOCCLIN")
        # self.moodCode = Element.Attribute("moodCode", data, fixed="EVN")

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
            "effectiveTime": TS_PointInTime.to_dict(),
            "confidentialityCode": CE_CodedWithEquivalents.to_dict(),
            "languageCode": CS_CodedSimpleValue.to_dict(),
            "setId": II_InstanceIdentifier.to_dict(),
            "versionNumber": INT_IntegerNumber.to_dict(),
            "copyTime": TS_PointInTime.to_dict(),
            "recordTarget": RecordTarget.to_dict(),
            "author": Author.to_dict(),
            "dataEnterer": DataEnterer.to_dict(),
            "informant": Informant12.to_dict(),
            "custodian": Custodian.to_dict(),
            "informationRecipient": InformationRecipient.to_dict(),
            "legalAuthenticator": LegalAuthenticator.to_dict(),
            "authenticator": Authenticator.to_dict(),
            "participant": Participant1.to_dict(),
            "inFulfillmentOf": InFulfillmentOf.to_dict(),
            "documentationOf": DocumentationOf.to_dict(),
            "relatedDocument": RelatedDocument.to_dict(),
            "authorization": Authorization.to_dict(),
            "componentOf": Component1.to_dict(),
            "component": Component2.to_dict(),
            # "classCode": "DOCCLIN",
            # "moodCode": "EVN"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict_req(),
            "typeId": InfrastructureRootTypeId.to_dict_req(),
            "templateId": II_InstanceIdentifier.to_dict_req(),
            "id": II_InstanceIdentifier.to_dict_req(),
            "code": CE_CodedWithEquivalents.to_dict_req(),
            "effectiveTime": TS_PointInTime.to_dict_req(),
            "confidentialityCode": CE_CodedWithEquivalents.to_dict_req(),
            "languageCode": CS_CodedSimpleValue.to_dict_req(),
            "setId": II_InstanceIdentifier.to_dict_req(),
            "versionNumber": INT_IntegerNumber.to_dict_req(),
            "recordTarget": RecordTarget.to_dict_req(),
            "author": Author.to_dict_req(),
            "custodian": Custodian.to_dict_req(),
            "legalAuthenticator": LegalAuthenticator.to_dict_req(),
            "componentOf": Component1.to_dict_req(),
            "component": Component2.to_dict_req(),
            # "classCode": "DOCCLIN",
            # "moodCode": "EVN"
        }
