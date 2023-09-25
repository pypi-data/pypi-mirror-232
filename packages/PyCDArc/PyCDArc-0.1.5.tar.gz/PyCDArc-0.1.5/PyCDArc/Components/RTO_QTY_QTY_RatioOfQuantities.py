from .INT_IntegerNumber import INT_IntegerNumber
from .PQ_PhysicalQuantities import PQ_PhysicalQuantities
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class RTO_QTY_QTY_RatioOfQuantities(Component_Model):
    """RTO_QTY_QTY_RatioOfQuantities"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.numerator = Element.Component(PQ_PhysicalQuantities, "numerator", data)
        if "unit" in data["denominator"]:
            self.denominator = Element.Component(PQ_PhysicalQuantities, "denominator", data)
        else:
            self.denominator = Element.Component(INT_IntegerNumber, "denominator", data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "numerator": PQ_PhysicalQuantities.to_dict(),
            "denominator_int": INT_IntegerNumber.to_dict(),
            "denominator_pq": PQ_PhysicalQuantities.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "numerator": PQ_PhysicalQuantities.to_dict_req()
        }
