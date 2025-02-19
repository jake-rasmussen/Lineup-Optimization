import {
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
} from "@heroui/modal";
import { Button, Select, SelectItem, useDisclosure } from "@heroui/react";
import { motion } from "framer-motion";
import { useState } from "react";
import { mockPlayers } from "~/data/players";
import type { Selection, SharedSelection } from "@heroui/react";

type PropType = {
  handleSubmit: (lineup: Record<number, string>) => void;
}

const BuildModal = (props: PropType) => {
  const { handleSubmit } = props;

  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const [selectedPlayers, setSelectedPlayers] = useState<Selection>(new Set());
  const [lineup, setLineup] = useState<Record<number, string>>({});

  const lineupSpots = Array.from({ length: 9 }, (_, i) => i + 1);

  const nextStep = () => {
    const players = new Set(selectedPlayers);
    if (step === 0 && players.size > 9) {
      setError("You cannot select more than 9 players.");
      return;
    } else if (step === 0 && players.size === 0) {
      setError(null);
      setStep((prev) => prev + 2);
    } else {
      setError(null);
      setStep((prev) => prev + 1);
    }

  };

  const prevStep = () => setStep((prev) => prev - 1);

  const handleSelectPlayers = (keys: SharedSelection) => {
    if (keys instanceof Set && keys.size > 9) {
      setError("You cannot select more than 9 players.");
    } else {
      setError(null);
      setSelectedPlayers(keys);
    }
  };

  const handleLineupChange = (spot: number, playerId: string) => {
    setLineup((prev) => {
      const newLineup = { ...prev };
      Object.keys(newLineup).forEach((key) => {
        if (newLineup[Number(key)] === playerId) {
          delete newLineup[Number(key)];
        }
      });
      newLineup[spot] = playerId;
      return newLineup;
    });
  };

  const assignedPlayers = new Set(Object.values(lineup));
  const unassignedPlayers = Array.from(selectedPlayers).filter(
    (playerId) => !assignedPlayers.has(playerId as string)
  );

  const variants = {
    enter: { opacity: 0, x: 100 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -100 },
  };

  return (
    <>
      <Button onPress={() => {
        setStep(0);
        onOpen();
        setSelectedPlayers(new Set());
        setLineup({});
      }} color="primary">
        Build Lineup
      </Button>
      <Modal isOpen={isOpen} onOpenChange={onOpenChange} size="2xl">
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader>
                {step === 0 && (
                  <div>
                    <h3>Select Players</h3>
                    <p className="text-gray-500 font-normal text-sm">Optional: Select up to 9 players for your lineup.</p>
                  </div>
                )}
                {step === 1 && (
                  <div>
                    <h3>Arrange Batting Order</h3>
                    <p className="text-gray-500 font-normal text-sm">Optional: Place any players in a certain position in your lineup.</p>
                  </div>
                )}
                {step === 2 && (
                  <div>
                    <h3>Review & Submit</h3>
                    <p className="text-gray-500 font-normal text-sm">Please review your lineup, and click submit once you're ready to compile your lineup</p>
                  </div>
                )}
              </ModalHeader>
              <ModalBody className="max-h-[70vh] overflow-y-scroll">
                <motion.div
                  key={step}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  variants={variants}
                  transition={{ duration: 0.6, ease: "easeInOut" }}
                  className="w-full"
                >
                  {step === 0 && (
                    <div className="flex flex-col">
                      <Select
                        className="max-w-md"
                        label="Select Players"
                        placeholder="Select up to 9 players"
                        selectionMode="multiple"
                        selectedKeys={selectedPlayers}
                        onSelectionChange={handleSelectPlayers}
                      >
                        {mockPlayers.map((player) => (
                          <SelectItem key={player.id}>{player.name}</SelectItem>
                        ))}
                      </Select>
                      {error && <p className="text-red-500 text-sm">{error}</p>}
                    </div>
                  )}

                  {step === 1 && (
                    <div className="flex flex-col gap-4">
                      {lineupSpots.map((spot) => (
                        <Select
                          key={spot}
                          label={`Batting Spot ${spot}`}
                          placeholder="Assign player"
                          selectionMode="single"
                          selectedKeys={new Set(lineup[spot] ? [lineup[spot]] : [])}
                          onSelectionChange={(selected) =>
                            handleLineupChange(spot, selected.currentKey as string)
                          }
                        >
                          {Array.from(selectedPlayers).map((playerId) => {
                            const player = mockPlayers.find((p) => p.id === playerId);
                            return player ? (
                              <SelectItem key={player.id}>{player.name}</SelectItem>
                            ) : null;
                          })}
                        </Select>
                      ))}
                    </div>
                  )}

                  {step === 2 && (
                    <div>
                      <h3 className="text-lg font-semibold">Final Lineup</h3>
                      <ul className="bg-gray-100 p-4 rounded-md">
                        {lineupSpots.map((spot) => (
                          <li key={spot}>
                            <strong>Batting Spot {spot}:</strong> {mockPlayers.find((p) => p.id === lineup[spot])?.name || "-"}
                          </li>
                        ))}
                      </ul>
                      {unassignedPlayers.length > 0 && (
                        <div className="mt-4">
                          <h4 className="text-lg font-semibold">Unassigned Players</h4>
                          <ul className="bg-gray-100 p-4 rounded-md">
                            {unassignedPlayers.map((playerId) => (
                              <li key={playerId}>{mockPlayers.find((p) => p.id === playerId)?.name || "Unknown Player"}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={step === 0 ? onClose : prevStep}>
                  {step === 0 ? "Close" : "Back"}
                </Button>
                {step < 2 && (
                  <Button color="primary" onPress={nextStep}>
                    Next
                  </Button>
                )}
                {step === 2 && (
                  <Button onPress={() => {
                    handleSubmit(lineup);
                    onOpenChange();
                  }} color="primary">
                    Submit
                  </Button>
                )}
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
};

export default BuildModal;
