import matplotlib.pyplot as plt
from typing import Optional
import json

class Orderbook():

    def __init__(self, seed: Optional[dict] = None) -> None:
        self.ts = None
        self.ticker = None
        self.bids = dict()
        self.asks = dict()

        if seed:
            self.update(seed)

    def update(self, seed: dict) -> None:
        for key, value in seed.items():
            try:
                if key == 'ts':
                    self.ts = int(value)
                elif key.startswith('yes.'):
                    value = int(value)
                    if value != 0:
                        self.bids[int(key[4:])] = value
                elif key.startswith('no.'):
                    value = int(value)
                    if value != 0:
                        self.asks[100 - int(key[3:])] = value
                elif key == "market_ticker":
                    self.ticker = value
            except Exception as e:
                print(e)
    
    def best_bid(self) -> Optional[int]:
        if self.bids:
            return max(self.bids.keys())
        else:
            return 0
        
    def best_offer(self) -> Optional[int]:
        if self.asks:
            return min(self.asks.keys())
        else:
            return 100
    
    def plot_depth_chart(self):
        # Process 'yes' bids (buy orders)
        yes_prices_sorted = sorted(self.bids.keys(), reverse=True)
        yes_volumes = [self.bids[price] for price in yes_prices_sorted]
        yes_cum_volumes = [sum(yes_volumes[:i+1]) for i in range(len(yes_volumes))]

        # Process 'no' bids as 'yes' asks (sell orders)
        no_prices_sorted = sorted(self.asks.keys(), reverse=True)
        no_volumes = [self.asks[price] for price in no_prices_sorted]
        no_cum_volumes = [sum(no_volumes[i:]) for i in range(len(no_volumes))]  # accumulate negatively

        # Plotting as step charts
        plt.figure(figsize=(10, 6))
        plt.step(yes_prices_sorted, yes_cum_volumes, label='Bids (Yes)', color='green', where='post')
        plt.step(no_prices_sorted, no_cum_volumes, label='Offers (No)', color='red', where='pre')  # use 'pre' for alignment

        # Fill under the curves
        plt.fill_between(yes_prices_sorted, yes_cum_volumes, step='post', alpha=0.2, color='green')
        plt.fill_between(no_prices_sorted, no_cum_volumes, step='pre', alpha=0.2, color='red')

        # Adding limits to x-axis if necessary, to show the spread
        if yes_prices_sorted and no_prices_sorted:
            plt.xlim([min(yes_prices_sorted + no_prices_sorted), max(yes_prices_sorted + no_prices_sorted)])

        plt.title('Orderbook Depth (Yes)')
        plt.xlabel('Price')
        plt.ylabel('Cumulative Quantity')
        plt.legend()
        plt.grid(True)
        plt.show()

    def to_json(self) -> str:
        json_dict = dict()
        if self.ts:
            json_dict['ts'] = self.ts
        if self.ticker:
            json_dict['market_ticker'] = self.ticker
        for price, volume in self.bids.items():
            json_dict[f'yes.{price}'] = volume
        for price, volume in self.asks.items():
            json_dict[f'no.{100 - price}'] = volume

        return json.dumps(json_dict)

    @classmethod
    def from_json(cls, json_str: str):
        json_dict = json.loads(json_str)
        return cls(json_dict)