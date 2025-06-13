#!/usr/bin/env python3
"""
test_main.py

Comprehensive testing script for main.py
Tests various scenarios including success and error cases.
"""

import json
import subprocess
import tempfile
import os
from main import optimize_lineup_from_json

def test_1_function_call():
    """Test 1: Direct function call"""
    print("="*60)
    print("TEST 1: Direct Function Call")
    print("="*60)
    
    # Valid test data
    test_data = {
        "1": {
            "name": "Leadoff Hitter",
            "data": {"pa": 600, "h": 180, "2b": 35, "3b": 8, "hr": 15,
                     "sb": 25, "bb": 80, "hbp": 5, "ibb": 2},
            "batting_hand": "LEFT"
        },
        "3": {
            "name": "Cleanup Hitter", 
            "data": {"pa": 650, "h": 195, "2b": 40, "3b": 5, "hr": 35,
                     "sb": 10, "bb": 90, "hbp": 8, "ibb": 15},
            "batting_hand": "RIGHT"
        },
        "11": {
            "name": "Utility Player 1",
            "data": {"pa": 580, "h": 160, "2b": 30, "3b": 4, "hr": 25,
                     "sb": 15, "bb": 70, "hbp": 4, "ibb": 5},
            "batting_hand": "RIGHT"
        },
        "12": {
            "name": "Utility Player 2",
            "data": {"pa": 550, "h": 145, "2b": 25, "3b": 6, "hr": 20,
                     "sb": 8, "bb": 65, "hbp": 3, "ibb": 3},
            "batting_hand": "SWITCH"
        },
        "13": {
            "name": "Utility Player 3",
            "data": {"pa": 520, "h": 135, "2b": 28, "3b": 3, "hr": 18,
                     "sb": 12, "bb": 55, "hbp": 5, "ibb": 2},
            "batting_hand": "LEFT"
        },
        "14": {
            "name": "Utility Player 4",
            "data": {"pa": 490, "h": 120, "2b": 22, "3b": 2, "hr": 12,
                     "sb": 20, "bb": 45, "hbp": 4, "ibb": 1},
            "batting_hand": "RIGHT"
        },
        "15": {
            "name": "Utility Player 5",
            "data": {"pa": 460, "h": 110, "2b": 20, "3b": 1, "hr": 8,
                     "sb": 5, "bb": 40, "hbp": 3, "ibb": 0},
            "batting_hand": "RIGHT"
        },
        "16": {
            "name": "Utility Player 6",
            "data": {"pa": 420, "h": 95, "2b": 15, "3b": 2, "hr": 5,
                     "sb": 10, "bb": 35, "hbp": 2, "ibb": 0},
            "batting_hand": "LEFT"
        },
        "17": {
            "name": "Utility Player 7",
            "data": {"pa": 400, "h": 85, "2b": 12, "3b": 1, "hr": 3,
                     "sb": 8, "bb": 30, "hbp": 1, "ibb": 0},
            "batting_hand": "RIGHT"
        },
        "max_consecutive_left": 2,
        "max_consecutive_right": 3
    }
    
    try:
        json_input = json.dumps(test_data)
        result = optimize_lineup_from_json(json_input)
        
        print("✅ Function call successful!")
        print("Result:")
        print(result)
        
        # Validate output format
        parsed = json.loads(result)
        if validate_output_format(parsed):
            print("✅ Output format is correct!")
        else:
            print("❌ Output format is incorrect!")
            
    except Exception as e:
        print(f"❌ Function call failed: {e}")


def test_2_command_line_with_file():
    """Test 2: Command line with JSON file"""
    print("\n" + "="*60)
    print("TEST 2: Command Line with File")
    print("="*60)
    
    # Create temporary JSON file
    test_data = {
        "11": {"name": "Player 1", "data": {"pa": 500, "h": 125, "2b": 25, "3b": 3, "hr": 15, "sb": 10, "bb": 50, "hbp": 3, "ibb": 1}, "batting_hand": "LEFT"},
        "12": {"name": "Player 2", "data": {"pa": 480, "h": 120, "2b": 20, "3b": 4, "hr": 12, "sb": 8, "bb": 45, "hbp": 2, "ibb": 0}, "batting_hand": "RIGHT"},
        "13": {"name": "Player 3", "data": {"pa": 460, "h": 115, "2b": 22, "3b": 2, "hr": 10, "sb": 15, "bb": 40, "hbp": 4, "ibb": 1}, "batting_hand": "SWITCH"},
        "14": {"name": "Player 4", "data": {"pa": 440, "h": 110, "2b": 18, "3b": 1, "hr": 8, "sb": 5, "bb": 35, "hbp": 2, "ibb": 0}, "batting_hand": "RIGHT"},
        "15": {"name": "Player 5", "data": {"pa": 420, "h": 105, "2b": 15, "3b": 3, "hr": 6, "sb": 12, "bb": 30, "hbp": 1, "ibb": 0}, "batting_hand": "LEFT"},
        "16": {"name": "Player 6", "data": {"pa": 400, "h": 100, "2b": 12, "3b": 2, "hr": 4, "sb": 8, "bb": 25, "hbp": 3, "ibb": 0}, "batting_hand": "RIGHT"},
        "17": {"name": "Player 7", "data": {"pa": 380, "h": 95, "2b": 10, "3b": 1, "hr": 2, "sb": 6, "bb": 20, "hbp": 1, "ibb": 0}, "batting_hand": "RIGHT"},
        "18": {"name": "Player 8", "data": {"pa": 360, "h": 90, "2b": 8, "3b": 0, "hr": 1, "sb": 4, "bb": 15, "hbp": 2, "ibb": 0}, "batting_hand": "LEFT"},
        "1": {"name": "Fixed Player", "data": {"pa": 600, "h": 180, "2b": 35, "3b": 8, "hr": 25, "sb": 20, "bb": 75, "hbp": 5, "ibb": 5}, "batting_hand": "RIGHT"},
        "max_consecutive_left": 2,
        "max_consecutive_right": 3
    }
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, indent=2)
            temp_filename = f.name
        
        print(f"Created temporary file: {temp_filename}")
        
        # Run main.py with the file
        result = subprocess.run(['python', 'main.py', temp_filename], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Command line execution successful!")
            print("Result:")
            print(result.stdout)
            
            # Validate output
            try:
                parsed = json.loads(result.stdout)
                if validate_output_format(parsed):
                    print("✅ Output format is correct!")
                else:
                    print("❌ Output format is incorrect!")
            except:
                print("❌ Output is not valid JSON!")
        else:
            print("❌ Command line execution failed!")
            print("Error:", result.stderr)
            
        # Clean up
        os.unlink(temp_filename)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_3_stdin_pipe():
    """Test 3: Stdin pipe"""
    print("\n" + "="*60)
    print("TEST 3: Stdin Pipe")
    print("="*60)
    
    test_data = {
        "11": {"name": "A", "data": {"pa": 400, "h": 100, "2b": 20, "3b": 2, "hr": 10, "sb": 5, "bb": 40, "hbp": 2, "ibb": 1}, "batting_hand": "LEFT"},
        "12": {"name": "B", "data": {"pa": 420, "h": 105, "2b": 21, "3b": 3, "hr": 12, "sb": 6, "bb": 42, "hbp": 3, "ibb": 0}, "batting_hand": "RIGHT"},
        "13": {"name": "C", "data": {"pa": 440, "h": 110, "2b": 22, "3b": 1, "hr": 14, "sb": 7, "bb": 44, "hbp": 1, "ibb": 2}, "batting_hand": "SWITCH"},
        "14": {"name": "D", "data": {"pa": 460, "h": 115, "2b": 23, "3b": 4, "hr": 16, "sb": 8, "bb": 46, "hbp": 4, "ibb": 1}, "batting_hand": "RIGHT"},
        "15": {"name": "E", "data": {"pa": 480, "h": 120, "2b": 24, "3b": 2, "hr": 18, "sb": 9, "bb": 48, "hbp": 2, "ibb": 3}, "batting_hand": "LEFT"},
        "16": {"name": "F", "data": {"pa": 500, "h": 125, "2b": 25, "3b": 5, "hr": 20, "sb": 10, "bb": 50, "hbp": 5, "ibb": 0}, "batting_hand": "RIGHT"},
        "17": {"name": "G", "data": {"pa": 380, "h": 95, "2b": 19, "3b": 1, "hr": 8, "sb": 4, "bb": 38, "hbp": 1, "ibb": 1}, "batting_hand": "RIGHT"},
        "18": {"name": "H", "data": {"pa": 360, "h": 90, "2b": 18, "3b": 0, "hr": 6, "sb": 3, "bb": 36, "hbp": 0, "ibb": 0}, "batting_hand": "LEFT"},
        "1": {"name": "I", "data": {"pa": 600, "h": 150, "2b": 30, "3b": 6, "hr": 25, "sb": 15, "bb": 60, "hbp": 6, "ibb": 4}, "batting_hand": "RIGHT"}
    }
    
    try:
        json_input = json.dumps(test_data)
        
        # Run main.py with stdin
        result = subprocess.run(['python', 'main.py'], 
                              input=json_input, 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Stdin execution successful!")
            print("Result:")
            print(result.stdout)
            
            # Validate output
            try:
                parsed = json.loads(result.stdout)
                if validate_output_format(parsed):
                    print("✅ Output format is correct!")
                else:
                    print("❌ Output format is incorrect!")
            except:
                print("❌ Output is not valid JSON!")
        else:
            print("❌ Stdin execution failed!")
            print("Error:", result.stderr)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_4_error_cases():
    """Test 4: Error handling"""
    print("\n" + "="*60)
    print("TEST 4: Error Cases")
    print("="*60)
    
    # Test case 1: Invalid JSON
    print("\n--- Test 4a: Invalid JSON ---")
    try:
        result = optimize_lineup_from_json('{"invalid": json}')
        parsed = json.loads(result)
        if "error" in parsed:
            print("✅ Invalid JSON properly handled")
            print(f"Error: {parsed['error']}")
        else:
            print("❌ Invalid JSON not properly handled")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test case 2: Wrong number of players
    print("\n--- Test 4b: Wrong number of players ---")
    try:
        wrong_data = {
            "11": {"name": "Player 1", "data": {"pa": 400, "h": 100, "2b": 20, "3b": 2, "hr": 10, "sb": 5, "bb": 40, "hbp": 2, "ibb": 1}, "batting_hand": "LEFT"},
            "12": {"name": "Player 2", "data": {"pa": 420, "h": 105, "2b": 21, "3b": 3, "hr": 12, "sb": 6, "bb": 42, "hbp": 3, "ibb": 0}, "batting_hand": "RIGHT"}
            # Only 2 players - should fail
        }
        result = optimize_lineup_from_json(json.dumps(wrong_data))
        parsed = json.loads(result)
        if "error" in parsed:
            print("✅ Wrong player count properly handled")
            print(f"Error: {parsed['error']}")
        else:
            print("❌ Wrong player count not properly handled")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test case 3: Invalid handedness
    print("\n--- Test 4c: Invalid handedness ---")
    try:
        invalid_hand_data = {
            "11": {"name": "Player 1", "data": {"pa": 400, "h": 100, "2b": 20, "3b": 2, "hr": 10, "sb": 5, "bb": 40, "hbp": 2, "ibb": 1}, "batting_hand": "INVALID"},
        }
        # Add 8 more valid players to make 9 total
        for i in range(2, 10):
            invalid_hand_data[str(10+i)] = {
                "name": f"Player {i}", 
                "data": {"pa": 400, "h": 100, "2b": 20, "3b": 2, "hr": 10, "sb": 5, "bb": 40, "hbp": 2, "ibb": 1}, 
                "batting_hand": "RIGHT"
            }
        
        result = optimize_lineup_from_json(json.dumps(invalid_hand_data))
        parsed = json.loads(result)
        if "error" in parsed:
            print("✅ Invalid handedness properly handled")
            print(f"Error: {parsed['error']}")
        else:
            print("❌ Invalid handedness not properly handled")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def validate_output_format(parsed_result):
    """Validate that the output has the correct format"""
    try:
        # Check that positions 1-9 exist and have string values
        for i in range(1, 10):
            if str(i) not in parsed_result:
                print(f"❌ Missing position {i}")
                return False
            if not isinstance(parsed_result[str(i)], str):
                print(f"❌ Position {i} is not a string")
                return False
        
        # Check that "average runs per game" exists and is a number
        if "average runs per game" not in parsed_result:
            print("❌ Missing 'average runs per game'")
            return False
        
        if not isinstance(parsed_result["average runs per game"], (int, float)):
            print("❌ 'average runs per game' is not a number")
            return False
        
        # Check that there are no extra fields (except error/status in error cases)
        expected_keys = {str(i) for i in range(1, 10)} | {"average runs per game"}
        actual_keys = set(parsed_result.keys())
        extra_keys = actual_keys - expected_keys - {"error", "status"}
        
        if extra_keys:
            print(f"❌ Unexpected extra keys: {extra_keys}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def main():
    """Run all tests"""
    print("TESTING main.py")
    print("This will test the main entry point for the lineup optimizer\n")
    
    test_1_function_call()
    test_2_command_line_with_file()
    test_3_stdin_pipe()
    test_4_error_cases()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()