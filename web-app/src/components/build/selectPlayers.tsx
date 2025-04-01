import { Divider, Input, Select, SelectItem } from "@heroui/react";
import { Dispatch, SetStateAction, useState } from "react";
import type { Selection } from "@heroui/react";
import toast from "react-hot-toast";
import mlbTeamMap from "~/data/teams";
import { api } from "~/utils/api";
import type { Player, Season } from "@prisma/client";
import PlayerTable from "../playerTableEdit";
import { PlayerSeason } from "./buildController";
import { getTeamName } from "~/utils/helper";
import TeamLogo from "../teamLogo";

type PropType = {
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};

const seasonYears = ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015"]

const SelectPlayers = ({ selectedPlayerSeasons, setSelectedPlayerSeasons }: PropType) => {
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [search, setSearch] = useState<string>("");
  const [dropdownOpened, setDropdownOpened] = useState(false);

  const { data: fetchedPlayers, isLoading } = api.player.getPlayersByFilter.useQuery(
    {
      teamId: selectedTeam || undefined,
      seasonYear: selectedYear ? parseInt(selectedYear) : undefined,
      search: search || undefined,
    },
    {
      enabled: dropdownOpened && (!!selectedTeam || !!selectedYear || search.length > 0),
    }
  );

  const playerSeasons = fetchedPlayers
    ? fetchedPlayers.flatMap((player: Player & { seasons: Season[] }) =>
      player.seasons.map((season) => ({
        compositeId: `${player.id}-${season.id}`,
        player,
        season,
      }))
    )
    : [];

  const selectedKeys = new Set(selectedPlayerSeasons.map((ps) => ps.compositeId));

  const handleSelectPlayerSeasons = (keys: Selection) => {
    if (keys instanceof Set) {
      if (keys.size > 9) {
        toast.dismiss();
        toast.error("You cannot select more than 9 player seasons.");
        return;
      }
      const selectedIds = Array.from(keys);
      const psMap = new Map<string, PlayerSeason>();

      selectedPlayerSeasons.forEach((ps) => {
        if (selectedIds.includes(ps.compositeId)) {
          psMap.set(ps.compositeId, ps);
        }
      });

      playerSeasons.forEach((ps) => {
        if (selectedIds.includes(ps.compositeId) && !psMap.has(ps.compositeId)) {
          psMap.set(ps.compositeId, ps);
        }
      });

      setSelectedPlayerSeasons(Array.from(psMap.values()));
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-4">
        <Select
          label="Select Year"
          placeholder="Choose a year"
          selectedKeys={selectedYear ? new Set([selectedYear]) : new Set()}
          onSelectionChange={(keys) => setSelectedYear(Array.from(keys)[0] as string)}
          className="max-w-40"
          renderValue={() => selectedYear ?? "Choose a year"}
        >
          {seasonYears.map((year) => (
            <SelectItem key={year} value={year}>
              {year}
            </SelectItem>
          ))}
        </Select>

        <Select
          label="Select Team"
          placeholder="Choose a team"
          selectedKeys={selectedTeam ? new Set([selectedTeam]) : new Set()}
          onSelectionChange={(keys) => setSelectedTeam(Array.from(keys)[0] as string)}
          className="max-w-60"
          renderValue={() => {
            const teamName = selectedTeam ? mlbTeamMap.get(selectedTeam) : "Choose a team";
            return teamName;
          }}
        >
          {Array.from(mlbTeamMap.entries()).map(([id, name]) => (
            <SelectItem key={id} value={id}>
              <div className="flex flex-row items-center gap-2">
                <TeamLogo teamId={id} className="w-10 h-10 object-fit" />  <div>{name}</div>
              </div>
            </SelectItem>
          ))}
        </Select>

        <Input
          label="Search player name"
          value={search}
          onValueChange={setSearch}
          className="grow h-full flex"
        />
      </div>

      <Select
        label="Select Player Seasons"
        placeholder="Click to load player seasons"
        selectionMode="multiple"
        selectedKeys={selectedKeys}
        onFocus={() => setDropdownOpened(true)}
        onSelectionChange={handleSelectPlayerSeasons}
        renderValue={() =>
          Array.from(selectedKeys)
            .map((compositeId) => {
              const ps = selectedPlayerSeasons.find((item) => item.compositeId === compositeId);
              return ps ? `${ps.player.firstName} ${ps.player.lastName} - ${getTeamName(ps.season.teamId)} ${ps.season.year}` : "";
            })
            .join(", ")
        }
        isLoading={isLoading}
        isDisabled={selectedTeam === null && selectedYear === null && search.length === 0}
      >
        {isLoading ? (
          <SelectItem key="loading" value="loading" className="w-full text-gray-400" isReadOnly>
            Loading player seasons...
          </SelectItem>
        ) : (
          playerSeasons.map((ps) => (
            <SelectItem key={ps.compositeId} value={ps.compositeId}>
              {ps.player.firstName} {ps.player.lastName} - {getTeamName(ps.season.teamId)} {ps.season.year}
            </SelectItem>
          ))
        )}
      </Select>

      <>
        <Divider />
        <PlayerTable
          selectedPlayerSeasons={selectedPlayerSeasons}
          setSelectedPlayerSeasons={setSelectedPlayerSeasons}
        />
      </>
    </div>
  );
};

export default SelectPlayers;
