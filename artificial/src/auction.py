# imports
import random
from sophisticated.util import calculate_expected_value
import numpy as np

class Auction():

    def __init__(self, traders, true_value_series, market_maker, N, V_T0):
        self.traders = traders
        self.true_value_series = true_value_series
        self.market_maker = market_maker
        self.N = N
        self.V_T0 = V_T0

    def run(self, omniscient: bool=False) -> dict:

        inventory_values = []
        bid_values = []
        ask_values = []
        true_values = []
        expected_values = [self.V_T0]

        mm_trades = []

        inventory = 0
        last_px = self.V_T0

        for a in range(self.N):

            true_value = self.true_value_series[a]

            # update the traders of the new true value
            for trader in self.traders:
                trader.update_true_value(true_value)
            
            # check if the true value has changed
            if omniscient:
                if true_value != self.true_value_series[a-1] and a > 0:
                    if self.market_maker.__class__.__name__ != "NaiveSpreadModule":
                        last_ev = expected_values[-1]
                        std_dev = np.std(expected_values)
                        self.market_maker.reset_pdf(initial_true_value=last_ev, std_dev=std_dev)
            
            # randomize trading order
            random.shuffle(self.traders)
            
            for trader in self.traders:
                
                # If the market maker's class name is NaiveSpreadModule,
                if self.market_maker.__class__.__name__ == "NaiveSpreadModule":
                    # then the market maker's get_spread method requires the last price and current inventory.
                    bid, ask = self.market_maker.get_spread(last_px=last_px, cur_inv=inventory)
                else:
                    bid, ask = self.market_maker.get_spread(cur_inv=inventory)
                
                bid_values.append(bid)
                ask_values.append(ask)
                true_values.append(true_value)
                
                if trader.participating(bid, ask):

                    order = trader.get_order(bid, ask)
                    if order == "buy":
                        inventory -= 1
                        mm_trades.append({"side": "sell", "price": ask, "auction": a})
                        last_px = ask
                        if self.market_maker.__class__.__name__ != "NaiveSpreadModule":
                            self.market_maker.update_pdf(buy_order=True, Pa=ask)
                        
                    elif order == "sell":
                        inventory += 1
                        mm_trades.append({"side": "buy", "price": bid, "auction": a})
                        last_px = bid
                        if self.market_maker.__class__.__name__ != "NaiveSpreadModule":
                            self.market_maker.update_pdf(buy_order=False, Pb=bid)

                inventory_values.append(inventory)
                if self.market_maker.__class__.__name__ != "NaiveSpreadModule":
                    expected_values.append(calculate_expected_value(self.market_maker.pdf, self.market_maker.prices))
                else:
                    expected_values.append(bid + ask / 2)

        return {
            "inventory": inventory_values,
            "bids": bid_values,
            "asks": ask_values,
            "true_values": true_values,
            "expected_values": expected_values,
            "mm_trades": mm_trades
        }