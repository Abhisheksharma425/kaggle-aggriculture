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
    Advanced Diversified Agent for Kaggriculture.
    - Crop Mix: Wheat ($10) + Carrot ($20) for fast daily cash flow.
    - Livestock Loop: Goose/Egg farming (Coop + Goose) for passive $50 daily egg income + fertilizer.
    - Smart Land Expansion: Only buys new land when current quadrant is >= 80% filled and bank >= $2,000.
    - Workforce: Hires 2 low-cost farm hands daily ($1 + $1 = $2 cost).
    - End-Game Saver: Stops purchases on Day 28+ to maximize final coin score.
    """
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    money = me["money"]
    day = obs["day"]

    unlocked_tiles = get_unlocked_tiles(me)
    num_unlocked = len(unlocked_tiles)

    tiles = me["tiles"]
    filled_tiles = [(x, y) for (x, y) in unlocked_tiles if tiles[y][x] is not None]
    utilization = len(filled_tiles) / max(1, num_unlocked)

    # ----------------------------------------------------
    # 1. MARKET ORDERS
    # ----------------------------------------------------
    market = []

    # Sell all produce in shed immediately every turn
    for item, qty in private["shed"].items():
        if qty > 0:
            market.append(["SELL", item, qty])

    # 80% Utilization Land Expansion Threshold:
    # Only buy NE land quadrant ($1,000) when >= 80% of current tiles are filled AND bank >= $2,000
    if num_unlocked == 25 and utilization >= 0.80 and money >= 2000 and day <= 20:
        market.append(["BUY_LAND"])

    # Active farming & animal phase (Day 0 to 27)
    if day <= 27:
        seeds = private["seeds"]
        wheat_seeds = seeds.get("WHEAT", 0)
        carrot_seeds = seeds.get("CARROT", 0)
        shed = private.get("shed", {})
        geese_in_shed = shed.get("GOOSE", 0)

        # Count total active coops/geese on board
        active_geese = 0
        coops_count = 0
        for x, y in unlocked_tiles:
            t = tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "COOP":
                coops_count += 1
                if t.get("animal") == "GOOSE":
                    active_geese += 1

        # Buy Goose ($300) if we have a Coop or enough money for investment (>= $800)
        if active_geese + geese_in_shed < 2 and money >= 800 and day <= 18:
            if active_geese + geese_in_shed == 0 or money >= 1200:
                market.append(["BUY_ANIMAL", "GOOSE", 1])

        target_seeds = 15 if num_unlocked > 25 else 10

        # Buy Carrot seeds (higher profit $35 vs $25) when cash > $300
        if money >= 300 and carrot_seeds < (target_seeds // 2):
            needed_c = (target_seeds // 2) - carrot_seeds
            buy_c = min(needed_c, int(money // 20))
            if buy_c > 0:
                market.append(["BUY_SEED", "CARROT", buy_c])
                carrot_seeds += buy_c

        # Primary Wheat seed buffer (also needed for animal feed)
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
    feed_tasks = []
    collect_tasks = []
    weed_tasks = []
    empty_tiles = []
    empty_coops = []

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
                if crop_age >= 2:
                    harvest_tasks.append((x, y))
                elif not tile.get("watered_today", False):
                    water_tasks.append((x, y))
            elif kind == "COOP":
                animal = tile.get("animal")
                if animal == "GOOSE":
                    if tile.get("yield_units", 0) > 0:
                        harvest_tasks.append((x, y))
                    if not tile.get("fed_today", False):
                        feed_tasks.append((x, y))
                    if tile.get("fertilizer_available", False):
                        collect_tasks.append((x, y))
                elif animal is None:
                    empty_coops.append((x, y))

    assigned_targets = set()
    farmer_action = ["PASS"]
    hands_actions = []

    for u_idx, u_pos in enumerate(units):
        ux, uy = u_pos
        action = None

        # Priority 1: Standing directly on a task tile? Act immediately!
        if (ux, uy) in feed_tasks:
            action = ["FEED"]
            feed_tasks.remove((ux, uy))
        elif (ux, uy) in harvest_tasks:
            action = ["HARVEST"]
            harvest_tasks.remove((ux, uy))
        elif (ux, uy) in water_tasks:
            action = ["WATER"]
            water_tasks.remove((ux, uy))
        elif (ux, uy) in collect_tasks:
            action = ["COLLECT_FERTILIZER"]
            collect_tasks.remove((ux, uy))
        elif (ux, uy) in weed_tasks:
            action = ["DIG"]
            weed_tasks.remove((ux, uy))
        elif (ux, uy) in empty_coops and private.get("shed", {}).get("GOOSE", 0) > 0:
            action = ["PLACE", "GOOSE"]
            empty_coops.remove((ux, uy))
        elif (ux, uy) in empty_tiles:
            # Build Coop if we have money >= $800 and no coop built yet
            if len(empty_coops) == 0 and money >= 800 and day <= 15:
                action = ["BUILD_COOP"]
                empty_tiles.remove((ux, uy))
            elif carrot_seeds > 0:
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
            for t in feed_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((0, t))
            for t in harvest_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((1, t))
            for t in water_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((2, t))
            for t in collect_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((3, t))
            for t in weed_tasks:
                if t not in assigned_targets:
                    candidate_targets.append((4, t))
            if (wheat_seeds + carrot_seeds) > 0:
                for t in empty_tiles:
                    if t not in assigned_targets:
                        candidate_targets.append((5, t))

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
