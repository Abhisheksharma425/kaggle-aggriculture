
code = '''# =============================================================================
# Kaggriculture Baseline Agent — Stage 1: Wheat Loop Farmer
# =============================================================================
#
# This is a simple rule-based agent that focuses exclusively on wheat farming.
# Wheat is the cheapest crop ($10/seed), has the shortest time-to-first-yield
# (2 days), and requires minimal micromanagement. The strategy is:
#
#   1. Buy wheat seeds whenever we have money and are running low
#   2. Walk the farm and plant wheat on every empty tile
#   3. Water wheat plants daily (critical — 2 missed days = weed)
#   4. Harvest wheat as soon as it has yield (day 2+)
#   5. Sell all harvested wheat immediately for cash flow
#
# This agent does NOT use:
#   - Fertilizer
#   - Animals
#   - Land expansion
#   - Hired hands
#   - Other crops
#
# It is intentionally minimal so you can see the core game loop clearly and
# build on top of it.
# =============================================================================

import json

# ------------------------------------------------------------------------------
# Game Constants (from README.md)
# ------------------------------------------------------------------------------

SEED_COST = {
    "WHEAT": 10,
    "CARROT": 20,
    "TOMATO": 50,
    "STRAWBERRY": 100,
    "MELON": 80,
}

FIRST_YIELD_DAY = {
    "WHEAT": 2,
    "CARROT": 2,
    "TOMATO": 8,
    "STRAWBERRY": 10,
    "MELON": 10,
}

MAX_YIELD_DAY = {
    "WHEAT": 4,
    "CARROT": 3,
    "TOMATO": 11,
    "STRAWBERRY": 16,
    "MELON": 10,
}

# Wheat-specific constants
WHEAT_SEED_COST = 10
WHEAT_FIRST_YIELD = 2
WHEAT_MAX_YIELD_DAY = 4

# Movement directions
DIRECTIONS = ["NORTH", "SOUTH", "EAST", "WEST"]
DIR_DELTA = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST":  (1, 0),
    "WEST":  (-1, 0),
}

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

def _is_inside(x, y, board_size=10):
    """Return True if (x, y) is inside the farm board."""
    return 0 <= x < board_size and 0 <= y < board_size


def _is_empty_tile(tile):
    """Return True if the tile is empty and unlocked."""
    return tile is None


def _is_plant(tile):
    """Return True if the tile contains a plant dict."""
    return isinstance(tile, dict) and tile.get("kind") == "PLANT"


def _is_weed(tile):
    """Return True if the tile is a weed."""
    return isinstance(tile, dict) and tile.get("kind") == "WEED"


def _is_locked(tile):
    """Return True if the tile is locked."""
    return tile == "LOCKED"


def _is_structure(tile):
    """Return True if the tile is a coop or pasture."""
    return isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE")


# ------------------------------------------------------------------------------
# Main Agent Function
# ------------------------------------------------------------------------------

def agent(obs):
    """
    Receive an observation dict and return an action dict.

    Observation fields used:
      - player          : int (0 or 1)
      - day             : int (0-indexed day of the season)
      - hour            : int (0-indexed turn within the day, 0..23)
      - farms           : list of farm dicts (index = player id)
      - market          : {inventory, prices}
      - town            : {unlocked_shops}
      - private         : {shed, seeds, inventories}

    Action format returned:
      {
        "farmer": [op, ...args],   # one action for the main farmer
        "hands":  [],              # no hired hands in baseline
        "market": [[op, ...], ...],# list of market orders (max 10)
      }
    """
    # --------------------------------------------------------------------------
    # Parse observation
    # --------------------------------------------------------------------------
    player = obs["player"]
    me = obs["farms"][player]          # our farm (public info)
    private = obs["private"]           # our private state
    fx, fy = me["farmer"]              # farmer position (x, y)
    tiles = me["tiles"]                # 2D list: tiles[y][x]
    day = obs["day"]
    hour = obs["hour"]
    money = me["money"]
    shed = private["shed"]
    seeds = private["seeds"]
    market_prices = obs["market"]["prices"]

    # --------------------------------------------------------------------------
    # Build market orders first (independent of farmer position)
    # --------------------------------------------------------------------------
    market = []

    # 1. Buy wheat seeds if we have money and are running low
    wheat_seeds = seeds.get("WHEAT", 0)
    if wheat_seeds < 3 and money >= WHEAT_SEED_COST:
        market.append(["BUY_SEED", "WHEAT", 1])

    # 2. Sell all wheat in the shed immediately for cash flow
    wheat_in_shed = shed.get("WHEAT", 0)
    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])

    # --------------------------------------------------------------------------
    # Decide what the farmer should do based on the tile he is standing on
    # --------------------------------------------------------------------------
    current_tile = tiles[fy][fx]

    # --- Case A: Standing on a weed -> dig it to free the tile ---
    if _is_weed(current_tile):
        return {
            "farmer": ["DIG"],
            "hands": [],
            "market": market,
        }

    # --- Case B: Standing on empty tile -> plant wheat if we have seeds ---
    if _is_empty_tile(current_tile):
        if wheat_seeds > 0:
            return {
                "farmer": ["PLANT", "WHEAT"],
                "hands": [],
                "market": market,
            }
        else:
            # No seeds and (probably) no money -- just pass
            return {
                "farmer": ["PASS"],
                "hands": [],
                "market": market,
            }

    # --- Case C: Standing on a wheat plant -> water or harvest ---
    if _is_plant(current_tile) and current_tile.get("crop") == "WHEAT":
        # If the plant has yield ready, harvest it
        if current_tile.get("yield_units", 0) > 0:
            return {
                "farmer": ["HARVEST"],
                "hands": [],
                "market": market,
            }

        # If not watered today, water it (critical -- don't let it become a weed)
        if not current_tile.get("watered_today", False):
            return {
                "farmer": ["WATER"],
                "hands": [],
                "market": market,
            }

        # Already watered and no yield yet -- nothing to do here, move on
        # Fall through to movement logic below

    # --- Case D: Standing on another crop or structure -- nothing to do ---
    # Fall through to movement logic

    # --------------------------------------------------------------------------
    # Movement: find the next useful tile and walk toward it
    # --------------------------------------------------------------------------
    # Strategy: scan the board looking for tiles that need attention (weeds,
    # empty tiles ready for planting, wheat plants that need watering or
    # harvesting).  We search in row-major order and pick the closest one.
    best_target = None
    best_dist = float("inf")

    for y in range(10):
        for x in range(10):
            tile = tiles[y][x]

            # Skip locked tiles -- we can't act on them
            if _is_locked(tile):
                continue

            # Determine if this tile needs attention
            needs_attention = False
            if _is_weed(tile):
                needs_attention = True
            elif _is_empty_tile(tile) and wheat_seeds > 0:
                needs_attention = True
            elif _is_plant(tile) and tile.get("crop") == "WHEAT":
                if tile.get("yield_units", 0) > 0:
                    needs_attention = True
                elif not tile.get("watered_today", False):
                    needs_attention = True

            if needs_attention:
                # Manhattan distance (we can only move orthogonally)
                dist = abs(x - fx) + abs(y - fy)
                if dist < best_dist:
                    best_dist = dist
                    best_target = (x, y)

    # If we found a target, move one step toward it
    if best_target is not None:
        tx, ty = best_target
        if tx > fx and _is_inside(fx + 1, fy):
            return {
                "farmer": ["EAST"],
                "hands": [],
                "market": market,
            }
        elif tx < fx and _is_inside(fx - 1, fy):
            return {
                "farmer": ["WEST"],
                "hands": [],
                "market": market,
            }
        elif ty > fy and _is_inside(fx, fy + 1):
            return {
                "farmer": ["SOUTH"],
                "hands": [],
                "market": market,
            }
        elif ty < fy and _is_inside(fx, fy - 1):
            return {
                "farmer": ["NORTH"],
                "hands": [],
                "market": market,
            }

    # --------------------------------------------------------------------------
    # Fallback: nothing useful to do -- PASS
    # --------------------------------------------------------------------------
    return {
        "farmer": ["PASS"],
        "hands": [],
        "market": market,
    }
'''

with open('new_main.py', 'w') as f:
    f.write(code)

print("File written successfully")
print(f"Lines: {code.count(chr(10))}")
