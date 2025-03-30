import { Button, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow } from "@heroui/react";
import { Player } from "@prisma/client";
import { Dispatch, SetStateAction } from "react";
import { formatPosition } from "~/utils/helper";
import PlayerCardModal from "./playerCardModal";

type PropType = {
  selectedPlayers: Player[];
  setSelectedPlayers: Dispatch<SetStateAction<Player[]>>;
};

const PlayerTable = ({ selectedPlayers, setSelectedPlayers }: PropType) => {
  return (
    <Table aria-label="Example static collection table">
      <TableHeader>
        <TableColumn>NAME</TableColumn>
        <TableColumn>POSITION</TableColumn>
        <TableColumn>VIEW CARD</TableColumn>
        <TableColumn>REMOVE</TableColumn>
      </TableHeader>
      <TableBody>
        {selectedPlayers.map((player) => (
          <TableRow key="1">
            <TableCell>{player.firstName} {player.lastName}</TableCell>
            <TableCell>{formatPosition(player.position)}</TableCell>
            <TableCell>
              <PlayerCardModal player={player} />
            </TableCell>
            <TableCell>
              <Button
                isIconOnly
                endContent={<>❌</>}
                variant="light"
                onPress={() =>
                  setSelectedPlayers((prev) =>
                    prev.filter((p) => p.id !== player.id)
                  )
                }
              />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default PlayerTable;