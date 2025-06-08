import {
  Divider, Input, Select, SelectItem,
} from "@heroui/react";
import { useEffect, useState } from "react";
import type { Selection } from "@heroui/react";
import toast from "react-hot-toast";
import { mlbTeamNameMap } from "~/data/teams";
import { api } from "~/utils/api";
import { League, Player, Season } from "@prisma/client";
import { PlayerSeason } from "~/data/types";
import PlayerTable from "~/components/playerTableEdit";
import CustomPlayerModal from "./customPlayerModal";
import { getPlayerSeasonCompositeId } from "~/utils/helper";

type PropType = {
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: React.Dispatch<React.SetStateAction<PlayerSeason[]>>;
};

type MLBTeam = {
  id: number;
  name: string;
};

const SelectMLBPlayers = ({ selectedPlayerSeasons, setSelectedPlayerSeasons }: PropType) => {
  const [selectedYear, setSelectedYear] = useState<string>();
  const [selectedTeamId, setSelectedTeamId] = useState<string>();
  const [search, setSearch] = useState<string>("");
  const [mlbTeams, setMlbTeams] = useState<MLBTeam[]>([]);

  useEffect(() => {
    if (!selectedYear) return;
    fetch(`https://statsapi.mlb.com/api/v1/teams?sportId=1&season=${selectedYear}&activeStatus=Y`)
      .then((res) => res.json())
      .then((data) => setMlbTeams(data.teams || []));
  }, [selectedYear]);

  const queryInput = {
    teamId: selectedTeamId || undefined,
    seasonYear: selectedYear ? parseInt(selectedYear) : undefined,
    search: search || undefined,
  };

  const { data: fetchedPlayers, isLoading: isLoadingPlayers } = api.mlb.getPlayersByFilter.useQuery(queryInput);
  const { mutateAsync: getPlayerStats } = api.mlb.getPlayerStats.useMutation();

  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    setIsLoading(isLoadingPlayers)
  }, [isLoadingPlayers])

  const selectedPlayers = selectedPlayerSeasons.map((playerSeason) => playerSeason.player);
  const selectedKeys = new Set(selectedPlayers.map((player) => player.id));
  const seasonYears = Array.from({ length: 2025 - 1910 + 1 }, (_, i) => (2025 - i).toString());

  const handleSelectPlayer = async (
    keys: Selection,
    newPlayerId: string,
    player: Player,
    newStats: Season[]
  ) => {
    if (!(keys instanceof Set)) return;
    if (keys.size > 9) return toast.error("9 players already added");

    if (selectedPlayerSeasons.some((playerSeason) => playerSeason.player.id === newPlayerId)) return;

    let season: Season | undefined = undefined;
    if (selectedYear && selectedTeamId) {
      season = newStats.find((season) => season.year === parseInt(selectedYear) && season.teamId === selectedTeamId);
    }

    const compositeId = getPlayerSeasonCompositeId(player, season)

    const newEntry: PlayerSeason = {
      player,
      season,
      compositeId,
    };

    setSelectedPlayerSeasons((prev) => [...prev, newEntry]);
  };


  return (
    <div className="flex flex-col gap-4 w-full">
      <div className="flex gap-4">
        <div className="flex gap-4 w-1/2">
          <Select
            label="Select Roster Year"
            selectedKeys={selectedYear ? new Set([selectedYear]) : new Set()}
            onSelectionChange={(keys) => {
              setSelectedYear(Array.from(keys)[0] as string);
              setSelectedTeamId(undefined);
            }}
            className="max-w-60"
            description="Select player from team"
          >
            {seasonYears.map((year) => (
              <SelectItem key={year} textValue={`${year}`}>{year}</SelectItem>
            ))}
          </Select>

          <Select
            label="Select Team"
            selectedKeys={selectedTeamId ? new Set([selectedTeamId]) : new Set()}
            onSelectionChange={(keys) => {
              const selected = Array.from(keys)[0];
              if (selected) {
                setSelectedTeamId(selected.toString());
              }
            }}
            renderValue={(items) => {
              const id = items[0]?.key;
              const team = mlbTeams.find((t) => t.id.toString() === id);
              if (!team) return null;
              return <p>{team.name}</p>;
            }}
            isDisabled={!selectedYear}
          >
            {mlbTeams.map((team) => {
              const modernName = mlbTeamNameMap.get(team.id.toString());
              return (
                <SelectItem key={team.id.toString()} textValue={`${team.name}`}>
                  <div className="flex items-center gap-2">
                    {modernName === team.name ? (
                      <img src={`https://www.mlbstatic.com/team-logos/${team.id}.svg`} className="w-10 h-10" />
                    ) : (
                      <div className="w-10 h-10 flex items-center justify-center text-2xl">⚾️</div>
                    )}
                    <div>{team.name}</div>
                  </div>
                </SelectItem>
              );
            })}
          </Select>
        </div>

        <Divider orientation="vertical" />

        <div className="w-1/2">
          <Input
            label="Search player name"
            value={search}
            onValueChange={setSearch}
            className="flex-grow"
            description="Select player from direct search"
          />
        </div>
      </div>

      <Select
        label="Choose Player"
        placeholder="Select filters or search to find players"
        selectionMode="multiple"
        selectedKeys={selectedKeys}
        onSelectionChange={async (keys) => {
          const currentKey = keys.currentKey;
          const playerId = String(currentKey);

          const player = fetchedPlayers?.find((player) => player.id === playerId);
          if (!player) return;

          setIsLoading(true);

          const stats = await getPlayerStats({ playerId });
          handleSelectPlayer(keys, playerId, player, stats);
          
          setIsLoading(false);
        }}
        isLoading={isLoading}
        isDisabled={(selectedTeamId && !selectedYear) || (!selectedTeamId && search.length === 0) || isLoading}
      >
        <>
          {(fetchedPlayers ?? [])
            .filter((player) => !selectedPlayers.some((selectedPlayer) => selectedPlayer.id === player.id))
            .map((player) => (
              <SelectItem key={player.id} textValue={`${player.firstName} ${player.lastName}`}>
                {player.firstName.replace(/&apos;/g, "'")} {player.lastName.replace(/&apos;/g, "'")} {
                  (selectedTeamId && selectedYear) ? `- ${mlbTeams.find((team) => team.id === parseInt(selectedTeamId))?.name} ${selectedYear}` : ""
                }
              </SelectItem>
            ))}
        </>
      </Select>

      <div className="flex justify-end mt-4 gap-4">
        <CustomPlayerModal setSelectedPlayerSeasons={setSelectedPlayerSeasons} />
      </div>

      <Divider />
      <PlayerTable
        selectedPlayerSeasons={selectedPlayerSeasons}
        setSelectedPlayerSeasons={setSelectedPlayerSeasons}
      />
    </div >
  );
};

export default SelectMLBPlayers;
