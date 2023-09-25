from .IVL_TS_IntervalOfTime import IVL_TS_IntervalOfTime
from .ST_String import ST_String
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class EN_GenericName(Component_Model):
    """AD"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.use = Element.Attribute("use", data)
        self.delimiter = Element.Component(ST_String, "delimiter", data)
        self.family = Element.Component(ST_String, "family", data)
        self.given = Element.Component(ST_String, "given", data)
        self.prefix = Element.Component(ST_String, "prefix", data)
        self.suffix = Element.Component(ST_String, "suffix", data)
        self.validTime = Element.Component(IVL_TS_IntervalOfTime, "validTime", data, as_list=False)

        """
        https://wiki.hl7.de/index.php?title=HL7_CDA_Core_Principles#Postal_Address_.28AD.29
        """

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "use": "",
            "delimiter": ST_String.to_dict(),
            "family": ST_String.to_dict(),
            "given": ST_String.to_dict(),
            "prefix": ST_String.to_dict(),
            "suffix": ST_String.to_dict(),
            "validTime": IVL_TS_IntervalOfTime.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "family": ST_String.to_dict_req(),
            "given": ST_String.to_dict_req()
        }
