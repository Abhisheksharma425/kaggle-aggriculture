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

CROP_FIRST_YIELD = {
    "WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10
}


def agent(obs):
    """
    Hybrid Super-Bot Strategy (Experimental):
    Combines workforce scaling & livestock feeding pipeline from main.py with:
    1. Day-0 Melon Launchpad (12 Melon seeds -> $16k+ payout on Day 11).
    2. Mass Ongoing Strawberry Engine (30-34 Strawberry plants for $4k-$8k daily passive income).
    3. Fast Quadrant Expansion (Day 7 NE, Day 12 SW, Day 13 SE).
    4. Multi-Unit Hired Hands Pipeline (Fibonacci hiring up to cost 13).
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
    # MARKET ORDERS
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

    # --- Fast Quadrant Expansion ---
    if day >= 7 and num_unlocked == 25 and money >= 1000:
        market.append(["BUY_LAND"])
    elif day >= 12 and num_unlocked == 50 and money >= 2000:
        market.append(["BUY_LAND"])
    elif day >= 13 and num_unlocked == 75 and money >= 4000:
        market.append(["BUY_LAND"])

    # --- Buy Wheat from market to feed animals ---
    if placed_animals > 0:
        needed_feed = max(0, placed_animals + 2 - wheat_in_shed)
        if needed_feed > 0 and money >= needed_feed * 25:
            buy_n = min(needed_feed, 10)
            market.append(["BUY_PRODUCT", "WHEAT", buy_n])
            money -= buy_n * 25

    # --- Livestock Purchasing ---
    if day <= 1:
        if total_cows < 2 and money >= 400:
            market.append(["BUY_ANIMAL", "COW", 1])
            money -= 400
            total_cows += 1
        if total_sheep < 2 and money >= 500:
            market.append(["BUY_ANIMAL", "SHEEP", 1])
            money -= 500
            total_sheep += 1
    elif day <= 20:
        if total_cows < 6 and money >= 800:
            market.append(["BUY_ANIMAL", "COW", 1])
            money -= 400
            total_cows += 1
        elif total_sheep < 10 and money >= 800:
            market.append(["BUY_ANIMAL", "SHEEP", 1])
            money -= 500
            total_sheep += 1

    # --- Seed Purchasing: Day 0 Melon Blitz -> Mass Strawberries + Wheat ---
    melon_seeds = seeds.get("MELON", 0)
    straw_seeds = seeds.get("STRAWBERRY", 0)
    wheat_seeds = seeds.get("WHEAT", 0)

    # Day 0-3: Buy 12 Melon seeds ($80 each)
    if day <= 4 and (melon_plants + melon_seeds) < 12 and money >= 80:
        needed_m = 12 - (melon_plants + melon_seeds)
        buy_m = min(needed_m, int(money // 80))
        if buy_m > 0:
            market.append(["BUY_SEED", "MELON", buy_m])
            money -= buy_m * 80
            melon_seeds += buy_m

    # Day 5-20: Mass Strawberry engine (target ~30 strawberry plants)
    if day >= 5 and day <= 20 and (straw_plants + straw_seeds) < 30 and money >= 100:
        needed_s = 30 - (straw_plants + straw_seeds)
        buy_s = min(needed_s, int(money // 100), 5)
        if buy_s > 0:
            market.append(["BUY_SEED", "STRAWBERRY", buy_s])
            money -= buy_s * 100
            straw_seeds += buy_s

    # Fill remaining space with Wheat seeds
    needed_pastures = max(0, (total_cows + total_sheep) - (active_cows + active_sheep + len(empty_pastures)))
    available_slots = len(empty_tiles) - needed_pastures
    if wheat_seeds < available_slots and money >= 10 and day <= 25:
        buy_w = min(available_slots - wheat_seeds, int(money // 10), 10)
        if buy_w > 0:
            market.append(["BUY_SEED", "WHEAT", buy_w])
            money -= buy_w * 10

    # --- Hiring (Workforce Scaling up to Fibonacci cost 13) ---
    hires_today = me.get("hires_today", 0)
    fib_a, fib_b = 1, 1
    for _ in range(hires_today):
        fib_a, fib_b = fib_b, fib_a + fib_b

    if day <= 28:
        max_hire_cost = 13  # Fib: 1, 1, 2, 3, 5, 8, 13
        while fib_a <= max_hire_cost and money >= fib_a:
            market.append(["HIRE"])
            money -= fib_a
            fib_a, fib_b = fib_b, fib_a + fib_b

    market = market[:10]

    # ================================================================
    # MULTI-UNIT TASK ASSIGNMENT
    # ================================================================
    units = [me["farmer"]] + me.get("hands", [])
    wheat_seeds = seeds.get("WHEAT", 0)
    straw_seeds = seeds.get("STRAWBERRY", 0)
    melon_seeds = seeds.get("MELON", 0)
    need_pastures = max(0, (total_cows + total_sheep) - (active_cows + active_sheep + len(empty_pastures)))

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

        # Care
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
            elif melon_seeds > 0:
                action = ["PLANT", "MELON"]
                r_empty.remove(here)
                melon_seeds -= 1
            elif straw_seeds > 0:
                action = ["PLANT", "STRAWBERRY"]
                r_empty.remove(here)
                straw_seeds -= 1
            elif wheat_seeds > 0:
                action = ["PLANT", "WHEAT"]
                r_empty.remove(here)
                wheat_seeds -= 1

        # Shed operations
        if action is None and on_shed:
            if has_produce and not carrying_animal:
                action = ["DROP"]
            elif len(r_unfed) > 0 and wheat_in_inv < len(r_unfed) and shed.get("WHEAT", 0) > 0 and not carrying_animal:
                pickup_n = min(len(r_unfed) - wheat_in_inv, shed.get("WHEAT", 0))
                if pickup_n > 0:
                    action = ["PICKUP", "WHEAT", pickup_n]
            elif not carrying_animal and shed.get("COW", 0) > 0 and len(r_empasture) > 0:
                action = ["PICKUP", "COW", 1]
            elif not carrying_animal and shed.get("SHEEP", 0) > 0 and len(r_empasture) > 0:
                action = ["PICKUP", "SHEEP", 1]

        # Move toward best target
        if action is None:
            candidates = []

            if carrying_animal:
                for t in r_empasture:
                    if t not in assigned:
                        candidates.append((0, t))

            if wheat_in_inv > 0 and not carrying_animal:
                for t in r_unfed:
                    if t not in assigned:
                        candidates.append((0, t))

            if wheat_in_inv == 0 and len(r_unfed) > 0 and not carrying_animal:
                if shed.get("WHEAT", 0) > 0:
                    for st in SHED_TILES:
                        if st not in assigned:
                            candidates.append((0, st))
                            break

            if not carrying_animal and animals_in_shed > 0 and len(r_empasture) > 0:
                for st in SHED_TILES:
                    if st not in assigned:
                        candidates.append((1, st))
                        break

            for t in r_harvest:
                if t not in assigned:
                    candidates.append((1, t))

            for t in r_water:
                if t not in assigned:
                    candidates.append((2, t))

            for t in r_care:
                if t not in assigned:
                    candidates.append((3, t))

            for t in r_fert:
                if t not in assigned:
                    candidates.append((3, t))

            for t in r_weeds:
                if t not in assigned:
                    candidates.append((4, t))

            if (melon_seeds + straw_seeds + wheat_seeds) > 0 or need_pastures > 0:
                for t in r_empty:
                    if t not in assigned:
                        candidates.append((5, t))

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
