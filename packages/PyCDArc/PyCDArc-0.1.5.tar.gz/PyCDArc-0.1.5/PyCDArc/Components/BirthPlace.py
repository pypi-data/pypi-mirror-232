from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Place import Place
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class BirthPlace(Component_Model):
    """BirthPlace"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.tempalteId = Element.Component(II_InstanceIdentifier, "tempalteId", data)
        self.place = Element.Component(Place, "place", data, required=True, as_list=False)
        self.classCode = Element.Attribute("classCode", data, fixed="BIRTHPL")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "tempalteId": II_InstanceIdentifier.to_dict(),
            "place": Place.to_dict(),
            "classCode": "BIRTHPL"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "place": Place.to_dict_req(),
            "classCode": "BIRTHPL"
        }
