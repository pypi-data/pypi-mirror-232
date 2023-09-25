from collections import OrderedDict


class DICTfactory:
    def __init__(self, obj):
        self.obj = obj

    def to_dict(self):
        return self._to_dict(self.obj)

    def _to_dict(self, obj):
        if isinstance(obj, (int, float, str, bool)):
            return obj
        elif isinstance(obj, list):
            return [self._to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._to_dict(value) for key, value in obj.items()}
        elif "text" in dir(obj):
            return {"_text": obj.text}
        else:
            res = OrderedDict()
            for attr in obj.__dict__:
                if not attr.startswith("__") and attr != "to_dict" and attr != "to_dict_req" and attr != "name" and getattr(obj, attr) is not None:
                    index = attr[1:] if attr.startswith("_") else attr
                    if not isinstance(getattr(obj, attr), (str, int)):
                        res[index] = self._to_dict(getattr(obj, attr))
                    else:
                        res[f"__{index}"] = self._to_dict(getattr(obj, attr))
            return dict(res)
