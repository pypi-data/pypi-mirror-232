from .INT_IntegerNumber import INT_IntegerNumber
from ..Core import Elements as Element


class RegionOfInterestValue(INT_IntegerNumber):
    """RegionOfInterestValue"""

    def __init__(self, name: str, data: dict):
        self.unsorte = Element.Attribute("unsorted", data, default="True")
        INT_IntegerNumber.__init__(self, name, data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        int_dict = INT_IntegerNumber.to_dict()
        int_dict["unsorted"] = ""
        return int_dict

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return INT_IntegerNumber.to_dict_req()
