from abc import ABC, abstractmethod
import numpy as np


class AbstractFunction(ABC):
    parameters = {}

    @abstractmethod
    def update(self, image: np.ndarray) -> np.ndarray:
        pass

    @classmethod
    def get_parameters(self) -> list:
        return self.parameters

    @classmethod
    def set_parameters(self, change_dict):
        for this_key in change_dict.keys():
            self.parameters[this_key]["value"] = change_dict[this_key]
