from abc import ABCMeta


class Serializable(object):
    """ Metaclass for any outer-API object """

    __metaclass__ = ABCMeta
    _id_attrs = ()

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def to_dict(self):
        data = dict()
        for key, value in self.__dict__.items():
            data[key] = value
        return data

    def __repr__(self):
        tmp = dict()
        for k, v in self.__dict__.items():
            tmp[k] = v
        return str(tmp)