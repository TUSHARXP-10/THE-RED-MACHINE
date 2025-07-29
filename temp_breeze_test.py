import os
from breeze_connector import refresh_session

refresh_session()

connector = BreezeConnector()

if connector.connect():
    # Example usage after successful connection
    # market_data = connector.get_market_data("NSE", "INFY")
    # print("Market Data:", market_data)

    # order_response = connector.place_order("NSE", "INFY", "BUY", 1, 1000)
    # print("Order Response:", order_response)
    pass