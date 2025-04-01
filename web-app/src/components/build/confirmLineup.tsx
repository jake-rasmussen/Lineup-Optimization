import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@heroui/react";
import { PlayerSeason } from "./buildController";
import { getTeamName } from "~/utils/helper";

type PropType = {
  lineup: Record<number, string | undefined>;
  selectedPlayerSeasons: PlayerSeason[];
  unassignedPlayers: string[];
};

const ConfirmLineup = ({ lineup, selectedPlayerSeasons, unassignedPlayers }: PropType) => {
  const lineupSpots = Array.from({ length: 9 }, (_, i) => i + 1);

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Final Lineup</h3>
        <Table aria-label="Final Lineup Table">
          <TableHeader>
            <TableColumn className="w-10">Batting Spot</TableColumn>
            <TableColumn>Player Name</TableColumn>
          </TableHeader>
          <TableBody>
            {lineupSpots.map((spot) => {
              const compositeId = lineup[spot];
              const ps = selectedPlayerSeasons.find((item) => item.compositeId === compositeId);
              return (
                <TableRow key={spot}>
                  <TableCell className="text-center">{spot}</TableCell>
                  <TableCell>
                    {ps
                      ? `${ps.player.firstName} ${ps.player.lastName} - ${getTeamName(ps.season.teamId)} ${ps.season.year}`
                      : "-"}
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
              {unassignedPlayers.map((compositeId) => {
                const ps = selectedPlayerSeasons.find((item) => item.compositeId === compositeId);
                return (
                  <TableRow key={compositeId}>
                    <TableCell>
                      {ps
                        ? `${ps.player.firstName} ${ps.player.lastName} - ${getTeamName(ps.season.teamId)} ${ps.season.year}`
                        : "Unknown Player"}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default ConfirmLineup;
