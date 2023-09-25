"""CDA Component Utils"""
from .Exceptions import InvalidGivenValue, InvalidGivenSubelementData


class Attribute:
    """ XML Attributes Class """

    def __new__(cls, name: str, data: dict, required: bool = False, fixed: str = '', default: str | None = '') -> str | None:
        try:
            if not fixed:
                return data[name]
            else:
                return data[name] if data[name] == fixed else default
                # return data[name]
        except Exception as error:
            if required and not default:
                raise InvalidGivenValue(f"Something went wrong generating {name}") from error
            elif default:
                return default
            return None


class Component:
    """ XML Component Class """

    def __new__(cls, class_name: type, name: str, data: dict, required: bool = False, as_list: bool = True):
        try:
            if isinstance(data[name], dict):
                return class_name(name, data[name])
            elif isinstance(data[name], list) and as_list:
                return [class_name(name, elem) for elem in data[name]]
            else:
                if as_list:
                    raise InvalidGivenSubelementData(f"{name} of type {class_name.__class__} can't be listed")
                else:
                    raise InvalidGivenSubelementData(f"{name} of type {class_name.__class__} must be dict or list")
        except Exception as error:
            if required:
                raise InvalidGivenSubelementData(f"Something went wrong generating {name} of type {class_name.__class__}") from error
            return None
