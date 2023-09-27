from abc import ABC, abstractclassmethod,abstractproperty


class TypeModel(ABC):

    @abstractclassmethod
    def from_json(object_json: dict):
        raise NotImplementedError
    
    @abstractproperty
    def body():
        raise NotImplementedError
    
    @abstractproperty
    def params():
        raise NotImplementedError