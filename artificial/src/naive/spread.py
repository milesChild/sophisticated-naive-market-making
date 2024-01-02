# imports
import numpy as np

class NaiveSpreadModule:

    def __init__(self, config: dict):
        self.__spread_width = config["spread_width"]
        self.__i_max = config["i_max"]
        self.__i_a = config["i_a"]
    
    def get_spread(self, last_px: float, cur_inv: int) -> tuple:
        bid = np.floor(last_px - self.__spread_width / 2)
        ask = np.ceil(last_px + self.__spread_width / 2)
        adjustment = self.__calc_inventory_adjustment(cur_inv)
        bid = max(0, min(bid + adjustment, 100))
        ask = max(0, min(ask + adjustment, 100))
        return bid, ask
    
    def __calc_inventory_adjustment(self, cur_inv: int) -> int:
        return int(self.__i_max * (1 - np.exp(-self.__i_a * np.abs(cur_inv))) * -np.sign(cur_inv))