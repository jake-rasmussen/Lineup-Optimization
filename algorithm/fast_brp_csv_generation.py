"""
FAST BDNRP CSV GENERATOR
Removes optimization routine: only generates `bdnrp_values.csv`.
Speeds up COM calls by:
  - Disabling automatic recalculation (manual mode via constant value)
  - Manually invoking `sheet.Calculate()` instead of sleeps
  - Bulk-building a list of tuples then dumping via pandas
"""
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from win32com.client import Dispatch, constants


def setup_excel(file_path: str) -> Any:
    """Open Excel workbook in manual calculation mode and return Excel objects."""
    print(f"[setup_excel] Opening Excel: {file_path}")
    excel = Dispatch('Excel.Application')
    excel.Visible = False
    excel.DisplayAlerts = False
    # Attempt to set manual calculation mode
    try:
        excel.Calculation = constants.xlCalculationManual
        print("[setup_excel] Calculation mode set to manual")
    except Exception as e:
        print(f"[setup_excel] Warning: could not set manual calculation mode: {e}")
    # Open workbook and sheet
    workbook = excel.Workbooks.Open(file_path)
    sheet = workbook.Sheets("4 Tuple Values 0 Outs")
    print(f"[setup_excel] Workbook opened; using sheet: {sheet.Name}")
    return excel, workbook, sheet


def generate_bdnrp_csv(players: List[str],
                       player_stats: Dict[str, Dict[str, int]],
                       excel_file_path: str,
                       output_csv: str = "bdnrp_values.csv") -> None:
    """
    Generate BDNRP for all distinct 4-tuples and save to CSV.
    """
    print(f"[generate_bdnrp_csv] Starting CSV generation for {len(players)} players")
    excel, workbook, sheet = setup_excel(excel_file_path)
    try:
        rows: List[Dict[str, Any]] = []
        print("[generate_bdnrp_csv] Computing 4-tuple combinations...")
        combos = [
            (p1, p2, p3, p4)
            for p1 in players
            for p2 in players
            for p3 in players
            for p4 in players
            if len({p1, p2, p3, p4}) == 4
        ]
        total = len(combos)
        print(f"[generate_bdnrp_csv] Total combinations: {total}")

        for idx_combo, (p1, p2, p3, p4) in enumerate(combos, start=1):
            for idx_player, player in enumerate((p1, p2, p3, p4)):
                stats = player_stats[player]
                base_row = 4 + idx_player * 7  # rows 4,11,18,27
                sheet.Range(f"D{base_row}").Value = player
                sheet.Range(f"H{base_row}").Value = stats["pa"]
                sheet.Range(f"K{base_row}").Value = stats["h"]
                sheet.Range(f"L{base_row}").Value = stats["2b"]
                sheet.Range(f"M{base_row}").Value = stats["3b"]
                sheet.Range(f"N{base_row}").Value = stats["hr"]
                sheet.Range(f"P{base_row}").Value = stats["sb"]
                sheet.Range(f"R{base_row}").Value = stats["bb"]
                sheet.Range(f"AA{base_row}").Value = stats["hbp"]
                sheet.Range(f"AD{base_row}").Value = stats["ibb"]

            # single manual recalc
            sheet.Calculate()
            bdnrp_value = sheet.Range("H103").Value
            rows.append({
                "player1": p1,
                "player2": p2,
                "player3": p3,
                "player4": p4,
                "bdnrp_value": bdnrp_value,
            })

            if idx_combo % 1000 == 0 or idx_combo == total:
                print(f"[generate_bdnrp_csv] Processed {idx_combo}/{total} combos")

        print("[generate_bdnrp_csv] All combinations processed; writing to CSV...")
        df = pd.DataFrame(rows)
        df.to_csv(output_csv, index=False)
        print(f"[generate_bdnrp_csv] BDNRP CSV generated: {output_csv}")

    finally:
        workbook.Close(SaveChanges=False)
        excel.Quit()
        print("[generate_bdnrp_csv] Excel closed")


if __name__ == "__main__":
    print("[main] FAST BDNRP CSV GENERATOR starting...")
    # Inline JSON input of players 10–18
    player_block = {
        "1": {"name": "", "data": None},
        "2": {"name": "", "data": None},
        "3": {"name": "", "data": None},
        "4": {"name": "", "data": None},
        "5": {"name": "", "data": None},
        "6": {"name": "", "data": None},
        "7": {"name": "", "data": None},
        "8": {"name": "", "data": None},
        "9": {"name": "", "data": None},
        "10": {"name": "Colton Cowser",    "data": {"pa":656,"h":130,"2b":26,"3b":3,"hr":25,"sb":0,"bb":66,"hbp":10,"ibb":2}},
        "11": {"name": "Adley Rutschman",  "data": {"pa":1910,"h":429,"2b":89,"3b":3,"hr":56,"sb":0,"bb":231,"hbp":8,"ibb":9}},
        "12": {"name": "Ryan O'Hearn",     "data": {"pa":2015,"h":448,"2b":86,"3b":9,"hr":72,"sb":0,"bb":168,"hbp":12,"ibb":7}},
        "13": {"name": "Ryan Mountcastle", "data": {"pa":2412,"h":577,"2b":111,"3b":5,"hr":93,"sb":0,"bb":164,"hbp":14,"ibb":4}},
        "14": {"name": "Boyce Mullins",    "data": {"pa":2838,"h":641,"2b":126,"3b":20,"hr":92,"sb":0,"bb":239,"hbp":31,"ibb":6}},
        "15": {"name": "Ramón Urías",      "data": {"pa":1547,"h":367,"2b":66,"3b":6,"hr":41,"sb":0,"bb":118,"hbp":24,"ibb":1}},
        "16": {"name": "Gunnar Henderson", "data": {"pa":1570,"h":371,"2b":73,"3b":18,"hr":72,"sb":0,"bb":155,"hbp":10,"ibb":4}},
        "17": {"name": "Tyler O'Neill",    "data": {"pa":2183,"h":476,"2b":88,"3b":4,"hr":111,"sb":0,"bb":194,"hbp":31,"ibb":5}},
        "18": {"name": "Jackson Holliday", "data": {"pa":298,"h":56,"2b":5,"3b":3,"hr":7,"sb":0,"bb":22,"hbp":4,"ibb":0}}
    }

    players: List[str] = []
    player_stats: Dict[str, Dict[str, int]] = {}
    for key in map(str, range(10, 19)):
        entry = player_block[key]
        if entry['name'] and entry['data']:
            players.append(entry['name'])
            player_stats[entry['name']] = entry['data']
    print(f"[main] Players: {players}")

    # Use a raw string literal to avoid unicode escapes
    excel_path = r"C:\Users\buman\OneDrive\Desktop\Lineup_Optimization\Copy_Of_Lineup_Optimization.xlsx"
    print(f"[main] Excel path: {excel_path}")

    generate_bdnrp_csv(players, player_stats, excel_path)
