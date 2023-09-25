# IMPORT CIRCOLARI
from . import Act
from . import Organizer
from .BL_Boolean import BL_Boolean
from .CS_CodedSimpleValue import CS_CodedSimpleValue
from .Encounter import Encounter
from .II_InstanceIdentifier import II_InstanceIdentifier
from .INT_IntegerNumber import INT_IntegerNumber
from .InfrastructureRootTypeId import InfrastructureRootTypeId
from .Observation import Observation
from .ObservationMedia import ObservationMedia
from .Procedure import Procedure
from .RegionOfInterest import RegionOfInterest
from .SubstanceAdministration import SubstanceAdministration
from .Supply import Supply
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model


class Component4(Component_Model):
    """Component4"""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.realmCode = Element.Component(CS_CodedSimpleValue, "realmCode", data)
        self.typeId = Element.Component(InfrastructureRootTypeId, "typeId", data, as_list=False)
        self.templateId = Element.Component(II_InstanceIdentifier, "templateId", data)
        self.sequenceNumber = Element.Component(INT_IntegerNumber, "sequenceNumber", data, as_list=False)
        self.seperatableInd = Element.Component(BL_Boolean, "seperatableInd", data, as_list=False)
        self.act = Element.Component(Act.Act, "act", data, as_list=False)
        self.encounter = Element.Component(Encounter, "encounter", data, as_list=False)
        self.observation = Element.Component(Observation, "observation", data, as_list=False)
        self.observationMedia = Element.Component(ObservationMedia, "observationMedia", data, as_list=False)
        self.organizer = Element.Component(Organizer.Organizer, "organizer", data, as_list=False)
        self.procedure = Element.Component(Procedure, "procedure", data, as_list=False)
        self.regionOfInterest = Element.Component(RegionOfInterest, "regionOfInterest", data, as_list=False)
        self.substanceAdministration = Element.Component(SubstanceAdministration, "substanceAdministration", data, as_list=False)
        self.supply = Element.Component(Supply, "supply", data, as_list=False)
        self.contextConductionInd = Element.Attribute("contextConductionInd", data, fixed="true")
        self.typeCode = Element.Attribute("typeCode", data, fixed="COMP")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "realmCode": CS_CodedSimpleValue.to_dict(),
            "typeId": InfrastructureRootTypeId.to_dict(),
            "templateId": II_InstanceIdentifier.to_dict(),
            "sequenceNumber": INT_IntegerNumber.to_dict(),
            "act": Act.Act.to_dict(),
            "encounter": Encounter.to_dict(),
            "observation": Observation.to_dict(),
            "observationMedia": ObservationMedia.to_dict(),
            "organizer": "Organizer.Organizer.to_dict() rec",
            "procedure": Procedure.to_dict(),
            "regionOfInterest": RegionOfInterest.to_dict(),
            "substanceAdministration": SubstanceAdministration.to_dict(),
            "supply": Supply.to_dict(),
            "contextConductionInd": "true",
            "typeCode": "COMP"
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "contextConductionInd": "true",
            "typeCode": "COMP"
        }
