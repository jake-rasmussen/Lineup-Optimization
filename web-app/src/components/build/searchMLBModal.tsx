import { Button, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure } from "@heroui/react";
import { PlayerSeason } from "~/data/types";
import SearchMLBPlayers from "./searchMLBPlayers";
import { Dispatch, SetStateAction, useState } from "react";
import toast from "react-hot-toast";

type Props = {
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};
const SearchMLBModal = ({ setSelectedPlayerSeasons }: Props) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [unsavedPlayerSeasons, setUnsavedPlayerSeasons] = useState<PlayerSeason[]>([]);

  const handleSave = () => {
    for (const ps of unsavedPlayerSeasons) {
      const season = ps.season;
      if (season && season.plateAppearances < 100) {
        toast(
          <div>
            <strong className="block font-semibold text-yellow-500">Low Sample Size</strong>
            <div className="mt-1 text-sm">
              This player has fewer than 100 plate appearances. Results may be less accurate.
            </div>
          </div>,
          {
            duration: 7500,
          }
        );
        break;
      }
    }

    setSelectedPlayerSeasons((prev) => {
      const existingIds = new Set(prev.map((ps) => ps.player.id));
      const newOnes = unsavedPlayerSeasons.filter((ps) => !existingIds.has(ps.player.id));
      return [...prev, ...newOnes];
    });

  };

  return (
    <>
      <Button onPress={onOpen}>Select MLB Records</Button>
      <Modal isOpen={isOpen} onOpenChange={onOpenChange} placement="center" size="3xl">
        <ModalContent>{onClose => (
          <>
            <ModalHeader>Search & Add Seasons</ModalHeader>
            <ModalBody className="max-h-[75vh] overflow-y-scroll">
              <SearchMLBPlayers
                setUnsavedPlayerSeasons={setUnsavedPlayerSeasons}
              />
            </ModalBody>
            <ModalFooter>
              <Button onPress={onClose} variant="light" color="danger">Cancel</Button>
              <Button onPress={() => {
                handleSave();
                onClose();
              }} color="primary" isDisabled={unsavedPlayerSeasons.length === 0}>
                Add Selected Players
              </Button>
            </ModalFooter>
          </>
        )}</ModalContent>
      </Modal>
    </>
  );
};

export default SearchMLBModal;