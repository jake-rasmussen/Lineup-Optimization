"use client";

import { Dispatch, SetStateAction, useState } from "react";
import {
  Button,
  Input,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Accordion,
  AccordionItem,
  Spinner,
} from "@heroui/react";
import { api } from "~/utils/api";
import { Player, Position, Season } from "@prisma/client";
import { PlayerSeason } from "~/data/types";

type PropType = {
  setUnsavedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};

export default function SearchMLBPlayers({ setUnsavedPlayerSeasons }: PropType) {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [fetchedPlayerSeasons, setFetchedPlayerSeasons] = useState<PlayerSeason[]>([]);

  const { mutateAsync: searchPlayerByName } = api.mlb.searchPlayerByName.useMutation();
  const { mutateAsync: getPlayerStats } = api.mlb.getPlayerStats.useMutation();

  const onSearch = async () => {
    setIsLoading(true);
    setFetchedPlayerSeasons([]);

    try {
      const players = await searchPlayerByName(query) as Player[];
      const hitters = players.filter((player: Player) => player.position !== Position.PITCHER);

      const results: PlayerSeason[] = [];

      for (const player of hitters) {
        const seasons = await getPlayerStats({
          playerId: player.id,
        }) as Season[];

        const playerSeasons = seasons.map((season) => ({
          compositeId: `${player.id}_${season.id}_${season.teamName}`,
          player,
          season,
        }));

        results.push(...playerSeasons);
      }

      setFetchedPlayerSeasons(results);
    } catch (e) {
      console.error(e);
      setFetchedPlayerSeasons([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Search MLB Player"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button onPress={onSearch} disabled={isLoading}>
          Search
        </Button>
      </div>

      <div className="space-y-6 overflow-y-scroll max-h-[50vh] flex flex-col items-center">
        {
          isLoading ? (
            <Spinner label="Searching players..." />
          ) : (
            <></>
          )
        }

        <Accordion>
          {Array.from(
            fetchedPlayerSeasons.reduce((acc, ps) => {
              if (!acc.has(ps.player.id)) {
                acc.set(ps.player.id, {
                  player: ps.player,
                  seasons: [],
                });
              }
              acc.get(ps.player.id)!.seasons.push(ps);
              return acc;
            }, new Map<string, { player: Player; seasons: PlayerSeason[] }>())
          ).map(([playerId, { player, seasons }]) => (
            <AccordionItem key={playerId} title={`${player.firstName} ${player.lastName}`}>
              <div className="p-4 border rounded space-y-2">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-bold">{player.firstName} {player.lastName}</h3>
                </div>
                <Table
                  selectionMode="multiple"
                  onSelectionChange={(keys) => {
                    if (!(keys instanceof Set)) return;

                    const selectedCompositeIds = Array.from(keys);

                    setUnsavedPlayerSeasons((prev) => {
                      const newSeasons: PlayerSeason[] = [];

                      for (const compositeId of selectedCompositeIds) {
                        const playerSeason = fetchedPlayerSeasons.find((ps) => ps.compositeId === compositeId);
                        if (playerSeason && !prev.some((p) => p.compositeId === compositeId)) {
                          newSeasons.push(playerSeason);
                        }
                      }

                      return [...prev, ...newSeasons];
                    });
                  }}
                >
                  <TableHeader>
                    <TableColumn key="season">Year</TableColumn>
                    <TableColumn key="team">Team</TableColumn>
                    <TableColumn key="league">League</TableColumn>
                  </TableHeader>
                  <TableBody items={seasons}>
                    {(playerSeason) => (
                      <TableRow key={playerSeason.compositeId}>
                        <TableCell>{playerSeason.season?.year}</TableCell>
                        <TableCell>{playerSeason.season?.teamName}</TableCell>
                        <TableCell>{playerSeason.season?.league}</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </div>
  );
}
