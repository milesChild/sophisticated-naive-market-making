import random

class GaussianTrader():

    def __init__(self, eta):
        """
        :param eta: probability of making a trade, 0 < eta < 1, 0.1 represents 10% chance of making a trade
        """
        self.eta = eta
        self.group = "Gaussian Trader"
    
    def participating(self, best_bid: int, best_ask: int) -> bool:
        
        return random.random() < self.eta
    
    def get_order(self, best_bid: int, best_ask: int) -> str:
        """
        Randomly generates a buy or sell order.
        """
        rand = random.randint(0, 1)
        if rand == 0:
            return "buy"
        else:
            return "sell"
        
    def update_true_value(self, true_value: int) -> None:
        pass