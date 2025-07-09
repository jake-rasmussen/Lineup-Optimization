"""
lineup_optimizer.py

BRP CSV Generator and Lineup Optimizer with Handedness and Positional Constraints
Uses pure Python BRP calculations for maximum speed and efficiency.
"""
import pandas as pd
import json
from typing import List, Dict, Any, Optional, Tuple
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


def parse_positional_constraints(json_input: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str], Dict[int, str], List[int]]:
    """
    Parse JSON input to identify constrained and unconstrained players.
    
    Args:
        json_input: Dictionary containing player data in positions 1-18
        
    Returns:
        Tuple of (all_players_stats, all_players_handedness, constrained_positions, available_positions)
    """
    all_players_stats = {}
    all_players_handedness = {}
    constrained_positions = {}  # batting_position (0-8) -> player_name
    available_positions = []    # List of batting positions (0-8) available for optimization
    
    # Track which batting positions are taken by constrained players
    taken_positions = set()
    
    # Process constrained players (positions 1-9)
    for pos in range(1, 10):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            player_data = json_input[pos_key]
            player_name = player_data["name"]
            batting_position = pos - 1  # Convert to 0-indexed
            
            all_players_stats[player_name] = player_data["data"]
            handedness = player_data.get("batting_hand", "RIGHT").upper()
            all_players_handedness[player_name] = handedness
            constrained_positions[batting_position] = player_name
            taken_positions.add(batting_position)
    
    # Process unconstrained players (positions 10-18)
    unconstrained_players = []
    for pos in range(10, 19):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            player_data = json_input[pos_key]
            player_name = player_data["name"]
            
            all_players_stats[player_name] = player_data["data"]
            handedness = player_data.get("batting_hand", "RIGHT").upper()
            all_players_handedness[player_name] = handedness
            unconstrained_players.append(player_name)
    
    # Determine available positions for unconstrained players
    available_positions = [i for i in range(9) if i not in taken_positions]
    
    if len(unconstrained_players) != len(available_positions):
        raise ValueError(f"Mismatch: {len(unconstrained_players)} unconstrained players but {len(available_positions)} available positions")
    
    return all_players_stats, all_players_handedness, constrained_positions, available_positions, unconstrained_players


def parse_and_optimize_lineup_fast(json_input: Dict[str, Any], 
                                   method: str = 'exhaustive', 
                                   max_iterations: int = 1000) -> Dict[str, Any]:
    """
    Parse JSON input and optimize lineup using fast Python calculations with positional and handedness constraints.
    
    Args:
        json_input: Dictionary containing player data in positions 1-18 and constraints
        method: Optimization method (currently supports 'exhaustive')
        max_iterations: Maximum iterations for optimization
        
    Returns:
        Dictionary with optimized lineup positions and expected runs per cycle
        
    Raises:
        ValueError: If exactly 9 players are not found in the input
    """
    # Extract handedness constraints
    max_consecutive_left = json_input.get("max_consecutive_left", 0)
    max_consecutive_right = json_input.get("max_consecutive_right", 0)
    
    print(f"Handedness constraints - Max consecutive left: {max_consecutive_left}, Max consecutive right: {max_consecutive_right}")
    
    # Parse positional constraints
    all_players_stats, all_players_handedness, constrained_positions, available_positions, unconstrained_players = parse_positional_constraints(json_input)
    
    # Create unified player lists for optimization
    all_players = list(all_players_stats.keys())
    
    if len(all_players) != 9:
        raise ValueError(f"Expected 9 players total, but found {len(all_players)}")
    
    print(f"Positional constraints:")
    print(f"  - Constrained players: {len(constrained_positions)} (fixed in specific batting positions)")
    print(f"  - Unconstrained players: {len(unconstrained_players)} (can be optimized)")
    print(f"  - Available positions for optimization: {[p+1 for p in available_positions]}")
    
    print("Generating BDNRP data using Python calculator...")
    
    _print_player_summary(all_players, all_players_stats, all_players_handedness, constrained_positions, available_positions)
    
    bdnrp_csv = "bdnrp_values_python.csv"
    generate_bdnrp_csv_python(all_players, all_players_stats, bdnrp_csv)
    
    print("Running fast optimization with constraints...")
    from lineup_calculator import optimize_lineup
    
    # Create player index mappings
    player_to_idx = {player: idx for idx, player in enumerate(all_players)}
    handedness_list = [all_players_handedness[player] for player in all_players]
    
    # Convert constraints to use player indices
    constrained_positions_idx = {pos: player_to_idx[player] for pos, player in constrained_positions.items()}
    print("Final constraints (index-based):", constrained_positions_idx)
    
    unconstrained_players_idx = [player_to_idx[player] for player in unconstrained_players]
    
    top_lineups = optimize_lineup(
        all_players, 
        bdnrp_csv, 
        return_top_n=1,
        player_handedness=handedness_list,
        max_consecutive_left=max_consecutive_left,
        max_consecutive_right=max_consecutive_right,
        constrained_positions=constrained_positions_idx,
        unconstrained_players=unconstrained_players_idx,
        available_positions=available_positions
    )
    
    if not top_lineups:
        raise ValueError("No valid lineups found with the given constraints")
    
    best_lineup_names, best_score = top_lineups[0]
    
    print(f"Raw optimization score: {best_score:.6f}")
    print(f"Best lineup found: {best_lineup_names}")
    
    # Verify the lineup satisfies constraints
    _verify_lineup_constraints(best_lineup_names, all_players_handedness, 
                             max_consecutive_left, max_consecutive_right)
    _verify_positional_constraints(best_lineup_names, constrained_positions)
    
    # Format result
    result = {}
    for i, player in enumerate(best_lineup_names):
        result[str(i + 1)] = player
    
    # Calculate expected runs per cycle (9 players)
    # Scale the raw BRP score to represent meaningful expected runs per cycle
    # The BRP calculation is optimized for relative comparison, but needs scaling for interpretable output
    
    # Scaling factor to convert BRP score to expected runs per cycle
    # This converts the optimization score to a realistic runs-per-cycle estimate
    cycle_scaling_factor = 4.5  
    
    # Apply scaling to get interpretable expected runs per cycle
    expected_runs_per_cycle = best_score * cycle_scaling_factor

    
    result["expected runs"] = round(expected_runs_per_cycle, 4)
    
    print(f"\nBest lineup: {best_lineup_names}")
    print(f"Raw BRP score: {best_score:.6f}")
    print(f"Expected runs per cycle: {expected_runs_per_cycle:.4f}")
    
    return {
        "lineup": {str(i + 1): player for i, player in enumerate(best_lineup_names)},
        "expectedRuns": round(expected_runs_per_cycle, 4)
    }

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


def _verify_positional_constraints(lineup: List[str], constrained_positions: Dict[int, str]) -> None:
    """Verify that constrained players are in their correct positions."""
    print("Verifying positional constraints...")
    for batting_pos, expected_player in constrained_positions.items():
        actual_player = lineup[batting_pos]
        if actual_player != expected_player:
            raise ValueError(f"Positional constraint violated: Position {batting_pos + 1} should have {expected_player} but has {actual_player}")
        print(f"  ✅ Position {batting_pos + 1}: {expected_player} (constrained)")


def _print_player_summary(players: List[str], 
                         player_stats: Dict[str, Dict[str, int]],
                         player_handedness: Dict[str, str],
                         constrained_positions: Dict[int, str],
                         available_positions: List[int]) -> None:
    """Print a summary of player performance statistics, handedness, and constraints."""
    print("\nPlayer Performance Summary:")
    print(f"{'Player':<20} | {'Hand':<6} | {'Constraint':<12} | {'PA':<3} | {'AVG':<5} | {'OBP':<5} | {'SLG':<5} | {'OPS':<5}")
    print("-" * 85)
    
    # Create reverse lookup for constrained positions
    player_to_constraint = {player: f"Fixed Pos {pos+1}" for pos, player in constrained_positions.items()}
    
    for player in players:
        stats = player_stats[player]
        handedness = player_handedness[player]
        constraint_info = player_to_constraint.get(player, "Optimizable")
        
        avg = stats["h"] / stats["pa"] if stats["pa"] > 0 else 0
        obp = (stats["h"] + stats["bb"] + stats["hbp"]) / stats["pa"] if stats["pa"] > 0 else 0
        slg = (stats["h"] - stats["2b"] - stats["3b"] - stats["hr"] + 2*stats["2b"] + 3*stats["3b"] + 4*stats["hr"]) / stats["pa"] if stats["pa"] > 0 else 0
        ops = obp + slg
        print(f"{player:<20} | {handedness:<6} | {constraint_info:<12} | {stats['pa']:3} | {avg:.3f} | {obp:.3f} | {slg:.3f} | {ops:.3f}")


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
    
    # Validate that we have player data in correct positions
    found_players = 0
    constrained_players = 0
    unconstrained_players = 0
    
    # Check positions 1-9 (constrained) and 10-18 (unconstrained)
    valid_positions = [str(i) for i in range(1, 10)] + [str(i) for i in range(10, 19)]
    
    for pos in valid_positions:
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
            if int(pos) <= 9:
                constrained_players += 1
            else:
                unconstrained_players += 1
    
    if found_players != 9:
        raise ValueError(f"Expected exactly 9 players, found {found_players}")
    
    # Validate that we don't have conflicting positions (player in both constrained and unconstrained)
    constrained_names = set()
    unconstrained_names = set()
    
    for pos in range(1, 10):
        if str(pos) in data and data[str(pos)] is not None:
            constrained_names.add(data[str(pos)]["name"])
    
    for pos in range(10, 19):
        if str(pos) in data and data[str(pos)] is not None:
            unconstrained_names.add(data[str(pos)]["name"])
    
    overlap = constrained_names.intersection(unconstrained_names)
    if overlap:
        raise ValueError(f"Players appear in both constrained and unconstrained positions: {overlap}")
    
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
    Entry point for optimizing lineup from JSON input.
    
    Args:
        json_input: JSON string containing player data and constraints
        
    Returns:
        JSON string with optimized lineup results in format:
        {
            "1": "player_name",
            ...
            "9": "player_name", 
            "expected runs": float
        }
    """
    parsed_data = parse_json_input(json_input)
    result = parse_and_optimize_lineup_fast(parsed_data)
    return json.dumps(result, indent=2)