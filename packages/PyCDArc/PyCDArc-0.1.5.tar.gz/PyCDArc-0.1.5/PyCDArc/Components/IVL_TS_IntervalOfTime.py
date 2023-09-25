from .INT_IntegerNumber import INT_IntegerNumber
from .PQ_PhysicalQuantities import PQ_PhysicalQuantities
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class IVL_TS_IntervalOfTime(Component_Model):
    """IVL_TS_IntervalOfTime"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.low = Element.Component(INT_IntegerNumber, "low", data)
        self.high = Element.Component(INT_IntegerNumber, "high", data)
        self.center = Element.Component(INT_IntegerNumber, "center", data)
        self.width = Element.Component(PQ_PhysicalQuantities, "width", data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "low": INT_IntegerNumber.to_dict(),
            "high": INT_IntegerNumber.to_dict(),
            "center": INT_IntegerNumber.to_dict(),
            "width": PQ_PhysicalQuantities.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "low": INT_IntegerNumber.to_dict_req(),
            "high": INT_IntegerNumber.to_dict_req()
        }
