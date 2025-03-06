import { Card, CardHeader, CardBody, CardFooter, Button, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow } from "@heroui/react";
import { api } from "~/utils/api";

export type SeasonData = {
  id: string;
  year: number;
  plateAppearances: number;
  runs: number;
  hits: number;
  singles: number;
  doubles: number;
  triples: number;
  homeruns: number;
  walks: number;
  hitByPitch: number;
  intentionalWalks: number;
};

export type PlayerData = {
  id: string;
  firstName: string;
  lastName: string;
  position: string;
};

type PlayerCardProps = {
  player: PlayerData;
  onClose: () => void;
};

const PlayerCard = ({ player }: PlayerCardProps) => {
  const { data: seasons, isLoading, error } = api.player.getSeasonsByPlayerId.useQuery({ playerId: player.id });

  return (
    <div className="w-full">
      {isLoading ? (
        <p>Loading seasons...</p>
      ) : error ? (
        <p>Error loading seasons.</p>
      ) : seasons && seasons.length > 0 ? (
        <Table aria-label="Example static collection table">
          <TableHeader>
            <TableColumn>Year</TableColumn>
            <TableColumn>PA</TableColumn>
            <TableColumn>Runs</TableColumn>
            <TableColumn>Hits</TableColumn>
            <TableColumn>HR</TableColumn>
          </TableHeader>
          <TableBody>
            {seasons.map((season: SeasonData) => (
              <TableRow>
                <TableCell>{season.year}</TableCell>
                <TableCell>{season.plateAppearances}</TableCell>
                <TableCell>{season.runs}</TableCell>
                <TableCell>{season.hits}</TableCell>
                <TableCell>{season.homeruns}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p>No seasons found.</p>
      )}
    </div>
  );
};

export default PlayerCard;
