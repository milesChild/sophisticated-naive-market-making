def process_pnl(trades: list, true_values: list, auctions: int) -> tuple:

    if len(true_values) != auctions:
        raise Exception("Length of true values and auctions must be equal.")

    open_trades = []
    closed_trades = []
    realized_pnl = []
    unrealized_pnl = []

    for auction in range(auctions):
        
        auction_trades = [t for t in trades if t['auction'] == auction]

        for trade in auction_trades: 

            # if the trade is on the opposite side of the first trade in open trades, this is a closing trade
            if len(open_trades) > 0 and trade["side"] != open_trades[0]["side"]:
                open_trade = open_trades.pop(0)
                if trade['side'] == 'sell':
                    pnl = trade["price"] - open_trade['price']
                else:
                    pnl = open_trade['price'] - trade["price"]
                close = {
                    "duration": trade["auction"] - open_trade["auction"],
                    "pnl": pnl
                }
                closed_trades.append(close)
            else:
                open_trades.append(trade)

        # realized pnl
        realized_pnl.append(sum([close["pnl"] for close in closed_trades]))

        # unrealized pnl
        if len(open_trades) > 0:
            if open_trades[0]["side"] == "buy":
                pnl = true_values[auction] - open_trades[0]["price"]
            else:
                pnl = open_trades[0]["price"] - true_values[auction]
        else:
            pnl = 0
        unrealized_pnl.append(pnl)

    return realized_pnl, unrealized_pnl