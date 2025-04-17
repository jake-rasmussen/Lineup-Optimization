import { Button, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow } from "@heroui/react";
import { Dispatch, SetStateAction } from "react";
import { formatPosition } from "~/utils/helper";
import PlayerCardModal from "./playerCardModal";
import { PlayerSeason } from "./build/buildController";

type PropType = {
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};

const PlayerTable = ({ selectedPlayerSeasons, setSelectedPlayerSeasons }: PropType) => {
  return (
    <Table aria-label="Selected Players Table">
      <TableHeader>
        <TableColumn>NAME</TableColumn>
        <TableColumn>POSITION</TableColumn>
        <TableColumn>VIEW CARD</TableColumn>
        <TableColumn>REMOVE</TableColumn>
      </TableHeader>
      <TableBody emptyContent={"No players selected."}>
        {selectedPlayerSeasons.map((playerSeason) => (
          <TableRow key={playerSeason.compositeId} >
            <TableCell>{playerSeason.player.firstName} {playerSeason.player.lastName}</TableCell>
            <TableCell>{formatPosition(playerSeason.player.position)}</TableCell>
            <TableCell>
              <PlayerCardModal player={playerSeason.player} />
            </TableCell>
            <TableCell>
              <Button
                isIconOnly
                endContent={<>❌</>}
                variant="light"
                onPress={() =>
                  setSelectedPlayerSeasons((prev) =>
                    prev.filter((p) => p.player.id !== playerSeason.player.id)
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