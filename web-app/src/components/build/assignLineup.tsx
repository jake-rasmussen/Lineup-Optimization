import { Divider, NumberInput, Select, SelectItem } from "@heroui/react";
import { Dispatch, SetStateAction } from "react";
import { PlayerSeason } from "~/data/types";
import { getPlayerSeasonString } from "~/utils/helper";

type PropType = {
  lineup: Record<number, string | undefined>;
  setLineup: Dispatch<SetStateAction<Record<number, string | undefined>>>;
  maxConsecutiveHandedness: number[];
  setMaxConsecutiveHandedness: Dispatch<SetStateAction<[number, number]>>;
  selectedPlayerSeasons: PlayerSeason[];
};

const AssignLineup = ({ lineup, setLineup, maxConsecutiveHandedness, setMaxConsecutiveHandedness, selectedPlayerSeasons }: PropType) => {
  const lineupSpots = Array.from({ length: 9 }, (_, i) => i + 1);

  const handleLineupChange = (spot: number, compositeId: string) => {
    setLineup((prev) => {
      const newLineup = { ...prev };

      Object.entries(newLineup).forEach(([k, v]) => {
        if (v === compositeId) {
          newLineup[Number(k)] = undefined;
        }
      });

      newLineup[spot] = compositeId;
      return newLineup;
    });
  };

  return (
    <div className="flex flex-col gap-8 w-full">
      <div className="flex flex-col gap-4">
        {lineupSpots.map((spot) => (
          <Select
            key={spot}
            label={`Batting Spot ${spot}`}
            selectionMode="single"
            selectedKeys={lineup[spot] ? new Set([lineup[spot]]) : new Set()}
            onSelectionChange={(selected) =>
              handleLineupChange(spot, selected.currentKey as string)
            }
            renderValue={(selectedKeys) => {
              const selectedKey = Array.from(selectedKeys)[0];
              const playerSeason = selectedPlayerSeasons.find((selectedPlayerSeason) => selectedPlayerSeason.compositeId === selectedKey?.key);

              if (playerSeason) {
                return getPlayerSeasonString(playerSeason);
              } else {
                return "-";
              }
            }}
            size="sm"
          >
            {selectedPlayerSeasons.map((playerSeason) => (
              <SelectItem key={playerSeason.compositeId}>
                {getPlayerSeasonString(playerSeason)}
              </SelectItem>
            ))}
          </Select>
        ))}
      </div>
      {/* <Divider />
      <div className="flex flex-col gap-2">
        <div className="flex flex-row gap-4">
          <NumberInput
            label="Enter max amount of consecutive lefties"
            minValue={1}
            maxValue={9}
            onValueChange={(e) => setMaxConsecutiveHandedness([e, maxConsecutiveHandedness[1]!])}
          />
          <NumberInput
            label="Enter max amount of consecutive righties"
            minValue={1}
            maxValue={9}
            onValueChange={(e) => setMaxConsecutiveHandedness([maxConsecutiveHandedness[0]!, e])}
          />
        </div>
        <p className="text-sm text-gray-500">No constraints will be added if no number is selected</p>
      </div> */}
    </div>
  );
};

export default AssignLineup;