import {
  Divider, Select, SelectItem,
} from "@heroui/react";
import { useEffect, useState } from "react";
import type { Selection } from "@heroui/react";
import toast from "react-hot-toast";
import { api } from "~/utils/api";
import { PlayerSeason } from "~/data/types";
import CustomPlayerModal from "../customPlayerModal";
import SearchMLBModal from "../searchMLBModal";
import PlayerTableALPB from "./playerTableEdit";
import { Season } from "@prisma/client";
import { getPlayerSeasonString } from "~/utils/helper";

type PropType = {
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: React.Dispatch<React.SetStateAction<PlayerSeason[]>>;
};

const SelectALPBPlayers = ({ selectedPlayerSeasons, setSelectedPlayerSeasons }: PropType) => {
  const [selectedSeasonId, setSelectedSeasonId] = useState<string>();
  const [selectedTeam, setSelectedTeam] = useState<string>();
  const [isLoading, setIsLoading] = useState(false);

  const { data: seasons = [] } = api.alpb.getSeasons.useQuery();
  const { data: teamsForSeason = [], isLoading: teamsLoading } = api.alpb.getTeamsBySeason.useQuery(
    { leagueId: "174", seasonId: selectedSeasonId! },
    { enabled: !!selectedSeasonId }
  );

  const {
    data: fetchedPlayerSeasons = [],
    isLoading: isLoadingPlayers
  } = api.alpb.getPlayersByFilter.useQuery(
    {
      teamId: selectedTeam || undefined,
      seasonId: selectedSeasonId,
    },
    {
      enabled: !!selectedSeasonId && !!selectedTeam,
    }
  );

  useEffect(() => {
    setIsLoading(isLoadingPlayers);
  }, [isLoadingPlayers]);

  const selectedKeys = new Set(
    selectedPlayerSeasons.map((ps) => ps.compositeId)
  );

  const handleSelectPlayer = (keys: Selection) => {
    if (!(keys instanceof Set)) return;

    const selectedIds = Array.from(keys) as string[];
    if (selectedIds.length > 9) {
      toast.error("You cannot select more than 9 players.");
      return;
    }

    const newSelections = fetchedPlayerSeasons.filter((playerSeason) =>
      selectedIds.includes(playerSeason.compositeId)
    );

    const merged = [
      ...selectedPlayerSeasons.filter((ps) => selectedIds.includes(ps.compositeId)),
      ...newSelections,
    ];

    const unique = new Map<string, PlayerSeason>();
    for (const playerSeason of merged) {
      unique.set(playerSeason.compositeId, playerSeason as PlayerSeason);
    }

    setSelectedPlayerSeasons(Array.from(unique.values()));
  };

  return (
    <div className="flex flex-col gap-4 items-center w-full">
      <div className="flex gap-4 w-full">
        <Select
          label="Select Roster Season"
          selectedKeys={selectedSeasonId ? new Set([selectedSeasonId]) : new Set()}
          onSelectionChange={(keys) => {
            setSelectedSeasonId(Array.from(keys)[0] as string);
            setSelectedTeam(undefined);
          }}
          className="w-1/2"
          renderValue={() =>
            seasons.find((season: Season) => season.id === selectedSeasonId)?.name ?? "Choose a season"
          }
        >
          {[...seasons]
            .sort((a, b) => (b.year ?? 0) - (a.year ?? 0))
            .map((season) => (
              <SelectItem key={season.id}>{season.name}</SelectItem>
            ))}
        </Select>

        <Select
          label="Select Team"
          selectedKeys={selectedTeam ? new Set([selectedTeam]) : new Set()}
          onSelectionChange={(keys) => {
            setSelectedTeam(Array.from(keys)[0] as string);
          }}
          className="w-1/2"
          isDisabled={!selectedSeasonId}
        >
          {teamsLoading ? (
            <SelectItem key="loading" isReadOnly className="text-gray-400">
              Loading teams...
            </SelectItem>
          ) : (
            teamsForSeason.map(({ id, name }) => (
              <SelectItem key={id}>{name}</SelectItem>
            ))
          )}
        </Select>
      </div>

      <Select
        label="Choose Player"
        placeholder="Select a team and season to load players"
        selectionMode="multiple"
        selectedKeys={selectedKeys}
        onSelectionChange={handleSelectPlayer}
        isLoading={isLoading}
        isDisabled={!selectedSeasonId || !selectedTeam || isLoading}
        renderValue={() => {
          const selectedNames = Array.from(selectedKeys)
            .map((id) => {
              const playerSeason = selectedPlayerSeasons.find((p) => p.compositeId === id);
              return playerSeason ? getPlayerSeasonString(playerSeason) : null;
            })
            .filter(Boolean)
            .join(", ");

          return selectedNames || "Choose Player";
        }}
      >
        {isLoading ? (
          <SelectItem key="loading" className="text-gray-400" isReadOnly>
            Loading players...
          </SelectItem>
        ) : (
          fetchedPlayerSeasons
            .filter((playerSeason) => !selectedKeys.has(playerSeason.compositeId))
            .map((playerSeason) => (
              <SelectItem key={playerSeason.compositeId}>
                {getPlayerSeasonString(playerSeason as PlayerSeason)}
              </SelectItem>
            ))
        )}
      </Select>


      <div className="flex justify-end mt-4 gap-4">
        <CustomPlayerModal setSelectedPlayerSeasons={setSelectedPlayerSeasons} />
        <SearchMLBModal
          selectedPlayerSeasons={selectedPlayerSeasons}
          setSelectedPlayerSeasons={setSelectedPlayerSeasons}
        />
      </div>

      <Divider />
      <PlayerTableALPB
        selectedPlayerSeasons={selectedPlayerSeasons}
        setSelectedPlayerSeasons={setSelectedPlayerSeasons}
      />
    </div>
  );
};

export default SelectALPBPlayers;
