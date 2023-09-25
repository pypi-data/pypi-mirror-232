from .II_InstanceIdentifier import II_InstanceIdentifier


class InfrastructureRootTypeId(II_InstanceIdentifier):
    """InfrastructureRootTypeId"""

    def __init__(self, name: str, data: dict):
        data["root"] = "2.16.840.1.113883.1.3"
        II_InstanceIdentifier.__init__(self, name, data)

    @classmethod
    def to_dict(cls):
        """to_dict"""
        return {
            "root": "2.16.840.1.113883.1.3",
            "extension": ""
        }

    @classmethod
    def to_dict_req(cls):
        """to_dict"""
        return {
            "root": "2.16.840.1.113883.1.3"
        }
