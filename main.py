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
    Market-Aware Diversified Crop Farming Agent for Kaggriculture.
    - Market Price Monitoring:
        * Checks current market prices (Carrot vs Wheat).
        * Wheat ($10 seed) is our primary resilient staple crop (`log` market shape).
        * Carrot ($20 seed) is planted selectively when Carrot market price >= $30 and bank > $500.
    - Land Expansion: Unlocks NE quadrant ($1,000) when bankroll >= $2,000 before Day 20.
    - Workforce: Hires 2 low-cost farm hands daily ($1 + $1 = $2 cost), quadrupling daily work actions.
    - End-Game Saver: Cuts off seed/hire spending on Day 28+ to save final bankroll.
    """
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    money = me["money"]
    day = obs["day"]
    prices = obs["market"].get("prices", {})

    unlocked_tiles = get_unlocked_tiles(me)
    num_unlocked = len(unlocked_tiles)

    # ----------------------------------------------------
    # 1. MARKET ORDERS
    # ----------------------------------------------------
    market = []

    # Sell everything sitting in the shed every turn
    for item, qty in private["shed"].items():
        if qty > 0:
            market.append(["SELL", item, qty])

    # Land Expansion: Buy NE quadrant ($1,000) when money >= $2,000 before Day 20
    if num_unlocked == 25 and money >= 2000 and day <= 20:
        market.append(["BUY_LAND"])

    # Active farming phase (Day 0 to 27)
    if day <= 27:
        seeds = private["seeds"]
        wheat_seeds = seeds.get("WHEAT", 0)
        carrot_seeds = seeds.get("CARROT", 0)

        target_seeds = 15 if num_unlocked > 25 else 10
        carrot_price = prices.get("CARROT", 35)

        # Market-aware Carrot buying: Only buy Carrots if price is profitable (>= $30) and we have surplus cash (> $500)
        if carrot_price >= 30 and money >= 500 and carrot_seeds < 5:
            needed_c = 5 - carrot_seeds
            buy_c = min(needed_c, int(money // 20))
            if buy_c > 0:
                market.append(["BUY_SEED", "CARROT", buy_c])
                carrot_seeds += buy_c

        # Primary Wheat seed buffer
        if wheat_seeds < target_seeds and money >= 10:
            needed_w = target_seeds - wheat_seeds
            buy_w = min(needed_w, int(money // 10))
            if buy_w > 0:
                market.append(["BUY_SEED", "WHEAT", buy_w])
                wheat_seeds += buy_w

        # Hire 2 farm hands daily ($1 + $1 = $2 total daily cost)
        if me.get("hires_today", 0) < 2 and money >= 100:
            market.append(["HIRE"])

    # ----------------------------------------------------
    # 2. UNIT ASSIGNMENTS (Farmer + Hired Hands)
    # ----------------------------------------------------
    units = [me["farmer"]] + me.get("hands", [])

    seeds = private["seeds"]
    wheat_seeds = seeds.get("WHEAT", 0)
    carrot_seeds = seeds.get("CARROT", 0)

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
                # Wheat & Carrot first yield day is 2
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
        elif (ux, uy) in empty_tiles:
            if carrot_seeds > 0:
                action = ["PLANT", "CARROT"]
                empty_tiles.remove((ux, uy))
                carrot_seeds -= 1
            elif wheat_seeds > 0:
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
            if (wheat_seeds + carrot_seeds) > 0:
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
