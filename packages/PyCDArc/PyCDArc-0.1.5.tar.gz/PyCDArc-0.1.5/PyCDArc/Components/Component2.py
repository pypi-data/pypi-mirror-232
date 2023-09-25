from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .NonXMLBody import NonXMLBody
from .StructuredBody import StructuredBody
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Component2(Component_Model):
    """Component2"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.nonXMLBody = Element.Component(NonXMLBody, "nonXMLBody", data, as_list=False)
        self.structuredBody = Element.Component(StructuredBody, "structuredBody", data, as_list=False)
        self.contextConductionInd = Element.Attribute("contextConductionInd", data, fixed="true")
        self.typeCode = Element.Attribute("typeCode", data, fixed="COMP")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "nonXMLBody": NonXMLBody.to_dict(),
            "structuredBody": StructuredBody.to_dict(),
            "contextConductionInd": "true",
            "typeCode": "COMP"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "structuredBody": StructuredBody.to_dict_req(),
            "contextConductionInd": "true",
            "typeCode": "COMP"
        }
