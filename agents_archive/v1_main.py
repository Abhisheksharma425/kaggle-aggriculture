def manhattan_step(curr, target):
    """Returns movement action ('NORTH', 'SOUTH', 'EAST', 'WEST') to step closer to target."""
    cx, cy = curr
    tx, ty = target
    if cx < tx:
        return "EAST"
    if cx > tx:
        return "WEST"
    if cy < ty:
        return "SOUTH"
    if cy > ty:
        return "NORTH"
    return "PASS"


def get_unlocked_tiles(farm):
    """Returns list of (x, y) coordinates for all unlocked tiles."""
    unlocked = []
    tiles = farm["tiles"]
    for y in range(len(tiles)):
        for x in range(len(tiles[y])):
            if tiles[y][x] != "LOCKED":
                unlocked.append((x, y))
    return unlocked


def agent(obs):
    """
    Enhanced Baseline Rule-Based Farming Agent for Kaggriculture.
    - Manages Wheat & Carrot loops across unlocked tiles.
    - Land Expansion: Buys NE quadrant when money >= 2000.
    - End-game strategy: Stops seed/hire spending after Day 27 to preserve profit.
    - Task Priorities: HARVEST > WATER > DIG WEED > PLANT.
    """
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    money = me["money"]
    day = obs["day"]

    unlocked_tiles = get_unlocked_tiles(me)
    num_unlocked = len(unlocked_tiles)

    # ----------------------------------------------------
    # 1. MARKET ORDERS
    # ----------------------------------------------------
    market = []

    # Sell everything sitting in the shed
    for item, qty in private["shed"].items():
        if qty > 0:
            market.append(["SELL", item, qty])

    # Buy land expansion (NE quadrant = $1,000) if we have solid cash reserves (> $2,000)
    if num_unlocked == 25 and money >= 2000:
        market.append(["BUY_LAND"])

    # End-game cutoff: Stop buying seeds/hiring on Day 28+ (since season ends on Day 30)
    if day <= 27:
        # Buy Wheat seeds to maintain a seed buffer (up to 15 seeds for expanded land)
        wheat_seeds = private["seeds"].get("WHEAT", 0)
        target_seeds = 15 if num_unlocked > 25 else 10
        if wheat_seeds < target_seeds and money >= 10:
            needed = target_seeds - wheat_seeds
            affordable = int(money // 10)
            buy_qty = min(needed, affordable)
            if buy_qty > 0:
                market.append(["BUY_SEED", "WHEAT", buy_qty])
                wheat_seeds += buy_qty

        # Hire farm hands (up to 2-3 daily) when cash flow is strong
        max_hires = 3 if num_unlocked > 25 else 2
        if me.get("hires_today", 0) < max_hires and money >= 100:
            market.append(["HIRE"])

    # ----------------------------------------------------
    # 2. UNIT ASSIGNMENTS (Farmer + Hired Hands)
    # ----------------------------------------------------
    units = [me["farmer"]] + me.get("hands", [])
    wheat_seeds = private["seeds"].get("WHEAT", 0)

    harvest_tasks = []
    water_tasks = []
    weed_tasks = []
    empty_tiles = []

    tiles = me["tiles"]
    for x, y in unlocked_tiles:
        tile = tiles[y][x]
        if tile is None:
            empty_tiles.append((x, y))
        elif isinstance(tile, dict):
            kind = tile.get("kind")
            if kind == "WEED":
                weed_tasks.append((x, y))
            elif kind == "PLANT":
                crop_age = day - tile["planted_day"]
                # Wheat & Carrot: harvest available at age >= 2
                if crop_age >= 2:
                    harvest_tasks.append((x, y))
                elif not tile.get("watered_today", False):
                    water_tasks.append((x, y))

    assigned_targets = set()
    farmer_action = ["PASS"]
    hands_actions = []

    for u_idx, u_pos in enumerate(units):
        ux, uy = u_pos
        action = None

        # Priority 1: Standing directly on a task tile? Act immediately!
        if (ux, uy) in harvest_tasks:
            action = ["HARVEST"]
            harvest_tasks.remove((ux, uy))
        elif (ux, uy) in water_tasks:
            action = ["WATER"]
            water_tasks.remove((ux, uy))
        elif (ux, uy) in weed_tasks:
            action = ["DIG"]
            weed_tasks.remove((ux, uy))
        elif (ux, uy) in empty_tiles and wheat_seeds > 0:
            action = ["PLANT", "WHEAT"]
            empty_tiles.remove((ux, uy))
            wheat_seeds -= 1

        # Priority 2: Not on task tile -> Move toward closest unassigned target
        if action is None:
            candidate_targets = []
            for t in harvest_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((0, t))
            for t in water_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((1, t))
            for t in weed_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((2, t))
            if wheat_seeds > 0:
                for t in empty_tiles:
                    if t not in assigned_targets:
                        candidate_targets.append((3, t))

            if candidate_targets:
                candidate_targets.sort(
                    key=lambda item: (
                        item[0],
                        abs(ux - item[1][0]) + abs(uy - item[1][1]),
                    )
                )
                best_target = candidate_targets[0][1]
                assigned_targets.add(best_target)
                move_dir = manhattan_step(u_pos, best_target)
                action = [move_dir]
            else:
                action = ["PASS"]

        if u_idx == 0:
            farmer_action = action
        else:
            hands_actions.append(action)

    return {
        "farmer": farmer_action,
        "hands": hands_actions,
        "market": market,
    }
