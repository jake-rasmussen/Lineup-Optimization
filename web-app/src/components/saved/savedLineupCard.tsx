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
  TableRow 
} from "@heroui/react";
import { useState } from "react";
import PlayerCard from "../playerCard";
import { Lineup, LineupEntry, Player } from "@prisma/client";

type PropType = {
  lineup: Lineup & {
    entries: (LineupEntry & {
      player: Player;
    })[];
  };
};

const SavedLineupCard = ({ lineup }: PropType) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  return (
    <>
      <Card className="w-full max-w-md my-4 shadow-xl shadow-blue-200 border">
        <CardHeader>
          <h3 className="text-lg font-semibold">Saved Lineup</h3>
        </CardHeader>
        <CardBody>
          <Table aria-label="Final Lineup Table">
            <TableHeader>
              <TableColumn className="w-10">Batting Spot</TableColumn>
              <TableColumn>Player Name</TableColumn>
              <TableColumn>View Details</TableColumn>
            </TableHeader>
            <TableBody>
              {lineup.entries.map((lineupEntry) => {
                const player = lineupEntry.player;
                return (
                  <TableRow key={lineupEntry.battingSpot}>
                    <TableCell className="text-center">{lineupEntry.battingSpot}</TableCell>
                    <TableCell>
                      {player ? `${player.firstName} ${player.lastName}` : "-"}
                    </TableCell>
                    <TableCell>
                      <Button
                        onPress={() => {
                          setSelectedPlayer(lineupEntry.player);
                          onOpen();
                        }}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardBody>
      </Card>

      {selectedPlayer && (
        <Modal
          isOpen={isOpen}
          onOpenChange={onOpenChange}
          placement="center"
          size="3xl"
        >
          <ModalContent>
            {(onClose) => (
              <>
                <ModalHeader>
                  {selectedPlayer.firstName} {selectedPlayer.lastName}
                </ModalHeader>
                <ModalBody>
                  <PlayerCard
                    player={selectedPlayer}
                    onClose={() => setSelectedPlayer(null)}
                  />
                </ModalBody>
                <ModalFooter>
                  <Button
                    onPress={() => {
                      onClose();
                      setSelectedPlayer(null);
                    }}
                  >
                    Close
                  </Button>
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
