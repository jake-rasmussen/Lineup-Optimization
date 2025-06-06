"""
Test script for the lineup optimizer using sample Dodgers data.
"""
import json
from lineup_optimizer import parse_and_optimize_lineup_fast, optimize_from_json

def main():
    """
    Test the lineup optimizer with sample Dodgers player data.
    """
    # Test JSON data with Dodgers players
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
        }
    }

    print("="*60)
    print("LINEUP OPTIMIZER TEST")
    print("="*60)
    print(f"Testing with {len([k for k in json_input.keys() if k.isdigit()])} Dodgers players")
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
            print(f"{pos}. {player}")
        print(f"\nExpected Runs: {result['expected runs']}")
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
    print("Test completed!")

if __name__ == "__main__":
    main()