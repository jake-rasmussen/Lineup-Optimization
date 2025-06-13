"""
lineup_optimizer.py

BRP CSV Generator and Lineup Optimizer with Handedness Constraints
Uses pure Python BRP calculations for maximum speed and efficiency.
"""
import pandas as pd
import json
from typing import List, Dict, Any
from brp_calculator import calculate_brp


def generate_bdnrp_csv_python(players: List[str],
                              player_stats: Dict[str, Dict[str, int]],
                              output_csv: str = "bdnrp_values.csv") -> None:
    """
    Generate BDNRP values for all distinct 4-tuples using pure Python calculation.
    
    Args:
        players: List of player names
        player_stats: Dictionary mapping player names to their statistics
        output_csv: Output CSV filename for BDNRP values
    """
    print(f"Starting CSV generation for {len(players)} players")
    
    rows: List[Dict[str, Any]] = []
    
    combos = [
        (p1, p2, p3, p4)
        for p1 in players
        for p2 in players
        for p3 in players
        for p4 in players
        if len({p1, p2, p3, p4}) == 4
    ]
    
    total = len(combos)
    print(f"Total combinations: {total}")

    for idx_combo, (p1, p2, p3, p4) in enumerate(combos, start=1):
        stats1 = player_stats[p1]
        stats2 = player_stats[p2] 
        stats3 = player_stats[p3]
        stats4 = player_stats[p4]
        
        brp_value = calculate_brp(stats1, stats2, stats3, stats4)
        
        rows.append({
            "player1": p1,
            "player2": p2,
            "player3": p3,
            "player4": p4,
            "bdnrp_value": brp_value,
        })

        if idx_combo % 1000 == 0 or idx_combo == total:
            print(f"Processed {idx_combo}/{total} combinations")

    print("Writing results to CSV...")
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"BDNRP CSV generated: {output_csv}")


def parse_and_optimize_lineup_fast(json_input: Dict[str, Any], 
                                   method: str = 'exhaustive', 
                                   max_iterations: int = 1000) -> Dict[str, Any]:
    """
    Parse JSON input and optimize lineup using fast Python calculations with handedness constraints.
    
    Args:
        json_input: Dictionary containing player data in positions 1-18 and handedness constraints
        method: Optimization method (currently supports 'exhaustive')
        max_iterations: Maximum iterations for optimization
        
    Returns:
        Dictionary with optimized lineup positions and expected runs
        
    Raises:
        ValueError: If exactly 9 players are not found in the input
    """
    # Extract handedness constraints
    max_consecutive_left = json_input.get("max_consecutive_left", 0)
    max_consecutive_right = json_input.get("max_consecutive_right", 0)
    
    print(f"Handedness constraints - Max consecutive left: {max_consecutive_left}, Max consecutive right: {max_consecutive_right}")
    
    players = []
    player_stats = {}
    player_handedness = {}
    constraints = {}
    
    # Process all positions (1-18)
    for pos in range(1, 19):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            player_data = json_input[pos_key]
            player_name = player_data["name"]
            players.append(player_name)
            player_stats[player_name] = player_data["data"]
            constraints[player_name] = pos
            handedness = player_data.get("batting_hand", "RIGHT").upper()
            player_handedness[player_name] = handedness

    if len(players) != 9:
        raise ValueError(f"Expected 9 players, but found {len(players)}")
    
    print("Generating BDNRP data using Python calculator...")
    
    _print_player_summary(players, player_stats, player_handedness)
    
    bdnrp_csv = "bdnrp_values_python.csv"
    generate_bdnrp_csv_python(players, player_stats, bdnrp_csv)
    
    print("Running fast optimization with constraints...")
    from lineup_calculator import optimize_lineup
    
    # Create handedness list in player order
    handedness_list = [player_handedness[player] for player in players]
    
    top_lineups = optimize_lineup(
        players, 
        bdnrp_csv, 
        return_top_n=1,
        player_handedness=handedness_list,
        max_consecutive_left=max_consecutive_left,
        max_consecutive_right=max_consecutive_right
    )
    
    if not top_lineups:
        raise ValueError("No valid lineups found with the given constraints")
    
    best_lineup_names, best_score = top_lineups[0]
    
    print(f"Raw optimization score: {best_score:.6f}")
    print(f"Best lineup found: {best_lineup_names}")
    
    # Verify the lineup satisfies constraints
    _verify_lineup_constraints(best_lineup_names, player_handedness, 
                             max_consecutive_left, max_consecutive_right)
    
    # Format result
    result = {}
    for i, player in enumerate(best_lineup_names):
        result[str(i + 1)] = player
    
    # Calculate expected runs with baseline adjustment
    baseline_runs_per_game = 4.5
    adjusted_score = (best_score + baseline_runs_per_game) * 1.5
    result["expected runs"] = round(adjusted_score, 4)
    
    print(f"\nBest lineup: {best_lineup_names}")
    print(f"Raw BRP score: {best_score:.4f}")
    print(f"Adjusted expected runs: {adjusted_score:.4f}")
    
    return result


def _verify_lineup_constraints(lineup: List[str], 
                             player_handedness: Dict[str, str],
                             max_consecutive_left: int,
                             max_consecutive_right: int) -> None:
    """Verify that the lineup satisfies handedness constraints."""
    if max_consecutive_left == 0 and max_consecutive_right == 0:
        return
    
    # Check consecutive handedness (including wraparound)
    extended_lineup = lineup + lineup
    consecutive_left = 0
    consecutive_right = 0
    max_left_found = 0
    max_right_found = 0
    
    for i in range(18):
        player = extended_lineup[i]
        handedness = player_handedness[player]
        
        if handedness == 'LEFT':
            consecutive_left += 1
            consecutive_right = 0
            max_left_found = max(max_left_found, consecutive_left)
        elif handedness == 'RIGHT':
            consecutive_right += 1
            consecutive_left = 0
            max_right_found = max(max_right_found, consecutive_right)
        else:  # SWITCH
            consecutive_left = 0
            consecutive_right = 0
    
    print(f"Lineup verification - Max consecutive left found: {max_left_found}, Max consecutive right found: {max_right_found}")
    
    if max_consecutive_left > 0 and max_left_found > max_consecutive_left:
        raise ValueError(f"Lineup violates left-handed constraint: {max_left_found} > {max_consecutive_left}")
    if max_consecutive_right > 0 and max_right_found > max_consecutive_right:
        raise ValueError(f"Lineup violates right-handed constraint: {max_right_found} > {max_consecutive_right}")


def _print_player_summary(players: List[str], 
                         player_stats: Dict[str, Dict[str, int]],
                         player_handedness: Dict[str, str]) -> None:
    """Print a summary of player performance statistics and handedness."""
    print("\nPlayer Performance Summary:")
    print(f"{'Player':<20} | {'Hand':<6} | {'PA':<3} | {'AVG':<5} | {'OBP':<5} | {'SLG':<5} | {'OPS':<5}")
    print("-" * 75)
    
    for player in players:
        stats = player_stats[player]
        handedness = player_handedness[player]
        avg = stats["h"] / stats["pa"] if stats["pa"] > 0 else 0
        obp = (stats["h"] + stats["bb"] + stats["hbp"]) / stats["pa"] if stats["pa"] > 0 else 0
        slg = (stats["h"] - stats["2b"] - stats["3b"] - stats["hr"] + 2*stats["2b"] + 3*stats["3b"] + 4*stats["hr"]) / stats["pa"] if stats["pa"] > 0 else 0
        ops = obp + slg
        print(f"{player:<20} | {handedness:<6} | {stats['pa']:3} | {avg:.3f} | {obp:.3f} | {slg:.3f} | {ops:.3f}")


def parse_json_input(json_data: str) -> Dict[str, Any]:
    """
    Parse JSON string input and validate structure.
    
    Args:
        json_data: JSON string containing player data and constraints
        
    Returns:
        Parsed dictionary with player information and constraints
        
    Raises:
        json.JSONDecodeError: If JSON is malformed
        ValueError: If required fields are missing
    """
    try:
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON format: {e}")
    
    # Validate that we have player data
    player_positions = [str(i) for i in range(1, 19)]
    found_players = 0
    
    for pos in player_positions:
        if pos in data and data[pos] is not None:
            player_data = data[pos]
            if "name" not in player_data or "data" not in player_data:
                raise ValueError(f"Player in position {pos} missing required 'name' or 'data' fields")
            
            required_stats = ["pa", "h", "2b", "3b", "hr", "sb", "bb", "hbp", "ibb"]
            for stat in required_stats:
                if stat not in player_data["data"]:
                    raise ValueError(f"Player {player_data['name']} missing required stat: {stat}")
            
            # Validate handedness if provided
            if "batting_hand" in player_data:
                handedness = player_data["batting_hand"].upper()
                if handedness not in ["LEFT", "RIGHT", "SWITCH"]:
                    raise ValueError(f"Invalid batting_hand '{player_data['batting_hand']}' for player {player_data['name']}. Must be LEFT, RIGHT, or SWITCH.")
            
            found_players += 1
    
    if found_players != 9:
        raise ValueError(f"Expected exactly 9 players, found {found_players}")
    
    # Validate handedness constraints if provided
    if "max_consecutive_left" in data:
        if not isinstance(data["max_consecutive_left"], int) or data["max_consecutive_left"] < 0:
            raise ValueError("max_consecutive_left must be a non-negative integer")
    
    if "max_consecutive_right" in data:
        if not isinstance(data["max_consecutive_right"], int) or data["max_consecutive_right"] < 0:
            raise ValueError("max_consecutive_right must be a non-negative integer")
    
    return data


def optimize_from_json(json_input: str) -> str:
    """
    Main entry point for optimizing lineup from JSON input.
    
    Args:
        json_input: JSON string containing player data and constraints
        
    Returns:
        JSON string with optimized lineup results
    """
    parsed_data = parse_json_input(json_input)
    result = parse_and_optimize_lineup_fast(parsed_data)
    return json.dumps(result, indent=2)