from abc import abstractmethod, ABC
from mlflow import log_params


class AbstractMlModelJob(ABC):
    
    def __init__(self, params, *args, **kwargs):
        log_params(params)
    
    @abstractmethod
    def train(self, **kwargs):
        pass
    
    @abstractmethod
    def predicate(self, **kwargs):
        pass
    
    @abstractmethod
    def test(self, **kwargs):
        pass
