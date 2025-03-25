import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@heroui/react";
import { Player } from "@prisma/client";

type PropType = {
  lineup: Record<number, string | undefined>;
  selectedPlayers: Player[];
  unassignedPlayers: string[];
};

const ConfirmLineup = ({ lineup, selectedPlayers, unassignedPlayers }: PropType) => {
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
              const player = selectedPlayers.find((p) => p.id === lineup[spot]);
              return (
                <TableRow key={spot}>
                  <TableCell className="text-center">{spot}</TableCell>
                  <TableCell>{player ? `${player.firstName} ${player.lastName}` : "-"}</TableCell>
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
              {unassignedPlayers.map((playerId) => {
                const player = selectedPlayers.find((p) => p.id === playerId);
                return (
                  <TableRow key={playerId}>
                    <TableCell>{player ? `${player.firstName} ${player.lastName}` : "Unknown Player"}</TableCell>
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
