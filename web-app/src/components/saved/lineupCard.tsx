import { Card, CardHeader, CardBody, CardFooter, Button, Tooltip, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure } from "@heroui/react";
import { useState } from "react";
import PlayerCard, { PlayerData } from "./playerCard";

export type SavedLineupPlayer = {
  battingSpot: number;
  position: string;
  player: {
    id: string;
    firstName: string;
    lastName: string;
  };
};

export type SavedLineup = {
  id: string;
  userEmail: string;
  players: SavedLineupPlayer[];
};

type SavedLineupCardProps = {
  lineup: SavedLineup;
};

const SavedLineupCard = ({ lineup }: SavedLineupCardProps) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [selectedPlayer, setSelectedPlayer] = useState<null | SavedLineupPlayer>(null);

  const sortedPlayers = [...lineup.players].sort((a, b) => a.battingSpot - b.battingSpot);

  const toPlayerData = (lp: SavedLineupPlayer): PlayerData => ({
    id: lp.player.id,
    firstName: lp.player.firstName,
    lastName: lp.player.lastName,
    position: lp.position,
  });

  return (
    <>
      <Card className="w-full max-w-md my-4 shadow-xl shadow-blue-200">
        <CardHeader>
        </CardHeader>
        <CardBody>
          <ul className="space-y-2">
            {sortedPlayers.map((lp) => (
              <li key={lp.battingSpot} className="flex items-center gap-2">
                <strong>Spot {lp.battingSpot}:</strong>{" "}
                <button
                  className="transition duration-300 ease-in-out hover:text-blue-500"
                  onClick={() => {
                    onOpen();
                    setSelectedPlayer(lp);
                  }}
                >
                  {lp.player.firstName} {lp.player.lastName}
                </button>
              </li>
            ))}
          </ul>
        </CardBody>
        <CardFooter>
          <Button>View Details</Button>
        </CardFooter>
      </Card>

      {selectedPlayer && (
        <Modal isOpen={isOpen} onOpenChange={onOpenChange} placement="center">
          <ModalContent>
            {(onClose) => (
              <>
                <ModalHeader>
                  {selectedPlayer.player.firstName} {selectedPlayer.player.lastName}
                </ModalHeader>
                <ModalBody>
                  <PlayerCard
                    player={toPlayerData(selectedPlayer)}
                    onClose={() => setSelectedPlayer(null)}
                  />
                </ModalBody>
                <ModalFooter>
                  <Button onPress={() => {
                    onClose();
                  }}>Close</Button>
                </ModalFooter>
              </>
            )}
          </ModalContent>
        </Modal>
      )}
    </>
  );
};

export default SavedLineupCard;
