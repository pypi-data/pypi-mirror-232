from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class INT_IntegerNumber(Component_Model):
    """INT_IntegerNumber"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.value = Element.Attribute("value", data, required=True)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "value": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "value": ""
        }
