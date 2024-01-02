# Manually running the auction with the jump detector equipped:

# imports
import random
from sophisticated.util import calculate_expected_value
import numpy as np

class CompetitiveAuction():

    def __init__(self, traders, true_value_series, market_makers, N, V_T0, jump_detector=None):
        self.traders = traders
        self.true_value_series = true_value_series
        self.market_makers = market_makers
        self.N = N
        self.V_T0 = V_T0
        if jump_detector:
            self.jump_detector = jump_detector

    def run(self) -> dict:

        inventory_values = {mm.name: [] for mm in self.market_makers}
        bid_values = {mm.name: [] for mm in self.market_makers}
        ask_values = {mm.name: [] for mm in self.market_makers}
        best_bids = []
        best_asks = []
        true_values = []
        expected_values = {mm.name: [] for mm in self.market_makers}

        mm_trades = {mm.name: [] for mm in self.market_makers}

        inventory = {mm.name: 0 for mm in self.market_makers}
        last_px = self.V_T0

        for a in range(self.N):

            true_value = self.true_value_series[a]

            # update the traders of the new true value
            for trader in self.traders:
                trader.update_true_value(true_value)
            
            # randomize trading order
            random.shuffle(self.traders)

            auction_buys = 0
            auction_sells = 0
            
            for trader in self.traders:

                # first, get the bids and asks from each market maker to get BBO
                best_bid = {'price': 0, 'mm': None}
                best_ask = {'price': 100, 'mm': None}

                random.shuffle(self.market_makers)  # price time prio

                for mm in self.market_makers:

                    # If the market maker's class name is NaiveSpreadModule,
                    if mm.__class__.__name__ == "NaiveSpreadModule":
                        bid, ask = mm.get_spread(last_px=last_px, cur_inv=inventory[mm.name])
                        if bid > best_bid['price'] or best_bid['price'] == 0:
                            best_bid['price'] = bid
                            best_bid['mm'] = mm
                        if ask < best_ask['price'] or best_ask['price'] == 100:
                            best_ask['price'] = ask
                            best_ask['mm'] = mm
                        bid_values[mm.name].append(bid)
                        ask_values[mm.name].append(ask)
                    else:
                        bid, ask = mm.get_spread(cur_inv=inventory[mm.name])
                        if bid > best_bid['price'] or best_bid['price'] == 0:
                            best_bid['price'] = bid
                            best_bid['mm'] = mm
                        if ask < best_ask['price'] or best_ask['price'] == 100:
                            best_ask['price'] = ask
                            best_ask['mm'] = mm
                
                best_bids.append(best_bid['price'])
                best_asks.append(best_ask['price'])
                true_values.append(true_value)
                
                if trader.participating(best_bid['price'], best_ask['price']):

                    order = trader.get_order(best_bid['price'], best_ask['price'])
                    if order == "buy":
                        mm = best_ask['mm']
                        inventory[mm.name] -= 1
                        mm_trades[mm.name].append({"side": "sell", "price": best_ask['price'], "auction": a})
                        last_px = best_ask['price']
                        auction_buys += 1
                        for mm in self.market_makers:
                            if mm.__class__.__name__ != "NaiveSpreadModule":
                                mm.update_pdf(buy_order=True, Pa=best_ask['price'])
                        
                    elif order == "sell":
                        mm = best_bid['mm']
                        inventory[mm.name] += 1
                        mm_trades[mm.name].append({"side": "buy", "price": best_bid['price'], "auction": a})
                        last_px = best_bid['price']
                        auction_sells += 1
                        for mm in self.market_makers:
                            if mm.__class__.__name__ != "NaiveSpreadModule":
                                mm.update_pdf(buy_order=False, Pb=best_bid['price'])

                for mm in self.market_makers:
                    inventory_values[mm.name].append(inventory[mm.name])
                    if mm.__class__.__name__ != "NaiveSpreadModule":
                        expected_values[mm.name].append(calculate_expected_value(mm.pdf, mm.prices))
                    else:
                        expected_values[mm.name].append(bid + ask / 2)
                
            if true_value != self.true_value_series[a-1] and a > 0:
                for mm in self.market_makers:
                    if mm.__class__.__name__ != "NaiveSpreadModule":
                        last_ev = expected_values[mm.name][-1]
                        std_dev = 10
                        mm.reset_pdf(initial_true_value=last_ev, std_dev=std_dev)
            # if self.jump_detector:
            #     if auction_buys + auction_sells > 0:
            #         buy_ratio = auction_buys / (auction_buys + auction_sells)
            #     else:
            #         buy_ratio = 0
            #     jump = self.jump_detector.update(buy_ratio)
            #     if jump:
            #         print(f"Jump detected at auction {a}")
            #         for mm in self.market_makers:
            #             if mm.__class__.__name__ != "NaiveSpreadModule":
            #                 last_ev = expected_values[mm.name][-1]
            #                 std_dev = 25
            #                 mm.reset_pdf(initial_true_value=last_ev, std_dev=std_dev)

        return {
            "inventory_values": inventory_values,
            "bid_values": bid_values,
            "ask_values": ask_values,
            "best_bids": best_bids,
            "best_asks": best_asks,
            "true_values": true_values,
            "expected_values": expected_values,
            "mm_trades": mm_trades
        }