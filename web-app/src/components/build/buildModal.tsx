import {
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
} from "@heroui/modal";
import { Button, Select, SelectItem } from "@heroui/react";
import { motion } from "framer-motion";
import { useState } from "react";
import { mockPlayers } from "~/data/players";
import type { Selection, SharedSelection } from "@heroui/react";
import toast from "react-hot-toast";

type PropType = {
  handleSubmit: (lineup: Record<number, string | undefined>, unassignedPlayers: string[]) => void;
}

const BuildModal = (props: PropType) => {
  const { handleSubmit } = props;

  const [step, setStep] = useState(0);

  const [selectedPlayers, setSelectedPlayers] = useState<Selection>(new Set());
  const [lineup, setLineup] = useState<Record<number, string | undefined>>(
    Object.fromEntries(Array.from({ length: 9 }, (_, i) => [i + 1, undefined]))
  );

  const lineupSpots = Array.from({ length: 9 }, (_, i) => i + 1);

  const nextStep = () => {
    const players = new Set(selectedPlayers);
    if (step === 0 && players.size > 9) {
      return;
    } else if (step === 0 && players.size === 0) {
      setStep((prev) => prev + 2);
    } else {
      setStep((prev) => prev + 1);
    }

  };

  const prevStep = () => setStep((prev) => prev - 1);

  const handleSelectPlayers = (keys: SharedSelection) => {
    if (keys instanceof Set && keys.size > 9) {
      toast.dismiss();
      toast.error("You cannot select more than 9 players.");
    } else {
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
  const unassignedPlayers: string[] = Array.from(selectedPlayers).filter(
    (playerId) => !assignedPlayers.has(playerId as string)
  ) as string[];

  const variants = {
    enter: { opacity: 0, x: 100 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -100 },
  };

  return (
    <>
      <Modal isOpen={true} size="2xl" className="h-[70vh]" backdrop="blur" hideCloseButton>
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
                    <div className="flex flex-col gap-4">
                      <Select
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

                      {
                        Array.from(selectedPlayers).length > 0 && (
                          <>
                            <h3 className="text-lg font-semibold">Selected</h3>
                            <ul className="bg-gray-100 p-4 rounded-md flex flex-col gap-2">
                              {Array.from(selectedPlayers).map((playerId) => {
                                const player = mockPlayers.find((p) => p.id === playerId);
                                return player ? (
                                  <div className="flex flex-row gap-1 items-center" key={playerId}><strong className="text-xs">⚾️</strong>{player.name}</div>
                                ) : null;
                              })}
                            </ul>
                          </>
                        )
                      }
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
                <Button color="danger" variant="light" onPress={step === 0 ? onClose : prevStep} isDisabled={step === 0}>
                  Back
                </Button>
                {step < 2 && (
                  <Button color="primary" onPress={nextStep}>
                    Next
                  </Button>
                )}
                {step === 2 && (
                  <Button onPress={() => {
                    handleSubmit(lineup, unassignedPlayers);
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
