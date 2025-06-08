import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@heroui/react";
import { PlayerSeason } from "~/data/types";
import { getPlayerSeasonString } from "~/utils/helper";

type PropType = {
  lineup: Record<number, string | undefined>;
  selectedPlayerSeasons: PlayerSeason[];
  unassignedPlayers: string[]; // array of player names
};

const ConfirmLineup = ({ lineup, selectedPlayerSeasons, unassignedPlayers }: PropType) => {
  const lineupSpots = Array.from({ length: 9 }, (_, i) => i + 1);

  return (
    <div className="space-y-8 w-full">
      <div>
        <h3 className="text-lg font-semibold mb-2">Assigned Players</h3>
        <Table aria-label="Final Lineup Table">
          <TableHeader>
            <TableColumn className="w-10">Batting Spot</TableColumn>
            <TableColumn>Player Name</TableColumn>
          </TableHeader>
          <TableBody>
            {lineupSpots.map((spot) => {
              const playerId = lineup[spot];
              const playerSeason = selectedPlayerSeasons.find(
                (selectedPlayerSeason) => selectedPlayerSeason.compositeId === playerId
              );
              return (
                <TableRow key={spot}>
                  <TableCell className="text-center">{spot}</TableCell>
                  <TableCell>
                    {getPlayerSeasonString(playerSeason)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {unassignedPlayers.length > 0 && (
        <div>
          <h4 className="text-lg font-semibold mb-2">Unassigned Players</h4>
          <Table aria-label="Unassigned Players Table">
            <TableHeader>
              <TableColumn>Player Name</TableColumn>
            </TableHeader>
            <TableBody>
              {unassignedPlayers.map((playerName) => (
                <TableRow key={playerName}>
                  <TableCell>{playerName}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default ConfirmLineup;
