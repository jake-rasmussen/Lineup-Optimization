import { Table, TableBody, TableCell, TableColumn, TableHeader, TableRow, Tooltip } from "@heroui/react";
import { DisplayLineupPlayer } from "~/data/types";

type PropType = {
  lineup: Record<number, DisplayLineupPlayer>;
};

const ResultsTable = ({ lineup }: PropType) => {
  const renderPlayerDesignation = (displayPlayer: DisplayLineupPlayer) => {
    if (displayPlayer.isSelected) {
      return (
        <Tooltip content="Player assigned to lineup position" placement="right">
          🔒
        </Tooltip>
      );
    }
    if (displayPlayer.isUnassigned) {
      return (
        <Tooltip content="Player unassigned to lineup position" placement="right">
          🔓
        </Tooltip>
      );
    }
    return <p>-</p>;
  };

  return (
    <Table aria-label="Final Lineup Table" className="max-w-xl">
      <TableHeader>
        <TableColumn>SPOT</TableColumn>
        <TableColumn>NAME</TableColumn>
        <TableColumn>DESIGNATION</TableColumn>
      </TableHeader>
      <TableBody>
        {Object.entries(lineup).map(([spot, displayPlayer]) => (
          <TableRow key={spot}>
            <TableCell>{spot}</TableCell>
            <TableCell className={displayPlayer.isSelected || displayPlayer.isUnassigned ? "font-black" : ""}>{`${displayPlayer.playerSeason.player.fullName}`}</TableCell>
            <TableCell>
              <div className="w-fit hover:cursor-pointer">
                {renderPlayerDesignation(displayPlayer)}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default ResultsTable;
