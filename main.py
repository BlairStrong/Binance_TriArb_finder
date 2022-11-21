
import requests
import json
from datetime import datetime
import time
import func_arbitrage
from func_arbitrage import get_coin_data, collect_tradables

"""URL Data"""
base = "https://api.binance.com"
kline_endpoint = "/api/v3/klines"
exchange_info  ="/api/v3/exchangeInfo"
depth = "/api/v3/depth"
add_symbol = "?symbol="

"""Step 0 - Collecting coin list"""
def step_0():
    """This step is Exchange specific"""

    #Extract list of coins and prices from the exchange:
    url = base+exchange_info
    coin_json = func_arbitrage.get_coin_data(url)
    coin_list_tradeable, coin_list_tradeable_joined = func_arbitrage.collect_tradables(coin_json)
    time.sleep(0.2)

    return coin_list_tradeable, coin_list_tradeable_joined

"""Step 1: Structuring Triangular Pairs Calculation only"""
def step_1(coin_list_tradeable):
    structured_list = func_arbitrage.structure_triangular_pairs(coin_list_tradeable)
    #Save Json with structured list
    with open("structured_triangular_pairs.json", "w") as json_file:
        json.dump(structured_list, json_file)

"""Step 2: Calculate Surface Rate Arb opportunities"""
def step_2():
    while True:
        time.sleep(2)
        bookTicker_dict = func_arbitrage.get_tradeable_coins_prices(coin_list_tradeable_joined)
        # get structured pairs
        with open("structured_triangular_pairs.json", "r") as fp:
            structured_pairs = json.load(fp)
            #Loop through and structure price information
            for t_pair in structured_pairs:
                prices_dict = func_arbitrage.get_price_for_t_pair(t_pair, bookTicker_dict)
                surface_arb = func_arbitrage.calc_triangular_arb_surface_rate(t_pair, prices_dict)
                if len(surface_arb) > 0:
                    real_rate_arb = func_arbitrage.get_depth_from_orderbook(surface_arb)
                    print(datetime.now(), real_rate_arb)
                    time.sleep(1)



"""MAIN"""
if __name__ == "__main__":


    print("Step 0 - Collecting coin list")
    coin_list_tradeable, coin_list_tradeable_joined = step_0()

    """Ensure the list of coins in line 94 of func arb is showing the full list of coins and hasnt been shortened.  """
    print("Step 1: Structuring Triangular Pairs Calculation only")
    structured_pairs = step_1(coin_list_tradeable)

    print("Step 2: Calculate Surface Rate Arb opportunities")
    step_2()











