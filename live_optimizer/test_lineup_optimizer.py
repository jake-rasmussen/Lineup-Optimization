"""
test_lineup_optimizer.py

Test script for the lineup optimizer using sample Dodgers data with handedness constraints.
"""
import json
from lineup_optimizer import parse_and_optimize_lineup_fast, optimize_from_json

def main():
    """
    Test the lineup optimizer with sample Dodgers player data and handedness constraints.
    """
    # Test JSON data with Dodgers players and handedness constraints
    json_input = {
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
            "name": "Shohei Ohtani",
            "data": {"pa": 3842, "h": 939, "2b": 176, "3b": 40, "hr": 243,
                     "sb": 0, "bb": 464, "hbp": 22, "ibb": 74},
            "batting_hand": "LEFT"
        },
        "13": { 
            "name": "Markus Betts",
            "data": {"pa": 6493, "h": 1665, "2b": 376, "3b": 40, "hr": 279,
                     "sb": 0, "bb": 699, "hbp": 50, "ibb": 33},
            "batting_hand": "RIGHT"
        },
        "14": { 
            "name": "Enrique Hernandez",
            "data": {"pa": 4014, "h": 854, "2b": 194, "3b": 15, "hr": 127,
                     "sb": 0, "bb": 351, "hbp": 27, "ibb": 12},
            "batting_hand": "RIGHT"
        },
        "15": { 
            "name": "Frederick Freeman",
            "data": {"pa": 8914, "h": 2322, "2b": 522, "3b": 32, "hr": 352,
                     "sb": 0, "bb": 1029, "hbp": 109, "ibb": 139},
            "batting_hand": "LEFT"
        },
        "16": { 
            "name": "Dalton Rushing",
            "data": {"pa": 17, "h": 4, "2b": 1, "3b": 0, "hr": 0,
                     "sb": 0, "bb": 1, "hbp": 0, "ibb": 0},
            "batting_hand": "LEFT"
        },
        "17": { 
            "name": "Miguel Rojas",
            "data": {"pa": 3922, "h": 931, "2b": 179, "3b": 11, "hr": 51,
                     "sb": 0, "bb": 246, "hbp": 42, "ibb": 16},
            "batting_hand": "RIGHT"
        },
        "18": { 
            "name": "Thomas Edman",
            "data": {"pa": 2725, "h": 654, "2b": 131, "3b": 21, "hr": 67,
                     "sb": 0, "bb": 169, "hbp": 34, "ibb": 4},
            "batting_hand": "SWITCH"
        },
        # Handedness constraints
        "max_consecutive_left": 2,   # No more than 2 consecutive left-handed batters
        "max_consecutive_right": 3   # No more than 3 consecutive right-handed batters
    }

    print("="*60)
    print("LINEUP OPTIMIZER TEST WITH HANDEDNESS CONSTRAINTS")
    print("="*60)
    print(f"Testing with {len([k for k in json_input.keys() if k.isdigit()])} Dodgers players")
    print(f"Constraints: Max {json_input['max_consecutive_left']} consecutive lefties, Max {json_input['max_consecutive_right']} consecutive righties")
    print()

    # Method 1: Using the direct function
    print("Method 1: Direct function call")
    print("-" * 30)
    try:
        result = parse_and_optimize_lineup_fast(json_input)
        print("✅ Optimization successful!")
        print("\nOptimal Batting Order:")
        for pos in range(1, 10):
            player = result[str(pos)]
            handedness = None
            # Find handedness for display
            for key, player_data in json_input.items():
                if key.isdigit() and player_data and player_data["name"] == player:
                    handedness = player_data["batting_hand"]
                    break
            print(f"{pos}. {player} ({handedness})")
        print(f"\nExpected Runs: {result['expected runs']}")
        
        # Verify constraints are met
        print("\n" + "-" * 30)
        print("Constraint Verification:")
        _verify_constraints_in_lineup(result, json_input)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*60)

    # Method 2: Using JSON string interface
    print("Method 2: JSON string interface")
    print("-" * 30)
    try:
        json_string = json.dumps(json_input)
        result_json = optimize_from_json(json_string)
        print("✅ JSON optimization successful!")
        print("\nResult JSON:")
        print(result_json)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    
    # Test 3: Test with no constraints (set both to 0)
    print("Method 3: Test with no handedness constraints")
    print("-" * 30)
    json_input_no_constraints = json_input.copy()
    json_input_no_constraints["max_consecutive_left"] = 0
    json_input_no_constraints["max_consecutive_right"] = 0
    
    try:
        result_no_constraints = parse_and_optimize_lineup_fast(json_input_no_constraints)
        print("✅ No constraints optimization successful!")
        print(f"Expected Runs (no constraints): {result_no_constraints['expected runs']}")
        print("This should potentially have a higher score since there are no constraints.")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*60)
    print("Test completed!")


def _verify_constraints_in_lineup(result, json_input):
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


if __name__ == "__main__":
    main()