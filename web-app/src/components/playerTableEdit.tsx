import {
  Button, Table, TableBody, TableCell, TableColumn,
  TableHeader, TableRow, Select, SelectItem, Spinner,
  useDisclosure
} from "@heroui/react";
import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { formatPosition, formatSeasonLabel, getPlayerSeasonCompositeId, getSeasonSelectKey, isMLBCareer } from "~/utils/helper";
import PlayerCardModal from "./playerCardModal";
import { PlayerSeason } from "~/data/types";
import { Season, League } from "~/data/types";
import { api } from "~/utils/api";
import toast from "react-hot-toast";

type PropType = {
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};

const PlayerTableEdit = ({
  selectedPlayerSeasons,
  setSelectedPlayerSeasons
}: PropType) => {
  const { mutateAsync: getPlayerStats } = api.mlb.getPlayerStats.useMutation();

  const [playerSeasonsMap, setPlayerSeasonsMap] = useState<Record<string, Season[]>>({});
  const [isLoadingPlayerId, setIsLoadingPlayerId] = useState<string | null>(null);

  const loadStatsIfNeeded = async (playerId: string) => {
    if (playerSeasonsMap[playerId]) return;

    setIsLoadingPlayerId(playerId);
    try {
      const stats = await getPlayerStats({ playerId });

      const allSeasons = stats.filter((s) => s.teamId.length > 0).map((season) => ({
        ...season,
        teamName: season.teamName || "Unknown Team",
      }));

      const mlbSeasons = allSeasons.filter((s) => s.league === "MLB");

      const lifetimeSeason: Season | null = mlbSeasons.length > 0
        ? {
          ...mlbSeasons[0],
          id: `${playerId}-mlb-career`,
          year: 9999,
          teamId: "MLB",
          teamName: "MLB Career",
          league: "MLB",
          plateAppearances: mlbSeasons.reduce((sum, s) => sum + (s.plateAppearances || 0), 0),
          hits: mlbSeasons.reduce((sum, s) => sum + (s.hits || 0), 0),
          doubles: mlbSeasons.reduce((sum, s) => sum + (s.doubles || 0), 0),
          triples: mlbSeasons.reduce((sum, s) => sum + (s.triples || 0), 0),
          homeruns: mlbSeasons.reduce((sum, s) => sum + (s.homeruns || 0), 0),
          walks: mlbSeasons.reduce((sum, s) => sum + (s.walks || 0), 0),
          hitByPitch: mlbSeasons.reduce((sum, s) => sum + (s.hitByPitch || 0), 0),
          singles: mlbSeasons.reduce((sum, s) => sum + (s.singles || 0), 0),
          runs: mlbSeasons.reduce((sum, s) => sum + (s.runs || 0), 0),
          intentionalWalks: mlbSeasons.reduce((sum, s) => sum + (s.intentionalWalks || 0), 0),
        } as Season
        : null;

      const finalSeasons = lifetimeSeason ? [lifetimeSeason, ...allSeasons] : allSeasons;

      setPlayerSeasonsMap((prev) => ({
        ...prev,
        [playerId]: finalSeasons,
      }));
    } catch (e) {
      console.error("Failed to load stats for player", playerId, e);
    } finally {
      setIsLoadingPlayerId(null);
    }
  };

  useEffect(() => {
    selectedPlayerSeasons.forEach((playerSeason: PlayerSeason) => {
      const { player, season, isCustom } = playerSeason;

      if (season) {
        setPlayerSeasonsMap((prev) => {
          const hasSeasonAlready = prev[player.id]?.some(
            (s) => s.id === season.id && s.teamId === season.teamId
          );
          return hasSeasonAlready
            ? prev
            : {
              ...prev,
              [player.id]: [...(prev[player.id] || []), season],
            };
        });
      }

      if (!isCustom) {
        loadStatsIfNeeded(player.id).then(async () => {
          const allSeasons = playerSeasonsMap[player.id] || [];

          const mlbSeasons = allSeasons.filter((s) => s.league === "MLB");

          if (mlbSeasons.length > 0) {
            const lifetimeSeason: Season = {
              ...mlbSeasons[0],
              id: `${player.id}-mlb-career`,
              year: 9999,
              teamId: "MLB",
              teamName: "MLB Career",
              league: "MLB",
              plateAppearances: mlbSeasons.reduce((sum, s) => sum + (s.plateAppearances || 0), 0),
              hits: mlbSeasons.reduce((sum, s) => sum + (s.hits || 0), 0),
              doubles: mlbSeasons.reduce((sum, s) => sum + (s.doubles || 0), 0),
              triples: mlbSeasons.reduce((sum, s) => sum + (s.triples || 0), 0),
              homeruns: mlbSeasons.reduce((sum, s) => sum + (s.homeruns || 0), 0),
              walks: mlbSeasons.reduce((sum, s) => sum + (s.walks || 0), 0),
              hitByPitch: mlbSeasons.reduce((sum, s) => sum + (s.hitByPitch || 0), 0),
              singles: mlbSeasons.reduce((sum, s) => sum + (s.singles || 0), 0),
              runs: mlbSeasons.reduce((sum, s) => sum + (s.runs || 0), 0),
              intentionalWalks: mlbSeasons.reduce((sum, s) => sum + (s.intentionalWalks || 0), 0),
            } as Season;

            setPlayerSeasonsMap((prev) => {
              const existing = prev[player.id] || [];
              const alreadyIncluded = existing.some(
                (s) => s.id === lifetimeSeason.id && s.teamId === lifetimeSeason.teamId
              );
              return alreadyIncluded
                ? prev
                : {
                  ...prev,
                  [player.id]: [...existing, lifetimeSeason],
                };
            });
          }
        });
      }
    });
  }, [selectedPlayerSeasons]);


  return (
    <Table aria-label="Selected Players Table">
      <TableHeader>
        <TableColumn>NAME</TableColumn>
        <TableColumn>POSITION</TableColumn>
        <TableColumn>VIEW CARD</TableColumn>
        <TableColumn>SELECT YEAR</TableColumn>
        <TableColumn>REMOVE</TableColumn>
      </TableHeader>
      <TableBody emptyContent={"No players selected."}>
        {selectedPlayerSeasons.map((playerSeason) => {
          const player = playerSeason.player;
          const playerSeasons = playerSeasonsMap[player.id] || [];
          const selectedKey = playerSeason.season ? getSeasonSelectKey(playerSeason.season) : undefined;

          return (
            <TableRow key={playerSeason.compositeId}>
              <TableCell>{player.fullName}</TableCell>
              <TableCell>{formatPosition(player.position)}</TableCell>
              <TableCell><PlayerCardModal player={player} isDisabled={playerSeason.isCustom} /></TableCell>
              <TableCell>
                <Select
                  aria-label={`Select season for ${player.fullName}`}
                  label="Select Year"
                  placeholder="Choose a season"
                  selectedKeys={selectedKey ? new Set([selectedKey]) : new Set()}
                  onSelectionChange={(keys) => {
                    const seasonId = [...keys][0] as string;
                    const season = playerSeasons.find((s) => getSeasonSelectKey(s) === seasonId);

                    if (season) {
                      const updated: PlayerSeason = {
                        compositeId: getPlayerSeasonCompositeId(player, season),
                        player,
                        season
                      };

                      if (season.plateAppearances < 100) {
                        toast((
                          <div>
                            <strong className="block font-semibold text-yellow-500">Low Sample Size</strong>
                            <div className="mt-1 text-sm">
                              This player has fewer than 100 plate appearances. Results may be less accurate.
                            </div>
                          </div>
                        ), {
                          duration: 7500
                        });
                      }

                      setSelectedPlayerSeasons((prev) =>
                        prev.map(playerSeason =>
                          playerSeason.player.id === player.id ? updated : playerSeason
                        )
                      );
                    }
                  }}
                  isLoading={isLoadingPlayerId === player.id}
                  renderValue={() => {
                    if (!selectedKey) return "Choose a season";
                    const selectedSeason = playerSeasons.find(
                      (s) => getSeasonSelectKey(s).includes(selectedKey)
                    );

                    if (selectedSeason?.league === League.CUSTOM) return "Custom Season"

                    return selectedSeason
                      ? formatSeasonLabel(selectedSeason)
                      : "Choose a season";
                  }}
                  isDisabled={isLoadingPlayerId === player.id || playerSeason.isCustom}
                  className="min-w-60"
                >
                  {[...playerSeasons]
                    .sort((a, b) => {
                      if (isMLBCareer(a)) return -1;
                      if (isMLBCareer(b)) return 1;
                      return (b.year ?? 0) - (a.year ?? 0);
                    })
                    .map((season: Season) => (
                      <SelectItem
                        key={getSeasonSelectKey(season)}
                        textValue={formatSeasonLabel(season)}
                      >
                        {formatSeasonLabel(season)}
                      </SelectItem>
                    ))}

                </Select>
              </TableCell>
              <TableCell>
                <Button
                  isIconOnly
                  endContent={<>❌</>}
                  variant="light"
                  onPress={() => {
                    setSelectedPlayerSeasons((prev) =>
                      prev.filter((ps) => ps.player.id !== player.id)
                    );
                  }}
                />
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};

export default PlayerTableEdit;
