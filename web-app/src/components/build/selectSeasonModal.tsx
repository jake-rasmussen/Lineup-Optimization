import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Select,
  SelectItem,
  Spinner,
} from "@heroui/react";
import { useEffect, useState } from "react";
import { getSeasonSelectKey, formatSeasonLabel } from "~/utils/helper";
import type { Player, Season } from "@prisma/client";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  player: Player | null;
  onSeasonSelect: (season: Season) => void;
  getPlayerStats: (playerId: string) => Promise<Season[]>;
};

const SelectSeasonModal = ({ isOpen, onClose, player, onSeasonSelect, getPlayerStats }: Props) => {
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [selectedKey, setSelectedKey] = useState<string>();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!player || !isOpen) return;

    setLoading(true);
    getPlayerStats(player.id).then((stats) => {
      setSeasons(stats.filter((s) => s.league === "MLB" && s.teamId && s.teamId.length > 0));
    }).finally(() => {
      setLoading(false);
    });
  }, [player, isOpen]);

  const handleConfirm = () => {
    const season = seasons.find((s) => getSeasonSelectKey(s) === selectedKey);
    if (season) {
      onSeasonSelect(season);
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onOpenChange={onClose}>
      <ModalContent>
        {(onCloseModal) => (
          <>
            <ModalHeader>Select Season for {player?.fullName}</ModalHeader>
            <ModalBody>
              {loading ? (
                <Spinner />
              ) : (
                <Select
                  label="Select Season"
                  selectedKeys={selectedKey ? new Set([selectedKey]) : new Set()}
                  onSelectionChange={(keys) => setSelectedKey(Array.from(keys)[0] as string)}
                >
                  {seasons.map((season) => (
                    <SelectItem key={getSeasonSelectKey(season)} textValue={formatSeasonLabel(season)}>
                      {formatSeasonLabel(season)}
                    </SelectItem>
                  ))}
                </Select>
              )}
            </ModalBody>
            <ModalFooter>
              <Button variant="light" onPress={onCloseModal} color="danger">
                Cancel
              </Button>
              <Button color="primary" onPress={handleConfirm} isDisabled={!selectedKey}>
                Confirm
              </Button>
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
};

export default SelectSeasonModal;
