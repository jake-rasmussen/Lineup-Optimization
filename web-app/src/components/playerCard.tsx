import { Card, CardBody, Divider, Spinner, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow } from "@heroui/react";
import { Player, Position, Season } from "@prisma/client";
import { api } from "~/utils/api";
import { formatPosition, getTeamName } from "~/utils/helper";

const CardHeader = ({ className, playerName, playerPosition }: { className?: string, playerName: string, playerPosition: Position }) => {
  return (
    <div className={`relative ${className}`}>
      <div className="absolute left-[23%] top-[7%] uppercase flex flex-row items-end gap-1">
        <h3 className="text-2xl font-semibold text-white ">
          {playerName}
        </h3>
        <Divider orientation="vertical" />
        <span className="uppercase font-black text-gray-200">
          {formatPosition(playerPosition)}
        </span>
      </div>

      <svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 930.42 133.51">
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#991b1b" stop-opacity="1" />
            <stop offset="100%" stop-color="#CA3B33" stop-opacity="1" />
          </linearGradient>
        </defs>
        <path fill="url(#gradient)" d="M204,9.16h734.1V142.67C885.31,127,829,112.84,769.14,101.08,533.65,54.77,322.33,61,154.12,83.17A246.76,246.76,0,0,0,188.6,38.86,246.25,246.25,0,0,0,204,9.16Z" transform="translate(-7.7 -9.16)" />
        <polygon fill="#6b7280" points="92.83 78.44 100.08 85.36 126.11 92.28 130.4 82.06 121.17 74.48 92.83 78.44" />
        <path fill="#6b7280" d="M111.37,77.53,145,58.77Z" transform="translate(-7.7 -9.16)" />
        <path fill="#6b7280" d="M111.37,77.53,39.85,65.78s33.8-29.89,105.11-7" transform="translate(-7.7 -9.16)" />
        <polygon fill="#6b7280" points="79.97 83.38 83.47 74.48 0 57.44 0 66.75 79.97 83.38" />
        <path fill="#6b7280" d="M195.5,17.49s-11.09,20.55-18.93,31c-8.55,11.34-14.48,19.7-27.28,33.61l-16.49-7a302.67,302.67,0,0,0,38-30.61C182.4,33.35,195.5,17.49,195.5,17.49Z" transform="translate(-7.7 -9.16)" />
        <path fill="#6b7280" d="M160.77,91" transform="translate(-7.7 -9.16)" />
      </svg>
    </div>)
}

type PlayerCardProps = {
  player: Player;
  onClose: () => void;
};

const PlayerCard = ({ player }: PlayerCardProps) => {
  const { data: seasons, isLoading, error } = api.player.getSeasonsByPlayerId.useQuery({ playerId: player.id });

  if (isLoading) {
    return (
      <div className="w-full flex justify-center">
        <Spinner label="loading" />
      </div>
    )
  } else if (error) {
    return (
      <p>Error loading seasons.</p>
    )
  } else {
    return (
      <Card className="w-full rounded-none">
        <CardBody className="border border-4 border-red-500 p-1 relative">
          <CardHeader className="" playerName={`${player.firstName} ${player.lastName}`} playerPosition={player.position} />
          {seasons && seasons.length > 0 ? (
            <div className="overflow-x-auto mt-4">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-red-700 text-white">
                    <th className="border border-gray-300 p-2 text-center">Year</th>
                    <th className="border border-gray-300 p-2 text-center">Team</th>
                    <th className="border border-gray-300 p-2 text-center">PA</th>
                    <th className="border border-gray-300 p-2 text-center">Runs</th>
                    <th className="border border-gray-300 p-2 text-center">Hits</th>
                    <th className="p-2 text-center">HR</th>
                  </tr>
                </thead>
                <tbody>
                  {seasons.map((season: Season) => (
                    <tr key={season.id} className="odd:bg-gray-100 even:bg-gray-200">
                      <td className="border border-gray-300 p-2">{season.year}</td>
                      <td className="border border-gray-300 p-2">{getTeamName(season.teamId)}</td>
                      <td className="border border-gray-300 p-2">{season.plateAppearances}</td>
                      <td className="border border-gray-300 p-2">{season.runs}</td>
                      <td className="border border-gray-300 p-2">{season.hits}</td>
                      <td className="border border-gray-300 p-2">{season.homeruns}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No seasons found.</p>
          )}
        </CardBody>
      </Card>
    );
  }
};

export default PlayerCard;
