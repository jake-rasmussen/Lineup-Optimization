import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, useDisclosure } from "@heroui/react";
import PlayerCard from "./playerCard";
import { Player, Season } from "@prisma/client";

type PropType = {
  player: Player;
}

const PlayerCardModal = ({ player }: PropType) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  return (
    <>
      <Button onPress={onOpen} size="sm">View Player</Button>
    
      <Modal isOpen={isOpen} onOpenChange={onOpenChange} placement="center">
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader>
                {player.firstName} {player.lastName}
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