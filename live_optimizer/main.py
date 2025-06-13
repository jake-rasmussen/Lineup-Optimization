#!/usr/bin/env python3
"""
main.py

Main entry point for the Baseball Lineup Optimizer
This file should be called from the frontend with JSON input.
"""

import json
import sys
from typing import Dict, Any
from lineup_optimizer import parse_and_optimize_lineup_fast, parse_json_input


def optimize_lineup_from_json(json_input: str) -> str:
    """
    Main entry point for optimizing lineup from JSON input.
    
    Args:
        json_input: JSON string containing player data and constraints
        
    Returns:
        JSON string with optimized lineup in the format:
        {
            "1": "player_name",
            "2": "player_name", 
            ...
            "9": "player_name",
            "average runs per game": float
        }
    """
    try:
        # Parse and validate input
        parsed_data = parse_json_input(json_input)
        
        # Run optimization
        result = parse_and_optimize_lineup_fast(parsed_data)
        
        # Convert to required output format
        output = {}
        for i in range(1, 10):
            output[str(i)] = result[str(i)]
        
        # Change "expected runs" to "average runs per game"
        output["average runs per game"] = result["expected runs"]
        
        return json.dumps(output, indent=2)
        
    except Exception as e:
        # Return error in JSON format
        error_response = {
            "error": str(e),
            "status": "failed"
        }
        return json.dumps(error_response, indent=2)


def main():
    """
    Main function for command line usage or direct execution.
    Reads JSON from stdin or file and outputs optimized lineup.
    """
    if len(sys.argv) > 1:
        # Read from file if filename provided
        try:
            with open(sys.argv[1], 'r') as f:
                json_input = f.read()
        except FileNotFoundError:
            print(json.dumps({"error": f"File not found: {sys.argv[1]}", "status": "failed"}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": f"Error reading file: {str(e)}", "status": "failed"}))
            sys.exit(1)
    else:
        # Read from stdin
        try:
            json_input = sys.stdin.read()
        except Exception as e:
            print(json.dumps({"error": f"Error reading from stdin: {str(e)}", "status": "failed"}))
            sys.exit(1)
    
    # Process the input and output result
    result = optimize_lineup_from_json(json_input)
    print(result)


if __name__ == "__main__":
    main()