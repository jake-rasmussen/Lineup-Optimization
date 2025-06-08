import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Table,
  TableBody,
  TableCell,
  TableColumn,
  TableHeader,
  TableRow,
  CardFooter,
} from "@heroui/react";
import { useState } from "react";
import { api } from "~/utils/api";
import { Season } from "@prisma/client";
import toast from "react-hot-toast";
import PlayerSeasonDropdown from "../build/playerSeasonDropdown";

type PlayerData = {
  name: string;
  data: {
    plateAppearances: number,
    hits: number,
    doubles: number,
    triples: number,
    homeruns: number,
    walks: number,
    hitByPitch: number,
    intentionalWalks: number,
  } | null;
};

type SavedLineup = {
  id: string;
  name: string;
  expectedRuns?: number | null;
  data: Record<number, PlayerData>;
};

type PropType = {
  lineup: SavedLineup;
};

const SavedLineupCard = ({ lineup }: PropType) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerData | null>(null);

  const utils = api.useUtils(); // for cache invalidation

  const deleteLineup = api.lineup.deleteLineup.useMutation({
    onSuccess: () => {
      toast.success("Lineup deleted");
      utils.lineup.getLineups.invalidate(); // refresh list
    },
    onError: () => {
      toast.error("Failed to delete lineup");
    },
  });

  const spots = Object.keys(lineup.data)
    .map((k) => parseInt(k))
    .sort((a, b) => a - b);

  return (
    <>
      <Card className="w-full max-w-md my-4 shadow-xl shadow-blue-200 border">
        <CardHeader>
          <div className="flex justify-between items-center w-full">
            <h3 className="text-lg font-semibold">{lineup.name}</h3>
            {lineup.expectedRuns != null && (
              <p className="text-sm text-gray-500">
                Expected Runs: {lineup.expectedRuns.toFixed(2)}
              </p>
            )}
          </div>
        </CardHeader>
        <CardBody>
          <Table aria-label="Saved Lineup Table">
            <TableHeader>
              <TableColumn className="w-10 text-center">Spot</TableColumn>
              <TableColumn>Player</TableColumn>
              <TableColumn>Applied Stats</TableColumn>
            </TableHeader>
            <TableBody>
              {spots.map((spot) => {
                const player = lineup.data[spot];
                return (
                  <TableRow key={spot}>
                    <TableCell className="text-center">{spot}</TableCell>
                    <TableCell>{player?.name || "Unknown Player"}</TableCell>
                    <TableCell>
                      <PlayerSeasonDropdown season={player?.data as Season} />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardBody>
        <CardFooter>
          <div className="w-full flex justify-end">
            <Button
              isIconOnly
              variant="light"
              onPress={() => deleteLineup.mutate({ id: lineup.id })}
            >
              🗑️
            </Button>
          </div>
        </CardFooter>
      </Card>
    </>
  );
};

export default SavedLineupCard;
