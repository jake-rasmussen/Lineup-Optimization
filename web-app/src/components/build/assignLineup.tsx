import { Select, SelectItem } from "@heroui/react";
import { Player } from "@prisma/client";
import { Dispatch, SetStateAction } from "react";

type PropType = {
  lineup: Record<number, string | undefined>;
  setLineup: Dispatch<SetStateAction<Record<number, string | undefined>>>;
  selectedPlayers: Player[];
}

const AssignLineup = ({ lineup, setLineup, selectedPlayers }: PropType) => {
  const lineupSpots = Array.from({ length: 9 }, (_, i) => i + 1);

  const handleLineupChange = (spot: number, playerId: string) => {
    setLineup((prev) => {
      const newLineup = { ...prev };
      Object.keys(newLineup).forEach((key) => {
        if (newLineup[Number(key)] === playerId) {
          delete newLineup[Number(key)];
        }
      });
      newLineup[spot] = playerId;
      return newLineup;
    });
  };

  return (
    <>
      <div className="flex flex-col gap-4">
        {lineupSpots.map((spot) => (
          <Select
            key={spot}
            label={`Batting Spot ${spot}`}
            // placeholder="Assign player"
            selectionMode="single"
            selectedKeys={lineup[spot] ? new Set([lineup[spot]]) : new Set()}
            onSelectionChange={(selected) =>
              handleLineupChange(spot, selected.currentKey as string)
            }
            renderValue={(selectedKeys) => {
              const selectedKey = Array.from(selectedKeys)[0];
              const player = selectedPlayers.find((p) => p.id === selectedKey?.key);
              return player ? `${player.firstName} ${player.lastName}` : "";
            }}
            size="sm"
          >
            {selectedPlayers.map((player) => (
              <SelectItem key={player.id} value={player.id}>
                {player.firstName} {player.lastName}
              </SelectItem>
            ))}
          </Select>
        ))}
      </div>
    </>
  )
}

export default AssignLineup;