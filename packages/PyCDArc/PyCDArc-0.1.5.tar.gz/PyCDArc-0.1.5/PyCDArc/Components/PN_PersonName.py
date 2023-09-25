from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .ST_String import ST_String
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class PN_PersonName(Component_Model):
    """PN_PersonName"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.given = Element.Component(ST_String, "given", data, required=True)
        self.family = Element.Component(ST_String, "family", data, required=True)
        self.validTime = Element.Component(IVL_TS_IntervalOfTime, "validTime", data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "given": ST_String.to_dict(),
            "family": ST_String.to_dict(),
            "validTime": IVL_TS_IntervalOfTime.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "given": ST_String.to_dict_req(),
            "family": ST_String.to_dict_req()
        }
