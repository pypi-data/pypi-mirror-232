from .TEL_TelecomincationAddress import TEL_TelecomincationAddress
from ..Core import Elements as Element
from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class ED_EncapsulatedData(Component_Model):
    """ED_EncapsulatedData"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        self.mediaType = Element.Attribute("mediaType", data)
        self.representation = Element.Attribute("representation", data)
        self.reference = Element.Component(TEL_TelecomincationAddress, "reference", data)
        self.thumbnail = Element.Component(ED_EncapsulatedData, "thumbnail", data)

        if self.reference is None and self.thumbnail is None:
            try:
                self.text = data["text"]
            except:
                raise InvalidGivenValue("Text Needed")

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "mediaType": "",
            "representation": "",
            "reference": TEL_TelecomincationAddress.to_dict(),
            "thumbnail": "ED_EncapsulatedData rec",
            "text": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "text": ""
        }
