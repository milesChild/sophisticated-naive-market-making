import random
import numpy as np

class GaussianInformedTrader():

    def __init__(self, sigma_w):
        """
        :param sigma_w: standard deviation of noise process
        """
        self.sigma_w = sigma_w
        self.noisy_true_value = 0

    def update_true_value(self, true_value: int) -> None:
        noise = np.random.normal(0, self.sigma_w)
        new_true_value = true_value + noise
        if new_true_value < 0:
            self.noisy_true_value = 0
        elif new_true_value > 100:
            self.noisy_true_value = 100
        else:
            self.noisy_true_value = new_true_value
    
    def participating(self, best_bid: int, best_ask: int) -> bool:
        
        return (best_ask < self.noisy_true_value) or (best_bid >= self.noisy_true_value)
    
    def get_order(self, best_bid: int, best_ask: int) -> str:
        """
        Randomly generates a buy or sell order.
        """
        
        if best_ask < self.noisy_true_value:
            return "buy"
        elif best_bid >= self.noisy_true_value:
            return "sell"
        else:
            raise Exception("[ ERROR ] Informed trader should not be participating in the market.")