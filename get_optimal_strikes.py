from high_oi_lot_manager import HighOILotManager

def get_optimal_strikes(current_price, expiry_date):
    """
    Wrapper function to get optimal strikes for 3000 capital
    """
    manager = HighOILotManager()
    return manager.get_optimal_strikes(current_price, expiry_date)

if __name__ == "__main__":
    # Test the function
    strikes = get_optimal_strikes(75000, "2024-12-19")
    print("Optimal strikes:", strikes)