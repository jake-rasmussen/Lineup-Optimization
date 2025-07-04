import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, useDisclosure } from "@heroui/react";
import PlayerCard from "./playerCard";
import { Player } from "@prisma/client";

type PropType = {
  player: Player;
  isDisabled?: boolean;
}

const PlayerCardModal = ({ player, isDisabled }: PropType) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  return (
    <>
      <Button onPress={onOpen} size="sm" isDisabled={isDisabled}>View Player</Button>

      <Modal isOpen={isOpen} onOpenChange={onOpenChange} placement="center" size="3xl">
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader>
                {player.fullName}
              </ModalHeader>
              <ModalBody>
                <PlayerCard
                  player={player}
                  onClose={onClose}
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
    </>

  )
}

export default PlayerCardModal;