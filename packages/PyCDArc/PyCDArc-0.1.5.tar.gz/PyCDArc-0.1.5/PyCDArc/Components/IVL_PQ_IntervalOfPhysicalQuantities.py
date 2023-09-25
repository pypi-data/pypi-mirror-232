from .INT_IntegerNumber import INT_IntegerNumber
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class IVL_PQ_IntervalOfPhysicalQuantities(Component_Model):
    """IVL_PQ_IntervalOfPhysicalQuantities"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.low = Element.Component(INT_IntegerNumber, "low", data)
        self.high = Element.Component(INT_IntegerNumber, "high", data)
        self.center = Element.Component(INT_IntegerNumber, "center", data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "low": INT_IntegerNumber.to_dict(),
            "high": INT_IntegerNumber.to_dict(),
            "center": INT_IntegerNumber.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "low": INT_IntegerNumber.to_dict_req(),
            "high": INT_IntegerNumber.to_dict_req()
        }
