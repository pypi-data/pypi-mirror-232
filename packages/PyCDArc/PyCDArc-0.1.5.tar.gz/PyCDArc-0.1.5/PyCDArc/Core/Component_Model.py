"""Component Class Model"""
from abc import abstractmethod


class Component_Model:
    """Component_Model"""
    name: str
    value: str | None

    @classmethod
    @abstractmethod
    def to_dict(cls):
        """to_dict"""

    @classmethod
    @abstractmethod
    def to_dict_req(cls):
        """to_dict"""
