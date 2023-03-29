from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np
mid_stock1 = []
mid_stock2 = []
stock2_bal = []
class Trader:
    profit = 0
    limit = 0
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        stock1_position = state.position.get('STOCK1', 0)
        stock2_position = state.position.get('STOCK2', 0)
        for product in state.order_depths.keys():
            if product == 'STOCK1':
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []
                acceptable_price = 99 #Enter fair pricew
                while len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if (best_ask < acceptable_price or (stock1_position<0and best_ask == acceptable_price)) and abs(stock1_position -best_ask_volume) <= Trader.limit:
                        Trader.profit += best_ask_volume * best_ask
                        orders.append(Order(product, best_ask, -best_ask_volume))
                        stock1_position -= best_ask_volume
                        print("BUY", str(-best_ask_volume) + "x", best_ask, 'stock1_positions:',stock1_position, 'balance:',Trader.profit,'profit:',Trader.profit+stock1_position*10000+stock2_position*mid_stock2[-1])
                    del order_depth.sell_orders[best_ask]
                while len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if (best_bid > acceptable_price or (stock1_position>0and best_bid == acceptable_price)) and abs(stock1_position - best_bid_volume) <= Trader.limit:
                        Trader.profit += best_bid_volume * best_bid
                        orders.append(Order(product, best_bid, -best_bid_volume))
                        stock1_position -= best_bid_volume
                        print("SELL", str(best_bid_volume) + "x", best_bid, 'stock1_positions:',stock1_position,'balance:',Trader.profit, 'profit:',Trader.profit+stock1_position*10000+stock2_position*mid_stock2[-1])
                    del order_depth.buy_orders[best_bid]
                result[product] = orders

            if product == 'STOCK2':
                order_depth: OrderDepth = state.order_depths[product]
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    mid_stock2.append((max(order_depth.buy_orders.keys())+min(order_depth.sell_orders.keys()))/2)
                orders: list[Order] = []
                avg_window = 5
                acceptable_price = np.mean(mid_stock2[-avg_window:])
                position = state.position.get(product, 0)
                a50 = np.mean(mid_stock2[-50:])
                a200 = np.mean(mid_stock2[-50:])
                std = np.std(mid_stock2[-avg_window:])
                trend_index = a50 - a200
                factor = 0.9
                price = acceptable_price
                if stock2_position != 0:
                    price = Trader.stock2_bal/stock2_position
                for best_ask in sorted(order_depth.sell_orders):
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if (best_ask < acceptable_price or (stock2_position <-10 and best_ask < price-factor*trend_index)) and abs(best_ask_volume) <= Trader.limit:
                        if abs(stock2_position - best_ask_volume) >= Trader.limit:
                            best_ask_volume = -Trader.limit+abs(stock2_position - best_ask_volume)
                        else:
                            best_ask_volume
                        Trader.profit += best_ask_volume * best_ask
                        Trader.stock2_bal += best_ask_volume * best_ask
                        orders.append(Order(product, best_ask, -best_ask_volume))
                        stock2_position -= best_ask_volume
                        print("BUY", str(-best_ask_volume) + "x", best_ask,'current_market',mid_stock2[-1],'stock2_positions:',stock2_position,'balance:',Trader.profit, 'profit:',Trader.profit+stock1_position*10000+stock2_position*mid_stock2[-1],'std:',std)
                    else:
                        break
                    order_depth.sell_orders[best_ask]
                for best_bid in sorted(order_depth.buy_orders, reverse=True):
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if (best_bid > acceptable_price or (stock2_position>10 and best_bid > price+factor*trend_index)) and abs(best_bid_volume) <= Trader.limit:
                        if abs(stock2_position - best_bid_volume) >= Trader.limit:
                            best_bid_volume = Trader.limit-abs(stock2_position - best_bid_volume)
                        else:
                            best_bid_volume
                            Trader.profit += best_bid_volume * best_bid
                            Trader.stock2_bal += best_bid_volume * best_bid
                            stock2_position -= best_bid_volume
                            orders.append(Order(product, best_bid, -best_bid_volume))
                            print("SELL", str(best_bid_volume) + "x", best_bid,'current_market',mid_stock2[-1],'stock2_positions:',stock2_position,'balance:',Trader.profit, 'profit:',Trader.profit+stock1_position*10000+stock2_position*mid_stock2[-1],'std:',std)
                    else:
                        break
                    order_depth.buy_orders.pop(best_bid)

                result[product] = orders
            return result