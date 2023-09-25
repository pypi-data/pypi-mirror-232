from .ST_String import ST_String
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class AD_PostalAddress(Component_Model):
    """AD"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.use = Element.Attribute("use", data)
        self.streetAddressLine = Element.Component(ST_String, "streetAddressLine", data, as_list=False)
        self.city = Element.Component(ST_String, "city", data, as_list=False)
        self.postalCode = Element.Component(ST_String, "postalCode", data, as_list=False)
        self.country = Element.Component(ST_String, "country", data, as_list=False)

        """
        https://wiki.hl7.de/index.php?title=HL7_CDA_Core_Principles#Postal_Address_.28AD.29
        """

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "use": "",
            "streetAddressLine": ST_String.to_dict(),
            "city": ST_String.to_dict(),
            "postalCode": ST_String.to_dict(),
            "country": ST_String.to_dict()
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "streetAddressLine": ST_String.to_dict_req(),
            "city": ST_String.to_dict_req(),
            "postalCode": ST_String.to_dict_req()
        }
