import {
  Table,
  TableBody,
  TableCell,
  TableColumn,
  TableHeader,
  TableRow,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Button,
  Tooltip,
} from "@heroui/react";
import { PlayerSeason } from "~/data/types";

type PropType = {
  selectedPlayerSeasons: PlayerSeason[];
  pitcherHandedness: "LEFT" | "RIGHT" | null;
};

const SelectedPlayersTable = ({ selectedPlayerSeasons, pitcherHandedness }: PropType) => {
  const getStatType = (ps: PlayerSeason): string => {
    if (!ps.seasonSplits) return "Full Season";
    if (pitcherHandedness === "LEFT") return "vs Left";
    if (pitcherHandedness === "RIGHT") return "vs Right";
    return "Full Season";
  };

  const getDisplayedSeason = (ps: PlayerSeason) => {
    if (pitcherHandedness === "LEFT") return ps.seasonSplits?.vsLeft ?? ps.season;
    if (pitcherHandedness === "RIGHT") return ps.seasonSplits?.vsRight ?? ps.season;
    return ps.season;
  };

  const renderStatsTable = (ps: PlayerSeason) => {
    const s = getDisplayedSeason(ps);
    if (!s) return <p className="text-gray-400 px-4 py-2">No stats available</p>;

    return (
      <div className="p-2 w-full">
        <Table
          aria-label="Mini Stat Table"
          removeWrapper
          className="w-full min-w-[500px]"
          isCompact
        >
          <TableHeader>
            <TableColumn>PA</TableColumn>
            <TableColumn>H</TableColumn>
            <TableColumn>2B</TableColumn>
            <TableColumn>3B</TableColumn>
            <TableColumn>HR</TableColumn>
            <TableColumn>BB</TableColumn>
            <TableColumn>HBP</TableColumn>
            <TableColumn>IBB</TableColumn>
            <TableColumn>SB</TableColumn>
          </TableHeader>
          <TableBody>
            <TableRow key={ps.compositeId}>
              <TableCell>{s.plateAppearances}</TableCell>
              <TableCell>{s.hits}</TableCell>
              <TableCell>{s.doubles}</TableCell>
              <TableCell>{s.triples}</TableCell>
              <TableCell>{s.homeruns}</TableCell>
              <TableCell>{s.walks}</TableCell>
              <TableCell>{s.hitByPitch}</TableCell>
              <TableCell>{s.intentionalWalks}</TableCell>
              <TableCell>{0}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    );
  };

  const hasLowSamplePlayer = selectedPlayerSeasons.some((ps) => {
    const s = getDisplayedSeason(ps);
    return s?.plateAppearances !== undefined && s.plateAppearances < 100;
  });

  return (
    <div className="space-y-4">
      <Table aria-label="Selected Player Seasons Table" className="max-w-6xl">
        <TableHeader>
          <TableColumn>PLAYER</TableColumn>
          <TableColumn>YEAR</TableColumn>
          <TableColumn>STATS USED</TableColumn>
        </TableHeader>
        <TableBody>
          {selectedPlayerSeasons.map((ps) => {
            const statLabel = getStatType(ps);
            const season = getDisplayedSeason(ps);
            const isLowSample =
              season?.plateAppearances !== undefined && season.plateAppearances < 100;

            return (
              <TableRow key={ps.compositeId}>
                <TableCell className="font-medium relative">
                  {ps.player.fullName}
                </TableCell>
                <TableCell>{season?.year ?? "N/A"}</TableCell>
                <TableCell className="flex flex-row">
                  <Dropdown placement="bottom-end">
                    <DropdownTrigger>
                      <Button variant="flat" size="sm" className="min-w-28">
                        View Stats
                      </Button>
                    </DropdownTrigger>
                    <DropdownMenu
                      aria-label="Stat Details"
                      className="w-fit min-w-[520px] px-2 py-1"
                      itemClasses={{ base: "pointer-events-none p-0" }}
                    >
                      <DropdownItem key="statsTable" className="w-full">
                        {renderStatsTable(ps)}
                      </DropdownItem>
                    </DropdownMenu>
                  </Dropdown>

                  {isLowSample && (
                    <div className="flex w-full justify-end items-center hover:cursor-pointer">
                      <Tooltip content="Fewer than 100 plate appearances" placement="left" showArrow color="warning">
                        <span className="text-yellow-600 inline-block leading-none text-xl">⚠️</span>
                      </Tooltip>
                    </div>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      {hasLowSamplePlayer && (
        <div className="text-sm text-gray-500 px-1 flex gap-4 items-center">
          <div className="text-xl">⚠️</div>
          <p>Players with fewer than 100 plate appearances may have unreliable stats.</p>
        </div>
      )}
    </div>
  );
};

export default SelectedPlayersTable;
