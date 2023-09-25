from ..Core.Component_Model import Component_Model
from ..Core.Exceptions import InvalidGivenValue


class ON_OrganisationName(Component_Model):
    """ON_OrganisationName"""

    def __init__(self, name: str, data: dict):
        if not data or data is None:
            raise InvalidGivenValue("Empty Data Set")

        self.name = name
        try:
            self.text = data["text"]
        except:
            raise InvalidGivenValue("Text Needed")

        # self.validTime = Element.Component("validTime", IVL_TS_IntervalOfTime, data)
        """ ????
            <name>The old hospital
                <validTime> 
                    <high value="20111231235959"/>
                </validTime>
            </name>
        """

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "text": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "text": ""
        }
