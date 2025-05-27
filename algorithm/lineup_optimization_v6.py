"""
PURE PYTHON BDNRP CSV GENERATOR
Uses the brp_calculator.py instead of Excel for maximum speed
"""
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any
from brp_calculator import calculate_brp  # Import your BRP calculator

def generate_bdnrp_csv_python(players: List[str],
                              player_stats: Dict[str, Dict[str, int]],
                              output_csv: str = "bdnrp_values.csv") -> None:
    """
    Generate BDNRP for all distinct 4-tuples using pure Python calculation.
    Much faster than Excel-based approach.
    """
    print(f"[generate_bdnrp_csv_python] Starting CSV generation for {len(players)} players")
    
    rows: List[Dict[str, Any]] = []
    print("[generate_bdnrp_csv_python] Computing 4-tuple combinations...")
    
    combos = [
        (p1, p2, p3, p4)
        for p1 in players
        for p2 in players
        for p3 in players
        for p4 in players
        if len({p1, p2, p3, p4}) == 4
    ]
    
    total = len(combos)
    print(f"[generate_bdnrp_csv_python] Total combinations: {total}")

    for idx_combo, (p1, p2, p3, p4) in enumerate(combos, start=1):
        # Get player stats
        stats1 = player_stats[p1]
        stats2 = player_stats[p2] 
        stats3 = player_stats[p3]
        stats4 = player_stats[p4]
        
        # Calculate BRP using your Python function
        brp_value = calculate_brp(stats1, stats2, stats3, stats4)
        
        rows.append({
            "player1": p1,
            "player2": p2,
            "player3": p3,
            "player4": p4,
            "bdnrp_value": brp_value,
        })

        if idx_combo % 1000 == 0 or idx_combo == total:
            print(f"[generate_bdnrp_csv_python] Processed {idx_combo}/{total} combos")

    print("[generate_bdnrp_csv_python] All combinations processed; writing to CSV...")
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"[generate_bdnrp_csv_python] BDNRP CSV generated: {output_csv}")

def parse_and_optimize_lineup_fast(json_input, method='exhaustive', max_iterations=1000):
    """
    Fast version of parse_and_optimize_lineup using pure Python calculations.
    """
    import json
    
    # Extract handedness constraints
    handedness_constraint = {}
    if "max_consecutive_right" in json_input:
        handedness_constraint["max_consecutive_right"] = json_input["max_consecutive_right"]
    if "max_consecutive_left" in json_input:
        handedness_constraint["max_consecutive_left"] = json_input["max_consecutive_left"]
    
    # Extract player information
    players = []
    player_stats = {}
    player_handedness = {}
    constraints = {}
    
    # Fixed positions (1-9)
    for pos in range(1, 10):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            player_data = json_input[pos_key]
            player_name = player_data["name"]
            players.append(player_name)
            player_stats[player_name] = player_data["data"]
            constraints[player_name] = pos
            player_handedness[player_name] = player_data.get("batting_hand", "R")
    
    # Flexible positions (10-18)
    for pos in range(10, 19):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            player_data = json_input[pos_key]
            player_name = player_data["name"]
            players.append(player_name)
            player_stats[player_name] = player_data["data"]
            constraints[player_name] = pos
            player_handedness[player_name] = player_data.get("batting_hand", "R")

    if len(players) != 9:
        raise ValueError(f"Expected 9 players, but found {len(players)}")
    
    print("Step 1: Generating BDNRP data using Python calculator...")
    bdnrp_csv = "bdnrp_values_python.csv"
    generate_bdnrp_csv_python(players, player_stats, bdnrp_csv)
    
    print("Step 2: Running fast optimization...")
    from fast_lineup_opti import optimize_lineup
    
    # Get top lineup from fast optimizer
    top_lineups = optimize_lineup(players, bdnrp_csv, return_top_n=1)
    best_lineup_names, best_score = top_lineups[0]
    
    # Format result as JSON
    result = {}
    for i, player in enumerate(best_lineup_names):
        result[str(i + 1)] = player
    
    # Calculate expected runs (you may need to adjust this calculation)
    result["expected runs"] = round(best_score, 4)
    
    print(f"\nBest lineup: {best_lineup_names}")
    print(f"Expected run production: {best_score:.4f}")
    
    return result
if __name__ == "__main__":
    # Test with 9 players (you currently only have 2)
    json_input = {
        "10": { 
            "name": "Earle Combs",
             "data": {
                "pa": 6507,
                "h": 1866,
                "2b": 309,
                "3b": 154,
                "hr": 58,
                "sb": 0,
                "bb": 670,
                "hbp": 17,
                "ibb": 0
            },
            "batting_hand": "LEFT"
        },
        "11": { 
            "name": "Mark Koenig",
            "data": {
                "pa": 4603,
                "h": 1190,
                "2b": 195,
                "3b": 49,
                "hr": 28,
                "sb": 0,
                "bb": 222,
                "hbp": 11,
                "ibb": 0
            },
            "batting_hand": "RIGHT"
        },
        "12": { 
            "name": "George Ruth",
            "data": {
                "pa": 10617,
                "h": 2873,
                "2b": 506,
                "3b": 136,
                "hr": 714,
                "sb": 0,
                "bb": 2062,
                "hbp": 43,
                "ibb": 0
            },
            "batting_hand": "LEFT"
        },
        "13": { 
            "name": "Anthony Lazzeri",
            "data": {
                "pa": 7303,
                "h": 1840,
                "2b": 334,
                "3b": 115,
                "hr": 178,
                "sb": 0,
                "bb": 869,
                "hbp": 21,
                "ibb": 0
            },
            "batting_hand": "LEFT"
        },
        "14": { 
            "name": "Henry Gehrig",
            "data": {
                "pa": 9660,
                "h": 2721,
                "2b": 534,
                "3b": 163,
                "hr": 493,
                "sb": 0,
                "bb": 1508,
                "hbp": 45,
                "ibb": 0
            },
            "batting_hand": "RIGHT"
        },
        "15": { 
            "name": "Joseph Dugan",
            "data": {
                "pa": 5879,
                "h": 1516,
                "2b": 277,
                "3b": 46,
                "hr": 42,
                "sb": 0,
                "bb": 250,
                "hbp": 42,
                "ibb": 0
            },
            "batting_hand": "RIGHT"
        },
        "16": { 
            "name": "Robert Meusel",
            "data": {
                "pa": 6028,
                "h": 1693,
                "2b": 368,
                "3b": 95,
                "hr": 156,
                "sb": 0,
                "bb": 375,
                "hbp": 21,
                "ibb": 0
            },
            "batting_hand": "LEFT"
        },
        "17": { 
            "name": "John Grabowski",
            "data": {
                "pa": 885,
                "h": 206,
                "2b": 25,
                "3b": 8,
                "hr": 3,
                "sb": 0,
                "bb": 47,
                "hbp": 2,
                "ibb": 0
            },
            "batting_hand": "RIGHT"
        },
        "18": { 
            "name": "Waite Hoyt",
            "data": {
                "pa": 1419,
                "h": 255,
                "2b": 26,
                "3b": 11,
                "hr": 0,
                "sb": 0,
                "bb": 40,
                "hbp": 1,
                "ibb": 0
            },
            "batting_hand": "LEFT"
        }
    }
    
    result = parse_and_optimize_lineup_fast(json_input)
    print(f"Final result: {json.dumps(result, indent=2)}")