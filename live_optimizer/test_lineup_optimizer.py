"""
test_lineup_optimizer.py

Test script for the lineup optimizer using sample Dodgers data with positional and handedness constraints.
"""
import json
from lineup_optimizer import parse_and_optimize_lineup_fast, optimize_from_json

def main():
    """
    Test the lineup optimizer with sample Dodgers player data, positional constraints, and handedness constraints.
    """
    # Test JSON data with positional constraints
    # Positions 1-9: Locked to specific batting order positions
    # Positions 11-18: Can be optimized into available spots
    json_input = {
        # CONSTRAINED PLAYERS (Fixed in specific batting positions)
        "16": {  # Locked in leadoff spot
            "name": "Shohei Ohtani",
            "data": {"pa": 3842, "h": 939, "2b": 176, "3b": 40, "hr": 243,
                     "sb": 0, "bb": 464, "hbp": 22, "ibb": 74},
            "batting_hand": "LEFT"
        },
        "17": {  # Locked in 3rd spot
            "name": "Markus Betts",
            "data": {"pa": 6493, "h": 1665, "2b": 376, "3b": 40, "hr": 279,
                     "sb": 0, "bb": 699, "hbp": 50, "ibb": 33},
            "batting_hand": "RIGHT"
        },
        "18": {  # Locked in cleanup spot
            "name": "Frederick Freeman",
            "data": {"pa": 8914, "h": 2322, "2b": 522, "3b": 32, "hr": 352,
                     "sb": 0, "bb": 1029, "hbp": 109, "ibb": 139},
            "batting_hand": "LEFT"
        },
        
        # UNCONSTRAINED PLAYERS (Can be optimized into positions 2, 5, 6, 7, 8, 9)
        "10": { 
            "name": "Andy Pages",
            "data": {"pa": 641, "h": 149, "2b": 29, "3b": 2, "hr": 22,
                     "sb": 0, "bb": 39, "hbp": 9, "ibb": 0},
            "batting_hand": "RIGHT"
        },
        "11": { 
            "name": "Teoscar Hernandez",
            "data": {"pa": 4019, "h": 974, "2b": 206, "3b": 14, "hr": 202,
                     "sb": 0, "bb": 283, "hbp": 31, "ibb": 8},
            "batting_hand": "RIGHT"
        },
        "12": { 
            "name": "Enrique Hernandez",
            "data": {"pa": 4014, "h": 854, "2b": 194, "3b": 15, "hr": 127,
                     "sb": 0, "bb": 351, "hbp": 27, "ibb": 12},
            "batting_hand": "RIGHT"
        },
        "13": { 
            "name": "Dalton Rushing",
            "data": {"pa": 17, "h": 4, "2b": 1, "3b": 0, "hr": 0,
                     "sb": 0, "bb": 1, "hbp": 0, "ibb": 0},
            "batting_hand": "LEFT"
        },
        "14": { 
            "name": "Miguel Rojas",
            "data": {"pa": 3922, "h": 931, "2b": 179, "3b": 11, "hr": 51,
                     "sb": 0, "bb": 246, "hbp": 42, "ibb": 16},
            "batting_hand": "RIGHT"
        },
        "15": { 
            "name": "Thomas Edman",
            "data": {"pa": 2725, "h": 654, "2b": 131, "3b": 21, "hr": 67,
                     "sb": 0, "bb": 169, "hbp": 34, "ibb": 4},
            "batting_hand": "SWITCH"
        },
        
        # Handedness constraints
        "max_consecutive_left": 2,   # No more than 2 consecutive left-handed batters
        "max_consecutive_right": 4   # No more than 4 consecutive right-handed batters
    }

    print("="*80)
    print("LINEUP OPTIMIZER TEST WITH POSITIONAL AND HANDEDNESS CONSTRAINTS")
    print("="*80)
    
    # Count constrained vs unconstrained players
    constrained_count = len([k for k in json_input.keys() if k.isdigit() and int(k) <= 9])
    unconstrained_count = len([k for k in json_input.keys() if k.isdigit() and int(k) >= 11])
    
    print(f"Testing with {constrained_count + unconstrained_count} Dodgers players:")
    print(f"  - {constrained_count} players with fixed batting positions")
    print(f"  - {unconstrained_count} players that can be optimized")
    print(f"Handedness constraints: Max {json_input['max_consecutive_left']} consecutive lefties, Max {json_input['max_consecutive_right']} consecutive righties")
    
    print("\nConstrained Players (Fixed Positions):")
    for pos in range(1, 10):
        if str(pos) in json_input and json_input[str(pos)]:
            player_data = json_input[str(pos)]
            print(f"  Position {pos}: {player_data['name']} ({player_data['batting_hand']})")
    
    print("\nUnconstrained Players (Can be optimized):")
    for pos in range(10, 19):
        if str(pos) in json_input and json_input[str(pos)]:
            player_data = json_input[str(pos)]
            print(f"  {player_data['name']} ({player_data['batting_hand']})")
    
    available_positions = [i for i in range(1, 10) if str(i) not in json_input or json_input[str(i)] is None]
    print(f"\nAvailable positions for optimization: {available_positions}")
    
    print("\n" + "="*80)

    # Method 1: Using the direct function
    print("Method 1: Direct function call with constraints")
    print("-" * 50)
    try:
        result = parse_and_optimize_lineup_fast(json_input)
        print("✅ Optimization successful!")
        print("\nOptimal Batting Order:")
        for pos in range(1, 10):
            player = result[str(pos)]
            handedness = None
            constraint_type = None
            
            # Find handedness and constraint type for display
            for key, player_data in json_input.items():
                if key.isdigit() and player_data and player_data["name"] == player:
                    handedness = player_data["batting_hand"]
                    if int(key) <= 9:
                        constraint_type = "FIXED"
                    else:
                        constraint_type = "OPTIMIZED"
                    break
            
            print(f"{pos}. {player:<20} ({handedness:<6}) [{constraint_type}]")
        
        print(f"\nExpected Runs: {result['expected runs']}")
        
        # Verify constraints are met
        print("\n" + "-" * 50)
        print("Constraint Verification:")
        _verify_all_constraints_in_lineup(result, json_input)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*80)

    # Test 2: All players unconstrained for comparison
    print("Method 2: All players unconstrained (for comparison)")
    print("-" * 50)
    
    json_input_unconstrained = {}
    player_counter = 10
    
    # Move all players to unconstrained positions
    for pos in range(1, 19):
        if str(pos) in json_input and json_input[str(pos)]:
            json_input_unconstrained[str(player_counter)] = json_input[str(pos)]
            player_counter += 1
    
    # Add constraints
    json_input_unconstrained["max_consecutive_left"] = json_input["max_consecutive_left"]
    json_input_unconstrained["max_consecutive_right"] = json_input["max_consecutive_right"]
    
    try:
        result_unconstrained = parse_and_optimize_lineup_fast(json_input_unconstrained)
        print("✅ Unconstrained optimization successful!")
        print(f"Average runs per game (unconstrained): {result_unconstrained['average runs per game']}")
        print("This may have a different (potentially higher) score since all positions can be optimized.")
        
        print("\nUnconstrained Optimal Order:")
        for pos in range(1, 10):
            player = result_unconstrained[str(pos)]
            handedness = None
            for key, player_data in json_input_unconstrained.items():
                if key.isdigit() and player_data and player_data["name"] == player:
                    handedness = player_data["batting_hand"]
                    break
            print(f"{pos}. {player:<20} ({handedness})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*80)

    # Test 3: JSON string interface
    print("Method 3: JSON string interface")
    print("-" * 50)
    try:
        json_string = json.dumps(json_input)
        result_json = optimize_from_json(json_string)
        print("✅ JSON optimization successful!")
        print("\nResult JSON (first few lines):")
        result_lines = result_json.split('\n')
        for line in result_lines[:10]:
            print(line)
        if len(result_lines) > 10:
            print("  ... (truncated)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*80)
    print("Test completed!")


def _verify_all_constraints_in_lineup(result, json_input):
    """Verify that the optimized lineup meets all constraints."""
    # Verify handedness constraints
    _verify_handedness_constraints_in_lineup(result, json_input)
    
    # Verify positional constraints
    _verify_positional_constraints_in_lineup(result, json_input)


def _verify_handedness_constraints_in_lineup(result, json_input):
    """Verify that the optimized lineup meets the handedness constraints."""
    max_consecutive_left = json_input.get("max_consecutive_left", 0)
    max_consecutive_right = json_input.get("max_consecutive_right", 0)
    
    if max_consecutive_left == 0 and max_consecutive_right == 0:
        print("No handedness constraints to verify.")
        return
    
    # Get handedness for each position
    lineup_handedness = []
    for pos in range(1, 10):
        player = result[str(pos)]
        for key, player_data in json_input.items():
            if key.isdigit() and player_data and player_data["name"] == player:
                lineup_handedness.append(player_data["batting_hand"])
                break
    
    # Check consecutive handedness (including wraparound)
    extended_lineup = lineup_handedness + lineup_handedness
    consecutive_left = 0
    consecutive_right = 0
    max_left_found = 0
    max_right_found = 0
    
    for i in range(18):
        handedness = extended_lineup[i]
        
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
    
    print(f"Max consecutive left-handed batters found: {max_left_found}")
    print(f"Max consecutive right-handed batters found: {max_right_found}")
    
    if max_consecutive_left > 0:
        if max_left_found <= max_consecutive_left:
            print(f"✅ Left-handed constraint satisfied ({max_left_found} ≤ {max_consecutive_left})")
        else:
            print(f"❌ Left-handed constraint violated ({max_left_found} > {max_consecutive_left})")
    
    if max_consecutive_right > 0:
        if max_right_found <= max_consecutive_right:
            print(f"✅ Right-handed constraint satisfied ({max_right_found} ≤ {max_consecutive_right})")
        else:
            print(f"❌ Right-handed constraint violated ({max_right_found} > {max_consecutive_right})")


def _verify_positional_constraints_in_lineup(result, json_input):
    """Verify that constrained players are in their correct positions."""
    print("\nPositional constraint verification:")
    
    # Check each constrained position
    constraints_met = True
    for pos in range(1, 10):
        if str(pos) in json_input and json_input[str(pos)]:
            expected_player = json_input[str(pos)]["name"]
            actual_player = result[str(pos)]
            
            if actual_player == expected_player:
                print(f"  ✅ Position {pos}: {expected_player} (correctly constrained)")
            else:
                print(f"  ❌ Position {pos}: Expected {expected_player}, got {actual_player}")
                constraints_met = False
    
    # Show optimized positions
    optimized_positions = []
    for pos in range(1, 10):
        if str(pos) not in json_input or not json_input[str(pos)]:
            optimized_positions.append(pos)
    
    if optimized_positions:
        print(f"\nOptimized positions: {optimized_positions}")
        for pos in optimized_positions:
            player = result[str(pos)]
            print(f"  Position {pos}: {player} (optimized placement)")
    
    if constraints_met:
        print("✅ All positional constraints satisfied!")
    else:
        print("❌ Some positional constraints violated!")


if __name__ == "__main__":
    main()