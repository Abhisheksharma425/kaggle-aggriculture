def manhattan_step(curr, target):
    cx, cy = curr
    tx, ty = target
    if cx < tx: return "EAST"
    if cx > tx: return "WEST"
    if cy < ty: return "SOUTH"
    if cy > ty: return "NORTH"
    return "PASS"


def manhattan_dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

# Crop data for harvest timing
CROP_FIRST_YIELD = {
    "WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10
}


def agent(obs):
    """
    Wheat-primary farming + gradual livestock.
    Phase 1 (Day 0-5): Plant wheat everywhere, harvest cycle every 2 days.
    Phase 2 (Day 4+): Build pastures, buy animals one at a time.
    Phase 3 (Day 8+): Expand land, add more animals.
    FEED requires WHEAT in unit inventory: PICKUP WHEAT → walk to animal → FEED.
    """
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    money = me["money"]
    day = obs["day"]
    hour = obs["hour"]

    tiles = me["tiles"]
    board_size = len(tiles)
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    inventories = private.get("inventories", [{}])

    # Build unlocked tile list
    unlocked = []
    for y in range(board_size):
        for x in range(len(tiles[y])):
            if tiles[y][x] != "LOCKED":
                unlocked.append((x, y))
    num_unlocked = len(unlocked)

    # Scan board state
    active_cows = 0
    active_sheep = 0
    empty_pastures = []
    unfed_animals = []
    harvestable = []
    unwatered = []
    fertilizer_tiles = []
    care_tiles = []
    weeds = []
    empty_tiles = []
    
    wheat_plants = 0
    straw_plants = 0
    melon_plants = 0

    for x, y in unlocked:
        t = tiles[y][x]
        if t is None:
            empty_tiles.append((x, y))
        elif isinstance(t, dict):
            kind = t.get("kind")
            if kind == "WEED":
                weeds.append((x, y))
            elif kind == "PLANT":
                crop = t.get("crop", "WHEAT")
                if crop == "WHEAT": wheat_plants += 1
                elif crop == "STRAWBERRY": straw_plants += 1
                elif crop == "MELON": melon_plants += 1
                first_yield = CROP_FIRST_YIELD.get(crop, 2)
                age = day - t["planted_day"]
                yu = t.get("yield_units", 0)
                if yu > 0 and age >= first_yield:
                    harvestable.append((x, y))
                elif not t.get("watered_today", False):
                    unwatered.append((x, y))
            elif kind in ("PASTURE", "COOP"):
                animal = t.get("animal")
                if animal:
                    if animal == "COW": active_cows += 1
                    elif animal == "SHEEP": active_sheep += 1
                    if not t.get("fed_today", False):
                        unfed_animals.append((x, y))
                    if t.get("yield_units", 0) > 0:
                        harvestable.append((x, y))
                    if t.get("fertilizer_available", False):
                        fertilizer_tiles.append((x, y))
                    if not t.get("cared_today", False) and t.get("fed_today", False):
                        care_tiles.append((x, y))
                else:
                    empty_pastures.append((x, y))

    cows_in_shed = shed.get("COW", 0)
    sheep_in_shed = shed.get("SHEEP", 0)
    total_cows = active_cows + cows_in_shed
    total_sheep = active_sheep + sheep_in_shed
    placed_animals = active_cows + active_sheep
    animals_in_shed = cows_in_shed + sheep_in_shed

    # ================================================================
    # MARKET ORDERS (max 10 per turn)
    # ================================================================
    market = []

    # --- Sell produce from shed (keep wheat buffer for feeding) ---
    wheat_in_shed = shed.get("WHEAT", 0)
    feed_buffer = placed_animals + 3
    if wheat_in_shed > feed_buffer:
        market.append(["SELL", "WHEAT", wheat_in_shed - feed_buffer])

    for item, qty in shed.items():
        if qty > 0 and item not in ("WHEAT", "COW", "SHEEP"):
            market.append(["SELL", item, qty])

    # --- Land expansion ---
    if day >= 8 and num_unlocked == 25 and money >= 1500:
        market.append(["BUY_LAND"])
    elif day >= 14 and num_unlocked == 50 and money >= 3000:
        market.append(["BUY_LAND"])

    # --- Buy Wheat from market to feed animals (only if shed is low) ---
    wheat_in_shed = shed.get("WHEAT", 0)
    if placed_animals > 0:
        needed_feed = max(0, placed_animals + 2 - wheat_in_shed)
        if needed_feed > 0 and money >= needed_feed * 25:
            buy_n = min(needed_feed, 10)
            market.append(["BUY_PRODUCT", "WHEAT", buy_n])
            money -= buy_n * 25

    # --- Livestock purchasing (gradual, only when we have income flowing) ---
    if day >= 4 and day <= 22:
        # Buy 1 cow when we can afford it
        if total_cows < 3 and money >= 800 and animals_in_shed == 0:
            market.append(["BUY_ANIMAL", "COW", 1])
            money -= 400

        if total_sheep < 2 and money >= 900 and animals_in_shed == 0 and day >= 6:
            market.append(["BUY_ANIMAL", "SHEEP", 1])
            money -= 500

    # --- Buy Strawberry Seeds (High Value for new land) ---
    straw_seeds = seeds.get("STRAWBERRY", 0)
    target_straw_total = 0
    if num_unlocked >= 75 and day <= 18:
        target_straw_total = 55 # Target 55 total for 3 quadrants
    elif num_unlocked >= 50 and day <= 18:
        target_straw_total = 30 # Target 30 total for 2 quadrants
        
    straw_deficit = max(0, target_straw_total - (straw_plants + straw_seeds))
    while straw_deficit > 0 and money >= 100 and len(market) < 8:
        buy_s = min(straw_deficit, int(money // 100), 10)
        if buy_s <= 0:
            break
        market.append(["BUY_SEED", "STRAWBERRY", buy_s])
        money -= buy_s * 100
        straw_deficit -= buy_s
        straw_seeds += buy_s

    # --- Buy wheat seeds ---
    wheat_seeds = seeds.get("WHEAT", 0)
    # Account for tiles that need pastures and strawberries
    needed_pastures = max(0, animals_in_shed - len(empty_pastures))
    plant_slots_for_wheat = max(0, len(empty_tiles) - needed_pastures - straw_seeds)
    target_wheat_seeds = max(0, plant_slots_for_wheat)
    
    # Buy up to 10 seeds per order, allowing multiple orders if we have a large seed deficit.
    seeds_to_buy = max(0, target_wheat_seeds - wheat_seeds)
    while seeds_to_buy > 0 and money >= 10 and len(market) < 8: # Leave room for hiring orders
        buy_w = min(seeds_to_buy, int(money // 10), 10)
        if buy_w <= 0:
            break
        market.append(["BUY_SEED", "WHEAT", buy_w])
        money -= buy_w * 10
        seeds_to_buy -= buy_w

    # --- Hiring ---
    hires_today = me.get("hires_today", 0)
    fib_a, fib_b = 1, 1
    for _ in range(hires_today):
        fib_a, fib_b = fib_b, fib_a + fib_b

    if day <= 28:
        max_hire_cost = 8 if day < 10 else 13
        while fib_a <= max_hire_cost and money >= fib_a:
            market.append(["HIRE"])
            money -= fib_a
            fib_a, fib_b = fib_b, fib_a + fib_b

    market = market[:10]

    # ================================================================
    # UNIT TASK ASSIGNMENT
    # ================================================================
    units = [me["farmer"]] + me.get("hands", [])
    wheat_seeds = seeds.get("WHEAT", 0)
    need_pastures = max(0, animals_in_shed - len(empty_pastures))

    # Mutable task lists
    r_unfed = list(unfed_animals)
    r_harvest = list(harvestable)
    r_water = list(unwatered)
    r_fert = list(fertilizer_tiles)
    r_care = list(care_tiles)
    r_weeds = list(weeds)
    r_empasture = list(empty_pastures)
    r_empty = list(empty_tiles)

    assigned = set()
    farmer_action = ["PASS"]
    hands_actions = []

    for u_idx, u_pos in enumerate(units):
        ux, uy = u_pos
        inv = inventories[u_idx] if u_idx < len(inventories) else {}
        if not isinstance(inv, dict):
            inv = {}

        wheat_in_inv = inv.get("WHEAT", 0)
        has_cow = inv.get("COW", 0) > 0
        has_sheep = inv.get("SHEEP", 0) > 0
        carrying_animal = has_cow or has_sheep
        has_produce = sum(v for k, v in inv.items() if k not in ("WHEAT",)) > 0

        action = None
        here = (ux, uy)
        on_shed = here in SHED_TILES

        # --- Act on current tile ---

        # Place animal on empty pasture
        if carrying_animal and here in r_empasture:
            action = ["PLACE", "COW"] if has_cow else ["PLACE", "SHEEP"]
            r_empasture.remove(here)

        # Feed unfed animal (need wheat in inventory)
        if action is None and here in r_unfed and wheat_in_inv > 0:
            action = ["FEED"]
            r_unfed.remove(here)

        # Harvest
        if action is None and here in r_harvest:
            action = ["HARVEST"]
            r_harvest.remove(here)

        # Water
        if action is None and here in r_water:
            action = ["WATER"]
            r_water.remove(here)

        # Care for animals (increases product yield)
        if action is None and here in r_care:
            action = ["CARE"]
            r_care.remove(here)

        # Collect fertilizer
        if action is None and here in r_fert:
            action = ["COLLECT_FERTILIZER"]
            r_fert.remove(here)

        # Clear weeds
        if action is None and here in r_weeds:
            action = ["DIG"]
            r_weeds.remove(here)

        # Build pasture or plant on empty tile
        if action is None and here in r_empty and not carrying_animal:
            if need_pastures > 0:
                action = ["BUILD_PASTURE"]
                r_empty.remove(here)
                need_pastures -= 1
            elif straw_seeds > 0:
                action = ["PLANT", "STRAWBERRY"]
                r_empty.remove(here)
                straw_seeds -= 1
            elif wheat_seeds > 0:
                action = ["PLANT", "WHEAT"]
                r_empty.remove(here)
                wheat_seeds -= 1

        # --- Shed operations ---
        if action is None and on_shed:
            # Drop produce into shed
            if has_produce and not carrying_animal:
                action = ["DROP"]
            # Pick up wheat to feed animals
            elif len(r_unfed) > 0 and wheat_in_inv < len(r_unfed) and shed.get("WHEAT", 0) > 0 and not carrying_animal:
                pickup_n = min(len(r_unfed) - wheat_in_inv, shed.get("WHEAT", 0))
                if pickup_n > 0:
                    action = ["PICKUP", "WHEAT", pickup_n]
            # Pick up animal to place
            elif not carrying_animal and shed.get("COW", 0) > 0 and len(r_empasture) > 0:
                action = ["PICKUP", "COW", 1]
            elif not carrying_animal and shed.get("SHEEP", 0) > 0 and len(r_empasture) > 0:
                action = ["PICKUP", "SHEEP", 1]

        # --- Move toward best target ---
        if action is None:
            candidates = []

            # Carrying animal → go to empty pasture
            if carrying_animal:
                for t in r_empasture:
                    if t not in assigned:
                        candidates.append((0, t))

            # Have wheat → go feed animals
            if wheat_in_inv > 0 and not carrying_animal:
                for t in r_unfed:
                    if t not in assigned:
                        candidates.append((0, t))

            # Need wheat for feeding → go to shed
            if wheat_in_inv == 0 and len(r_unfed) > 0 and not carrying_animal:
                if shed.get("WHEAT", 0) > 0:
                    for st in SHED_TILES:
                        if st not in assigned:
                            candidates.append((0, st))
                            break

            # Animals in shed need placing → go to shed
            if not carrying_animal and animals_in_shed > 0 and len(r_empasture) > 0:
                for st in SHED_TILES:
                    if st not in assigned:
                        candidates.append((1, st))
                        break

            # Harvest crops/animals
            for t in r_harvest:
                if t not in assigned:
                    candidates.append((1, t))

            # Water crops
            for t in r_water:
                if t not in assigned:
                    candidates.append((2, t))

            # Care for animals
            for t in r_care:
                if t not in assigned:
                    candidates.append((3, t))

            # Collect fertilizer
            for t in r_fert:
                if t not in assigned:
                    candidates.append((3, t))

            # Clear weeds
            for t in r_weeds:
                if t not in assigned:
                    candidates.append((4, t))

            # Plant on empty tiles
            if (wheat_seeds + straw_seeds) > 0 or need_pastures > 0:
                for t in r_empty:
                    if t not in assigned:
                        candidates.append((5, t))

            # Drop produce at shed
            if has_produce:
                for st in SHED_TILES:
                    if st not in assigned:
                        candidates.append((6, st))
                        break

            if candidates:
                candidates.sort(key=lambda c: (c[0], manhattan_dist((ux, uy), c[1])))
                best = candidates[0][1]
                assigned.add(best)
                action = [manhattan_step(u_pos, best)]
            else:
                action = ["PASS"]

        if u_idx == 0:
            farmer_action = action
        else:
            hands_actions.append(action)

    return {"farmer": farmer_action, "hands": hands_actions, "market": market}
