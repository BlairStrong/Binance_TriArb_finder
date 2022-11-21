#Step 0 - identify the tradable pairs
import time
import requests
import json
import requests

"""https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md"""

#Extract list of coins and prices from the exchange:
baseurl = "https://api.binance.com"
kline_endpoint = "/api/v3/klines"
exchange_info  ="/api/v3/exchangeInfo"
depth = "/api/v3/depth"
bookTicker = "/api/v3/ticker/bookTicker"
add_symbol = "?symbol="

def test_func(coin_list_tradeable_joined):
    pass


def get_coin_data(url):
    r = requests.get(url)
    coin_json = json.loads(r.text)
    time.sleep(0.05)
    return coin_json


"""collect_tradables(coin_json) has exchange specific code"""
def collect_tradables(coin_json):
    #initialising Variables
    all_coin_list  = []
    all_coin_list_joined = []
    coin_list_tradeable = []
    coin_list_tradeable_joined = []
    untradeable_pairs_list = []
    count = 0
    for coin in coin_json["symbols"]:
        if coin_json["symbols"][count]["isSpotTradingAllowed"]:
            base = coin_json["symbols"][count]["baseAsset"]
            quote = coin_json["symbols"][count]["quoteAsset"]
            pair = base+"_"+quote
            all_coin_list.append(pair)
        else:
           untradeable_pairs_list.append(coin_json["symbols"][count]["symbol"])
        count += 1

    for item in all_coin_list:
        x = item.split("_")
        item_x = x[0]+x[1]
        all_coin_list_joined.append(item_x)

    #gathering order book data to eliminate coins with no bids/asks
    collection_count = 0
    bid_ask_data = []
    while collection_count < len(all_coin_list_joined):
        collection_request = 500
        request_list = all_coin_list_joined[collection_count:(collection_count+collection_request)]
        url = "https://api.binance.com/api/v3/ticker/bookTicker?symbols="+str(request_list)
        url = url.replace(" ", "")
        url = url.replace("'",'"')
        bid_ask_data_r = get_coin_data(url)
        bid_ask_data.append(bid_ask_data_r)
        collection_count += collection_request

    bid_ask_data_all = bid_ask_data[0] + bid_ask_data[1] + bid_ask_data[2] + bid_ask_data[3] + bid_ask_data[4]

    symbol_count = 0
    req_count = 0


    for coin in all_coin_list_joined:
        for item in bid_ask_data_all:
            if item["symbol"] == coin:
                if float(item["bidQty"]) == 0 or float(item["askQty"]) == 0 or float(item["bidPrice"]) == 0 or float(item["askPrice"]) == 0 or item["bidQty"] == [] or item["askQty"] == [] or item["bidPrice"] == [] or item["askPrice"] == []:
                    pass
                else:
                    coin_list_tradeable_joined.append(coin)

    #This Code is trying to put a list together with the split in it
    for item in all_coin_list:
        item_split_list = item.split("_")
        item_joined = item_split_list[0] + item_split_list[1]
        for coin in coin_list_tradeable_joined:
            if item_joined == coin:
                coin_list_tradeable.append(item)
    """List of tradables must be in the same configuration ie: BTCUSDT or BTC_USDT or BTC-USDT etc that excahnge API calls will recognise"""
    return coin_list_tradeable, coin_list_tradeable_joined


def structure_triangular_pairs(coin_list):
    #Declare Variables
    console_count = 0 # this counter is to show the user something is happening whilst program establishes the pairs
    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = coin_list[0:]
    pairs_count = 0
    bad_count = 0

    #Get pair A:
    for pair_a in pairs_list:
        pair_a_split = pair_a.split("_")
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]
        a_pair_box = [a_base, a_quote]
        coin_json = get_coin_data(baseurl + depth + add_symbol + a_base + a_quote)

        #Get Pair B;
        for pair_b in pairs_list:
            pair_b_split = pair_b.split("_")
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]
            b_pair_box = [b_base, b_quote]


            #check Pair b
            if pair_b != pair_a:
                if b_base in a_pair_box or b_quote in a_pair_box:

                    #Get Pair C
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split("_")
                        c_base = pair_c_split[0]
                        c_quote = pair_c_split[1]
                        c_pair_box = [c_base, c_quote]


                        #count the number of matching c items
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            c_base_counter = 0
                            for symbol in pair_box:
                                if symbol == c_base:
                                    c_base_counter += 1

                            c_quote_counter = 0
                            for symbol in pair_box:
                                if symbol == c_quote:
                                    c_quote_counter += 1

                            #Triangular Match reached
                            if c_base_counter == 2 and c_quote_counter == 2 and c_quote != c_base:
                                combined = pair_a+","+pair_b+","+pair_c
                                unique_item = "".join(sorted(combine_all))

                                if unique_item not in remove_duplicates_list:
                                    match_dict = {
                                        'a_base' : a_base,
                                        'a_quote' : a_quote,
                                        'b_base': b_base,
                                        'b_quote': b_quote,
                                        'c_base': c_base,
                                        'c_quote': c_quote,
                                        'pair_a': pair_a,
                                        'pair_b': pair_b,
                                        'pair_c': pair_c,
                                        'combined':combined
                                    }
                                    triangular_pairs_list.append(match_dict)
                                    remove_duplicates_list.append(unique_item)
                                    pairs_count += 1
                                    print(console_count)
                                    console_count += 1

    return triangular_pairs_list


"""get_tradeable_coins_prices(coin_list_tradeable_joined) has exchange specific code"""
def get_tradeable_coins_prices(coin_list_tradeable_joined):
    all_data = []
    try:
        API_list_1 = coin_list_tradeable_joined[:500]
        API_url_list = str(API_list_1).replace(" ", "")
        API_url_list = API_url_list.replace("'", '"')


        """URL - This link wil be bespoke to each Exchange"""
        url = baseurl + bookTicker + "?symbols=" + API_url_list


        if len(API_url_list) > 2:
            API_list_1_json = get_coin_data(url)
            all_data.append(API_list_1_json)
    except:
        pass
    try:
        API_list_2 = coin_list_tradeable_joined[500:1000]
        API_url_list = str(API_list_2).replace(" ", "")
        API_url_list = API_url_list.replace("'", '"')
        url = baseurl + bookTicker + "?symbols=" + API_url_list
        if len(API_url_list) > 2:
            API_list_2_json = get_coin_data(url)
            all_data.append(API_list_2_json)
    except:
        pass
    try:
        API_list_3 = coin_list_tradeable_joined[1000:1500]
        API_url_list = str(API_list_3).replace(" ", "")
        API_url_list = API_url_list.replace("'", '"')
        url = baseurl + bookTicker + "?symbols=" + API_url_list
        if len(API_url_list) > 2:
            API_list_3_json = get_coin_data(url)
            all_data.append(API_list_3_json)
    except:
        pass
    try:
        API_list_4 = coin_list_tradeable_joined[1500:2000]
        API_url_list = str(API_list_4).replace(" ", "")
        API_url_list = API_url_list.replace("'", '"')
        url = baseurl + bookTicker + "?symbols=" + API_url_list
        if len(API_url_list) > 2:
            API_list_4_json = get_coin_data(url)
            all_data.append(API_list_4_json)
    except:
        pass
    try:
        API_list_5 = coin_list_tradeable_joined[2000:2500]
        API_url_list = str(API_list_5).replace(" ", "")
        API_url_list = API_url_list.replace("'", '"')
        url = baseurl + bookTicker + "?symbols=" + API_url_list
        if len(API_url_list) > 2:
            print(url)
            API_list_5_json = get_coin_data(url)
            all_data.append(API_list_5_json)
    except:
        pass

    #Creating new dict with all price data in
    bookTicker_dict = {}
    list_count = 0
    item_count = 0
    while list_count < len(all_data) :
        item_count = 0
        while item_count < 500:
            try:
                bookTicker_dict[all_data[list_count][item_count]["symbol"]] = {
                    "bidPrice": all_data[list_count][item_count]["bidPrice"],
                    "askPrice": all_data[list_count][item_count]["askPrice"],
                    "bidQty": all_data[list_count][item_count]["bidQty"],
                    "askQty": all_data[list_count][item_count]["askQty"],
                }
                item_count += 1
            except:
                break
        list_count += 1

    return bookTicker_dict


def get_price_for_t_pair(t_pair, bookTicker_dict):

    #Extract the pair info
    pair_a = t_pair["a_base"]+t_pair["a_quote"]
    pair_b = t_pair["b_base"]+t_pair["b_quote"]
    pair_c = t_pair["c_base"]+t_pair["c_quote"]
    pairs_list = [pair_a, pair_b, pair_c]

    #Extract Price information
    pair_a_ask = float(bookTicker_dict[pair_a]["askPrice"])
    pair_a_bid = float(bookTicker_dict[pair_a]["bidPrice"])

    pair_b_ask = float(bookTicker_dict[pair_b]["askPrice"])
    pair_b_bid = float(bookTicker_dict[pair_b]["bidPrice"])

    pair_c_ask = float(bookTicker_dict[pair_c]["askPrice"])
    pair_c_bid = float(bookTicker_dict[pair_c]["bidPrice"])

    #output dict
    prices_dict = {
        "pair_a": pair_a,
        "pair_a_ask": pair_a_ask,
        "pair_a_bid": pair_a_bid,
        "pair_b": pair_b,
        "pair_b_ask": pair_b_ask,
        "pair_b_bid": pair_b_bid,
        "pair_c": pair_c,
        "pair_c_ask": pair_c_ask,
        "pair_c_bid": pair_c_bid,
    }
    return prices_dict


def calc_triangular_arb_surface_rate(t_pair, prices_dict):

    #set Variables:
    starting_amount = 1
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t1 = 0
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0

    #extract Pair variables
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["a_base"]+t_pair["a_quote"]
    pair_b = t_pair["b_base"]+t_pair["b_quote"]
    pair_c = t_pair["c_base"]+t_pair["c_quote"]

    #Extract_price_information
    a_ask = prices_dict["pair_a_ask"]
    a_bid = prices_dict["pair_a_bid"]
    b_ask = prices_dict["pair_b_ask"]
    b_bid = prices_dict["pair_b_bid"]
    c_ask = prices_dict["pair_c_ask"]
    c_bid = prices_dict["pair_c_bid"]

    #Set directions and loop
    direction_list = ['forward','reverse']
    for direction in direction_list:

        #set additional variables for swap information
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0

        """
        if we are swapping the coin on the left(BASE) to the right(quote) then * 1/ask
        if we are swapping the coin on the right(quote) to the left(BASE) then * bid
        """

        # assume starting with a_base and swapping for a_quote
        if direction == "forward":
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = 1 / a_ask
            direction_trade_1 = "base_to_quote"
        # assume starting with a_quote and swapping for a_bid
        elif direction == "reverse":
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_bid
            direction_trade_1 = "quote_to_base"


        #place first trade
        contract_1 = pair_a
        acquired_coin_t1 = starting_amount * swap_1_rate


        """
        FORWARD
        Calculate the order for which coins must be trades and in which direction
        Is A_quote == B_quote?"""

        if direction == "forward":
            # Scenario 1:
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b
                #if b_base matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1/c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c
                #if b_base matches c_quote
                elif b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            # Scenario 2:
            elif a_quote == b_base and calculated == 0:
                swap_2_rate = 1/b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b
                #if b_quote matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1/c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c
                #if b_quote matches c_quote
                elif b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

            #Scenario 3:
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c
                #if c_base matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1/b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b
                #if c_base matches b_quote
                elif c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            # Scenario 4:
            elif a_quote == c_base and calculated == 0:
                swap_2_rate = 1/c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c
                #if c_quote matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1/b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b
                #if c_quote matches b_quote
                elif c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        if direction == "reverse":
            # Scenario 5:
            if a_base == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b
                #if b_base matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1/c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c
                #if b_base matches c_quote
                elif b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            # Scenario 6:
            elif a_base == b_base and calculated == 0:
                swap_2_rate = 1/b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b
                #if b_quote matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1/c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c
                #if b_quote matches c_quote
                elif b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

            #Scenario 7:
            if a_base == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c
                #if c_base matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1/b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b
                #if c_base matches b_quote
                elif c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            # Scenario 8:
            elif a_base == c_base and calculated == 0:
                swap_2_rate = 1/c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c
                #if c_quote matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1/b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b
                #if c_quote matches b_quote
                elif c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        profit_loss = acquired_coin_t3 - starting_amount
        profit_percent = (acquired_coin_t3-starting_amount / starting_amount)*100

        #Trade descripotions:
        trade_description_1 = f"Start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}"
        trade_description_2 = f"Start with {swap_2} of {acquired_coin_t1}. Swap at {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}"
        trade_description_3 = f"Start with {swap_3} of {acquired_coin_t2}. Swap at {swap_3_rate} for {swap_1} acquiring {acquired_coin_t3}"

        #Output results
        if profit_percent > min_surface_rate:
            surface_dict = {
                'swap_1':swap_1,
                'swap_2':swap_2,
                'swap_3':swap_3,
                'contract_1':contract_1,
                'contract_2':contract_2,
                'contract_3':contract_3,
                'direction_trade_1':direction_trade_1,
                'direction_trade_2':direction_trade_2,
                'direction_trade_3':direction_trade_3,
                'starting_amount':starting_amount,
                'acquired_coin_t1':acquired_coin_t1,
                'acquired_coin_t2':acquired_coin_t2,
                'acquired_coin_t3':acquired_coin_t3,
                'swap_1_rate':swap_1_rate,
                'swap_2_rate':swap_2_rate,
                'swap_3_rate':swap_3_rate,
                'profit_loss':profit_loss,
                'profit_percent':profit_percent,
                'direction':direction,
                'trade_description_1':trade_description_1,
                'trade_description_2':trade_description_2,
                'trade_description_3':trade_description_3,
            }
            return surface_dict
    return surface_dict

def reformatted_orderbook(prices, contract_direction):
    price_list_main = []
    if contract_direction == "base_to_quote":
        for price in prices["asks"]:
            ask_price = float(price[0])
            adj_price = 1/ask_price if ask_price != 0 else 0
            adj_quantity = float(price[1]) * ask_price
            price_list_main.append([adj_price, adj_quantity])
    elif contract_direction == "quote_to_base":
        for price in prices["bids"]:
            bid_price = float(price[0])
            adj_price = bid_price
            adj_quantity = float(price[1])
            price_list_main.append([adj_price, adj_quantity])
    return price_list_main

def calculate_acquired_coin(amount_in, orderbook):

    #initialise Variables
    trading_balance = amount_in
    amount_bought = 0
    quantity_bought = 0
    acquired_coin = 0
    counts = 0

    for level in orderbook:
        level_price = level[0]
        level_available_quantity = level[1]
        if trading_balance != None:
            if trading_balance <= level_available_quantity:
                quantity_bought = trading_balance
                trading_balance = 0
                amount_bought = quantity_bought*level_price

            elif trading_balance > level_available_quantity:
                quantity_bought = level_available_quantity
                trading_balance -= quantity_bought
                amount_bought = quantity_bought * level_price

            #Accumulate acquired coin
            acquired_coin = acquired_coin + amount_bought

            #Exit conditions
            if trading_balance == 0:
                return acquired_coin

            #exit if to may orderbook levels (10)
            counts += 1
            if counts == 200:
                return 0
        else:
            return 0


"""get_depth_from_orderbook() has exchange specific code"""
def get_depth_from_orderbook(surface_arb):
    swap_1 = surface_arb["swap_1"]
    starting_amount = 1000
    starting_amount_dict = {
        "BUSD":1000,
    }
    if swap_1 in starting_amount_dict:
        starting_amount = starting_amount_dict[swap_1]

    #Defined Pairs
    contract_1 = surface_arb["contract_1"]
    contract_2 = surface_arb["contract_2"]
    contract_3 = surface_arb["contract_3"]

    contract_1_direction = surface_arb["direction_trade_1"]
    contract_2_direction = surface_arb["direction_trade_2"]
    contract_3_direction = surface_arb["direction_trade_3"]

    #get orderbook depth
    """URL has exchange specific code"""
    url1 = baseurl + depth + "?symbol=" + f"{contract_1}"
    depth_1_prices = get_coin_data(url1)
    depth_1_reformatted_prices = reformatted_orderbook(depth_1_prices, contract_1_direction)
    time.sleep(0.3)

    """URL has exchange specific code"""
    url2 = baseurl + depth + "?symbol=" + f"{contract_2}"
    depth_2_prices = get_coin_data(url2)
    depth_2_reformatted_prices = reformatted_orderbook(depth_2_prices, contract_2_direction)
    time.sleep(0.3)

    """URL has exchange specific code"""
    url3 = baseurl + depth + "?symbol=" + f"{contract_3}"
    depth_3_prices = get_coin_data(url3)
    depth_3_reformatted_prices = reformatted_orderbook(depth_3_prices, contract_3_direction)
    time.sleep(0.3)

    #get acquired coins
    acquired_coin_t1 = calculate_acquired_coin(starting_amount, depth_1_reformatted_prices)
    acquired_coin_t2 = calculate_acquired_coin(acquired_coin_t1, depth_2_reformatted_prices)
    acquired_coin_t3 = calculate_acquired_coin(acquired_coin_t2, depth_3_reformatted_prices)

    #Calculate real rate
    if acquired_coin_t3 != None and starting_amount != None:
        profit_loss = acquired_coin_t3 - starting_amount
        real_rate_percent = (profit_loss/starting_amount) * 100 if profit_loss != 0 else 0

        if real_rate_percent > 0.25:
            return_dict = {
                'profit_loss': profit_loss,
                'real_rate_percent': real_rate_percent,
                'contract_1':contract_1,
                'contract_2':contract_2,
                'contract_3':contract_3,
                'contract_1_direction':contract_1_direction,
                'contract_2_direction':contract_2_direction,
                'contract_3_direction':contract_3_direction,
            }
        else:
            return_dict = {}
    else:
        print("Error")
        print(acquired_coin_t3, starting_amount, surface_arb)
        return_dict = {}

    return return_dict





        
    
















