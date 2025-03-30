import { Divider, Input, Select, SelectItem } from "@heroui/react";
import { Dispatch, SetStateAction, useState } from "react";
import type { Selection } from "@heroui/react";
import toast from "react-hot-toast";
import mlbTeamMap from "~/data/teams";
import { api } from "~/utils/api";
import type { Player } from "@prisma/client";
import PlayerTable from "../playerTableEdit";

type PropType = {
  selectedPlayers: Player[];
  setSelectedPlayers: Dispatch<SetStateAction<Player[]>>;
};

const SelectPlayers = ({ selectedPlayers, setSelectedPlayers }: PropType) => {
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

  const selectedKeys = new Set(selectedPlayers.map((player) => player.id));

  const handleSelectPlayers = (keys: Selection) => {
    if (keys instanceof Set) {
      if (keys.size > 9) {
        toast.dismiss();
        toast.error("You cannot select more than 9 players.");
        return;
      }
      const selectedIds = Array.from(keys);
      const playerMap = new Map<string, Player>();

      selectedPlayers.forEach((player) => {
        if (selectedIds.includes(player.id)) {
          playerMap.set(player.id, player);
        }
      });

      if (fetchedPlayers) {
        fetchedPlayers.forEach((player: Player) => {
          if (selectedIds.includes(player.id) && !playerMap.has(player.id)) {
            playerMap.set(player.id, {
              id: player.id,
              firstName: player.firstName,
              lastName: player.lastName,
              position: player.position,
            });
          }
        });
      }

      setSelectedPlayers(Array.from(playerMap.values()));
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
          {["2024"].map((year) => (
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
              {name}
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
        label="Select Players"
        placeholder="Click to load players"
        selectionMode="multiple"
        selectedKeys={selectedKeys}
        onFocus={() => setDropdownOpened(true)}
        onSelectionChange={handleSelectPlayers}
        renderValue={() =>
          Array.from(selectedKeys)
            .map((id) => {
              const player = selectedPlayers.find((p) => p.id === id);
              return player ? `${player.firstName} ${player.lastName}` : "";
            })
            .join(", ")
        }
        isLoading={isLoading}
        isDisabled={selectedTeam === null && selectedYear === null && search.length === 0}
      >
        {isLoading ? (
          <SelectItem key="loading" value="loading" className="w-full text-gray-400">
            Loading players...
          </SelectItem>
        ) : (
          (fetchedPlayers || []).map((player: Player) => (
            <SelectItem key={player.id} value={player.id}>
              {player.firstName} {player.lastName}
            </SelectItem>
          ))
        )}
      </Select>

      {selectedPlayers.length > 0 && (
        <>
          <Divider />
          <PlayerTable
            selectedPlayers={selectedPlayers}
            setSelectedPlayers={setSelectedPlayers}
          />
        </>
      )}
    </div>
  );
};

export default SelectPlayers;
