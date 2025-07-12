"use client";

import {
  Button, Table, TableBody, TableCell, TableColumn,
  TableHeader, TableRow
} from "@heroui/react";
import { Dispatch, SetStateAction } from "react";
import { formatPosition, getPlayerSeasonString } from "~/utils/helper";
import { PlayerSeason, Season } from "~/data/types";
import PlayerSeasonDropdown from "../playerSeasonDropdown";

type PropType = {
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};

const PlayerTableALPB = ({ selectedPlayerSeasons, setSelectedPlayerSeasons }: PropType) => {
  return (
    <Table aria-label="Selected Players Table">
      <TableHeader>
        <TableColumn>NAME</TableColumn>
        <TableColumn>POSITION</TableColumn>
        <TableColumn>VIEW STATS</TableColumn>
        <TableColumn>REMOVE</TableColumn>
      </TableHeader>
      <TableBody emptyContent={"No players selected."}>
        {selectedPlayerSeasons.map((playerSeason) => (
          <TableRow key={playerSeason.compositeId}>
            <TableCell>
              {getPlayerSeasonString(playerSeason)}
            </TableCell>
            <TableCell>
              {formatPosition(playerSeason.player.position)}
            </TableCell>
            <TableCell>
              <PlayerSeasonDropdown season={playerSeason.season as Season} />
            </TableCell>
            <TableCell>
              <Button
                isIconOnly
                endContent={<>❌</>}
                variant="light"
                size="sm"
                onPress={() => {
                  setSelectedPlayerSeasons((prev) =>
                    prev.filter((p) => p.player.id !== playerSeason.player.id)
                  );
                }}
              />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default PlayerTableALPB;
