import {
  Button,
  Divider, Input, Select, SelectItem,
  useDisclosure
} from "@heroui/react";
import { useEffect, useState } from "react";
import type { Selection } from "@heroui/react";
import toast from "react-hot-toast";
import { mlbTeamNameMap } from "~/data/teams";
import { api } from "~/utils/api";
import { Player, Season } from "@prisma/client";
import { PlayerSeason } from "~/data/types";
import PlayerTable from "~/components/playerTableEdit";
import CustomPlayerModal from "./customPlayerModal";
import { getPlayerSeasonCompositeId } from "~/utils/helper";
import SelectSeasonModal from "./selectSeasonModal";

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
  const [manualSeasonPlayer, setManualSeasonPlayer] = useState<Player | null>(null);
  const [forceCloseSelect, setForceCloseSelect] = useState(false);

  const { isOpen: isSelectSeasonOpen, onOpen: openSelectSeason, onClose: closeSelectSeason } = useDisclosure();

  const { data: fetchedPlayers, isLoading: isLoadingPlayers } = api.mlb.getPlayersByFilter.useQuery({
    teamId: selectedTeamId || undefined,
    seasonYear: selectedYear ? parseInt(selectedYear) : undefined,
    search: search || undefined,
  });

  const { mutateAsync: getPlayerStats } = api.mlb.getPlayerStats.useMutation();
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!selectedYear) return;
    fetch(`https://statsapi.mlb.com/api/v1/teams?sportId=1&season=${selectedYear}&activeStatus=Y`)
      .then((res) => res.json())
      .then((data) => setMlbTeams(data.teams || []));
  }, [selectedYear]);

  useEffect(() => {
    setIsLoading(isLoadingPlayers)
  }, [isLoadingPlayers]);

  const selectedPlayers = selectedPlayerSeasons.map((ps) => ps.player);
  const selectedKeys = new Set(selectedPlayers.map((p) => p.id));
  const seasonYears = Array.from({ length: 2025 - 1910 + 1 }, (_, i) => (2025 - i).toString());

  const handleSelectPlayer = async (
    keys: Selection,
    newPlayerId: string,
    player: Player,
    newStats: Season[]
  ) => {
    if (!(keys instanceof Set)) return;
    if (keys.size > 9) return toast.error("9 players already added");
    if (selectedPlayerSeasons.some((ps) => ps.player.id === newPlayerId)) return;

    let season: Season | undefined = undefined;

    if (selectedYear && selectedTeamId) {
      season = newStats.find((s) =>
        s.year === parseInt(selectedYear) && s.teamId === selectedTeamId
      );
    } else {
      setForceCloseSelect(true);

      setTimeout(() => {
        setForceCloseSelect(false);
        setManualSeasonPlayer(player);
        openSelectSeason();
      }, 0);
      return;
    }

    const compositeId = getPlayerSeasonCompositeId(player, season);

    const newEntry: PlayerSeason = {
      player,
      season,
      compositeId,
    };

    if (season && season.plateAppearances < 100) {
      toast(
        <div>
          <strong className="block font-semibold text-yellow-500">Low Sample Size</strong>
          <div className="mt-1 text-sm">
            This player has fewer than 100 plate appearances. Results may be less accurate.
          </div>
        </div>,
        { duration: 7500 }
      );
    }

    setSelectedPlayerSeasons((prev) => [...prev, newEntry]);
  };

  return (
    <div className="flex flex-col gap-4 w-full z-30">
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
              return team ? <p>{team.name}</p> : null;
            }}
            isDisabled={!selectedYear}
          >
            {mlbTeams.map((team) => {
              const modernName = mlbTeamNameMap.get(team.id.toString());
              return (
                <SelectItem key={team.id.toString()} textValue={team.name}>
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

      {!forceCloseSelect && (
        <Select
          label="Choose Player"
          placeholder="Select filters or search to find players"
          selectionMode="multiple"
          selectedKeys={selectedKeys}
          onSelectionChange={async (keys) => {
            const currentKey = keys.currentKey;
            if (!currentKey) return;

            const playerId = String(currentKey);
            const player = fetchedPlayers?.find((p) => p.id === playerId);
            if (!player) return;

            setIsLoading(true);
            const stats = await getPlayerStats({ playerId });
            await handleSelectPlayer(keys, playerId, player, stats);
            setIsLoading(false);
          }}
          isLoading={isLoading}
          isDisabled={(selectedTeamId && !selectedYear) || (!selectedTeamId && search.length === 0) || isLoading}
        >
          {(fetchedPlayers ?? [])
            .filter((player) => !selectedPlayers.some((p) => p.id === player.id))
            .map((player) => (
              <SelectItem key={player.id} textValue={`${player.displayName}`} className="z-0">
                {(player.fullName || "").replace(/&apos;/g, "'")}
                {(selectedTeamId && selectedYear)
                  ? ` - ${mlbTeams.find((team) => team.id === parseInt(selectedTeamId))?.name} ${selectedYear}`
                  : ""}
              </SelectItem>
            ))}
        </Select>
      )}

      <div className="flex mt-4 gap-4">
        {
          selectedPlayerSeasons.length > 0 && (
            <Button
              onPress={() => {
                setSelectedPlayerSeasons([]);
              }}
            >
              Clear Lineup
            </Button>
          )
        }

        <div className="grow flex justify-end">
          <CustomPlayerModal setSelectedPlayerSeasons={setSelectedPlayerSeasons} />
        </div>

      </div>

      <SelectSeasonModal
        isOpen={isSelectSeasonOpen}
        onClose={() => {
          setManualSeasonPlayer(null);
          closeSelectSeason();
        }}
        player={manualSeasonPlayer}
        getPlayerStats={(id) => getPlayerStats({ playerId: id })}
        onSeasonSelect={(season) => {
          if (!manualSeasonPlayer) return;
          const compositeId = getPlayerSeasonCompositeId(manualSeasonPlayer, season);
          const newEntry: PlayerSeason = {
            player: manualSeasonPlayer,
            season,
            compositeId,
          };

          if (season.plateAppearances < 100) {
            toast(
              <div>
                <strong className="block font-semibold text-yellow-500">Low Sample Size</strong>
                <div className="mt-1 text-sm">
                  This player has fewer than 100 plate appearances. Results may be less accurate.
                </div>
              </div>,
              { duration: 7500 }
            );
          }

          setSelectedPlayerSeasons((prev) => [...prev, newEntry]);
          setManualSeasonPlayer(null);
        }}
      />

      <Divider />

      <PlayerTable
        selectedPlayerSeasons={selectedPlayerSeasons}
        setSelectedPlayerSeasons={setSelectedPlayerSeasons}
      />
    </div>
  );
};

export default SelectMLBPlayers;
