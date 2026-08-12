def agent(obs):
    """
    A simple baseline agent that runs a Wheat loop on the starting tile.
    - Buys Wheat seeds if none are in inventory and money permits.
    - Plants Wheat on the current tile if empty.
    - Waters the Wheat crop daily.
    - Harvests the Wheat crop when ready (at day 2 or later).
    - Sells harvested Wheat back to the market.
    """
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]

    market = []
    
    # 1. Buy seed if we don't have any and we have enough money (Wheat cost = 10)
    if private["seeds"].get("WHEAT", 0) == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])
        
    # 2. Sell any wheat sitting in the shed to make money
    wheat_in_shed = private["shed"].get("WHEAT", 0)
    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])

    # 3. Action selection for the farmer
    # If the current tile is empty and we have a seed, plant it
    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": market}
        
    # If the tile has a plant, manage it
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        crop_age = obs["day"] - tile["planted_day"]
        
        # Harvest Wheat once it has grown (first yield day is 2)
        if crop_age >= 2:
            return {"farmer": ["HARVEST"], "hands": [], "market": market}
            
        # Water it if not watered today
        if not tile["watered_today"]:
            return {"farmer": ["WATER"], "hands": [], "market": market}

    # Pass if there's nothing to do
    return {"farmer": ["PASS"], "hands": [], "market": market}
