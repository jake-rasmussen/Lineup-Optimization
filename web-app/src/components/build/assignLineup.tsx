import { Select, SelectItem } from "@heroui/react";
import { Dispatch, SetStateAction } from "react";
import { PlayerSeason } from "./buildController";
import { getTeamName } from "~/utils/helper";

type PropType = {
  lineup: Record<number, string | undefined>;
  setLineup: Dispatch<SetStateAction<Record<number, string | undefined>>>;
  selectedPlayerSeasons: PlayerSeason[];
};

const AssignLineup = ({ lineup, setLineup, selectedPlayerSeasons }: PropType) => {
  const lineupSpots = Array.from({ length: 9 }, (_, i) => i + 1);

  const handleLineupChange = (spot: number, compositeId: string) => {
    setLineup((prev) => {
      const newLineup = { ...prev };
      Object.keys(newLineup).forEach((key) => {
        if (newLineup[Number(key)] === compositeId) {
          delete newLineup[Number(key)];
        }
      });
      newLineup[spot] = compositeId;
      return newLineup;
    });
  };

  return (
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
            const ps = selectedPlayerSeasons.find((item) => item.compositeId === selectedKey?.key);
            return ps
              ? `${ps.player.firstName} ${ps.player.lastName} - ${getTeamName(ps.season.teamId)} ${ps.season.year}`
              : "";
          }}
          size="sm"
        >
          {selectedPlayerSeasons.map((ps) => (
            <SelectItem key={ps.compositeId} value={ps.compositeId}>
              {ps.player.firstName} {ps.player.lastName} - {getTeamName(ps.season.teamId)} {ps.season.year}
            </SelectItem>
          ))}
        </Select>
      ))}
    </div>
  );
};

export default AssignLineup;
