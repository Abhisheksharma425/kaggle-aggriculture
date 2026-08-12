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
    Rank 2 Strategy (Kawashige Clone):
    1. Zero Hired Hands (saves ~$20k in daily hiring costs).
    2. Day-0 Melon Blitz (12 Melon seeds + 2 Cows + 2 Sheep).
    3. Mass Strawberry Engine (30-34 Strawberry plants for $4k-$8k daily passive income).
    4. Fast Quadrant Expansion (Day 7 NE, Day 12 SW, Day 13 SE).
    5. Integrated 4-step Feeding/Care pipeline for Milk, Wool, and Fertilizer.
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
    # MARKET ORDERS (NO HIRING - ZERO HANDS)
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

    # --- Livestock Purchasing (Day 0 Blitz + Midgame Expansion) ---
    if day <= 1:
        if total_cows < 2 and money >= 400:
            market.append(["BUY_ANIMAL", "COW", 1])
            money -= 400
            total_cows += 1
        if total_sheep < 2 and money >= 500:
            market.append(["BUY_ANIMAL", "SHEEP", 1])
            money -= 500
            total_sheep += 1
    elif day <= 18:
        if total_cows < 6 and money >= 800:
            market.append(["BUY_ANIMAL", "COW", 1])
            money -= 400
            total_cows += 1
        elif total_sheep < 12 and money >= 800:
            market.append(["BUY_ANIMAL", "SHEEP", 1])
            money -= 500
            total_sheep += 1

    # --- Seed Purchasing: Day 0 Melon Blitz -> Mass Strawberry Engine ---
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

    # Day 5-20: Mass Strawberry engine (target ~34 strawberry plants)
    if day >= 5 and day <= 20 and (straw_plants + straw_seeds) < 34 and money >= 100:
        needed_s = 34 - (straw_plants + straw_seeds)
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

    market = market[:10]

    # ================================================================
    # MAIN FARMER SINGLE-UNIT TASK ASSIGNMENT
    # ================================================================
    u_pos = me["farmer"]
    ux, uy = u_pos
    inv = inventories[0] if inventories else {}
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
    need_pastures = max(0, (total_cows + total_sheep) - (active_cows + active_sheep + len(empty_pastures)))

    # --- Act on current tile ---
    if carrying_animal and here in empty_pastures:
        action = ["PLACE", "COW"] if has_cow else ["PLACE", "SHEEP"]
        empty_pastures.remove(here)

    if action is None and here in unfed_animals and wheat_in_inv > 0:
        action = ["FEED"]
        unfed_animals.remove(here)

    if action is None and here in harvestable:
        action = ["HARVEST"]
        harvestable.remove(here)

    if action is None and here in unwatered:
        action = ["WATER"]
        unwatered.remove(here)

    if action is None and here in care_tiles:
        action = ["CARE"]
        care_tiles.remove(here)

    if action is None and here in fertilizer_tiles:
        action = ["COLLECT_FERTILIZER"]
        fertilizer_tiles.remove(here)

    if action is None and here in weeds:
        action = ["DIG"]
        weeds.remove(here)

    if action is None and here in empty_tiles and not carrying_animal:
        if need_pastures > 0:
            action = ["BUILD_PASTURE"]
            empty_tiles.remove(here)
            need_pastures -= 1
        elif melon_seeds > 0:
            action = ["PLANT", "MELON"]
            empty_tiles.remove(here)
            melon_seeds -= 1
        elif straw_seeds > 0:
            action = ["PLANT", "STRAWBERRY"]
            empty_tiles.remove(here)
            straw_seeds -= 1
        elif wheat_seeds > 0:
            action = ["PLANT", "WHEAT"]
            empty_tiles.remove(here)
            wheat_seeds -= 1

    # --- Shed operations ---
    if action is None and on_shed:
        if has_produce and not carrying_animal:
            action = ["DROP"]
        elif len(unfed_animals) > 0 and wheat_in_inv < len(unfed_animals) and shed.get("WHEAT", 0) > 0 and not carrying_animal:
            pickup_n = min(len(unfed_animals) - wheat_in_inv, shed.get("WHEAT", 0))
            if pickup_n > 0:
                action = ["PICKUP", "WHEAT", pickup_n]
        elif not carrying_animal and shed.get("COW", 0) > 0 and len(empty_pastures) > 0:
            action = ["PICKUP", "COW", 1]
        elif not carrying_animal and shed.get("SHEEP", 0) > 0 and len(empty_pastures) > 0:
            action = ["PICKUP", "SHEEP", 1]

    # --- Move toward best target ---
    if action is None:
        candidates = []

        if carrying_animal:
            for t in empty_pastures:
                candidates.append((0, t))

        if wheat_in_inv > 0 and not carrying_animal:
            for t in unfed_animals:
                candidates.append((0, t))

        if wheat_in_inv == 0 and len(unfed_animals) > 0 and not carrying_animal:
            if shed.get("WHEAT", 0) > 0:
                for st in SHED_TILES:
                    candidates.append((0, st))
                    break

        if not carrying_animal and (shed.get("COW", 0) > 0 or shed.get("SHEEP", 0) > 0) and len(empty_pastures) > 0:
            for st in SHED_TILES:
                candidates.append((1, st))
                break

        for t in harvestable:
            candidates.append((1, t))

        for t in unwatered:
            candidates.append((2, t))

        for t in care_tiles:
            candidates.append((3, t))

        for t in fertilizer_tiles:
            candidates.append((3, t))

        for t in weeds:
            candidates.append((4, t))

        if (melon_seeds + straw_seeds + wheat_seeds) > 0 or need_pastures > 0:
            for t in empty_tiles:
                candidates.append((5, t))

        if has_produce:
            for st in SHED_TILES:
                candidates.append((6, st))
                break

        if candidates:
            candidates.sort(key=lambda c: (c[0], manhattan_dist((ux, uy), c[1])))
            best = candidates[0][1]
            action = [manhattan_step(u_pos, best)]
        else:
            action = ["PASS"]

    return {"farmer": action, "hands": [], "market": market}
