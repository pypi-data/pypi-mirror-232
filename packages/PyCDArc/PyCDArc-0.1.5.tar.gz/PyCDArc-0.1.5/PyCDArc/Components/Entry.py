from .Act import Act
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .Encounter import Encounter
from .II_InstanceIdentifier import II_InstanceIdentifier
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Observation import Observation
from .ObservationMedia import ObservationMedia
from .Organizer import Organizer
from .Procedure import Procedure
from .RegionOfInterest import RegionOfInterest
from .SubstanceAdministration import SubstanceAdministration
from .Supply import Supply
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Entry(Component_Model):
    """Entry"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.act = Element.Component(Act, "act", data, as_list=False)
        self.encounter = Element.Component(Encounter, "encounter", data, as_list=False)
        self.observation = Element.Component(Observation, "observation", data, as_list=False)
        self.observationMedia = Element.Component(ObservationMedia, "observationMedia", data, as_list=False)
        self.organizer = Element.Component(Organizer, "organizer", data, as_list=False)
        self.procedure = Element.Component(Procedure, "procedure", data, as_list=False)
        self.regionOfInterest = Element.Component(RegionOfInterest, "regionOfInterest", data, as_list=False)
        self.substanceAdministration = Element.Component(SubstanceAdministration, "substanceAdministration", data, as_list=False)
        self.supply = Element.Component(Supply, "supply", data, as_list=False)
        self.contextConductionInd = Element.Attribute("contextConductionInd", data)
        self.typeCode = Element.Attribute("typeCode", data, default="COMP")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "act": Act.to_dict(),
            "encounter": Encounter.to_dict(),
            "observation": Observation.to_dict(),
            "observationMedia": ObservationMedia.to_dict(),
            "organizer": Organizer.to_dict(),
            "procedure": Procedure.to_dict(),
            "regionOfInterest": RegionOfInterest.to_dict(),
            "substanceAdministration": SubstanceAdministration.to_dict(),
            "supply": Supply.to_dict(),
            "contextConductionInd": "",
            "typeCode": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "observation": Observation.to_dict_req()
        }
