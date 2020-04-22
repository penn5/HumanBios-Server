from .serializable import Serializable


class ContextItem(Serializable):
    def to_dict(self):
        data = dict()
        for key, value in self.__dict__.items():
            if key in ('db', '_id_attrs'):
                continue
            if isinstance(value, ContextItem):
                data[key] = value.to_dict()
            else:
                data[key] = value
        return data

    @classmethod
    def from_dict(cls, values):
        obj = cls()
        for key, value in values.items():
            if isinstance(value, dict):
                obj[key] = cls.from_dict(value)
            else:
                obj[key] = value
        return obj


class Context(Serializable):
    @classmethod
    def from_json(cls, json_ish):
        obj = cls()
        for key, item in json_ish.items():
            if isinstance(item, dict):
                obj[key] = ContextItem.from_dict(item)
            else:
                obj[key] = item
        return obj