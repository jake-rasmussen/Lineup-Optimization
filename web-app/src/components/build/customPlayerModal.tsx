import {
  Button,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  useDisclosure,
  NumberInput,
  Input,
  Select,
  SelectItem,
  Divider
} from "@heroui/react";
import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { formatBattingHand, formatPosition } from "~/utils/helper";
import { PlayerSeason, Position, BattingHand, Player, League, Season } from "~/data/types";
import toast from "react-hot-toast";

type Props = {
  setSelectedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};

type SeasonInput = {
  year?: number;
  plateAppearances?: number;
  runs?: number;
  hits?: number;
  singles?: number;
  doubles?: number;
  triples?: number;
  homeruns?: number;
  walks?: number;
  hitByPitch?: number;
  intentionalWalks?: number;
};

const initialSeasonState: SeasonInput = {
  year: undefined,
  plateAppearances: undefined,
  runs: undefined,
  hits: undefined,
  singles: undefined,
  doubles: undefined,
  triples: undefined,
  homeruns: undefined,
  walks: undefined,
  hitByPitch: undefined,
  intentionalWalks: undefined,
};

const CustomPlayerModal = ({ setSelectedPlayerSeasons }: Props) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [season, setSeason] = useState<SeasonInput>(initialSeasonState);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [position, setPosition] = useState<Position | undefined>(undefined);
  const [battingHand, setBattingHand] = useState<BattingHand | undefined>(undefined);

  const handleChange = (field: keyof SeasonInput, value: any) => {
    const num = Number(value);
    setSeason((prev) => ({ ...prev, [field]: isNaN(num) ? undefined : num }));
  };

  const handleSave = () => {
    const id = `custom-${Date.now()}`;
    const player = {
      id,
      fullName: firstName + " " + lastName,
      position: position!,
      battingHand: battingHand!,
    };

    const playerSeason: PlayerSeason = {
      compositeId: `${firstName} ${lastName} - custom`,
      player: player as Player,
      season: {
        id: `season-${id}`,
        year: season.year ?? 2024,
        plateAppearances: season.plateAppearances ?? 0,
        runs: season.runs ?? 0,
        hits:
          (season.singles ?? 0) +
          (season.doubles ?? 0) +
          (season.triples ?? 0) +
          (season.homeruns ?? 0),
        singles: season.singles ?? 0,
        doubles: season.doubles ?? 0,
        triples: season.triples ?? 0,
        homeruns: season.homeruns ?? 0,
        walks: season.walks ?? 0,
        hitByPitch: season.hitByPitch ?? 0,
        intentionalWalks: season.intentionalWalks ?? 0,
        playerId: id,
        league: League.CUSTOM,
      } as Season,
      isCustom: true,
    };

    if (season && season.plateAppearances && season.plateAppearances < 100) {
      toast((
        <div>
          <strong className="block font-semibold text-yellow-500">Low Sample Size</strong>
          <div className="mt-1 text-sm">
            This player has fewer than 100 plate appearances. Results may be less accurate.
          </div>
        </div>
      ), {
        duration: 7500
      });
    }

    setSelectedPlayerSeasons((prev) => [...prev, playerSeason]);
  };

  return (
    <>
      <Button onPress={onOpen} color="primary">Create Custom Player</Button>

      <Modal isOpen={isOpen} onOpenChange={onOpenChange} placement="center" size="3xl">
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader>Enter Player Season Stats</ModalHeader>
              <ModalBody className="flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input label="First Name" value={firstName} onValueChange={setFirstName} />
                  <Input label="Last Name" value={lastName} onValueChange={setLastName} />

                  <Select
                    label="Position"
                    selectedKeys={position ? new Set([position]) : new Set()}
                    onSelectionChange={(keys) => setPosition(Array.from(keys)[0] as Position)}
                  >
                    {Object.values(Position).map((position) => (
                      <SelectItem key={position}>{formatPosition(position)}</SelectItem>
                    ))}
                  </Select>

                  <Select
                    label="Batting Hand"
                    selectedKeys={battingHand ? new Set([battingHand]) : new Set()}
                    onSelectionChange={(keys) => setBattingHand(Array.from(keys)[0] as BattingHand)}
                  >
                    {Object.values(BattingHand).map((battingHand) => (
                      <SelectItem key={battingHand}>{formatBattingHand(battingHand)}</SelectItem>
                    ))}
                  </Select>
                </div>


                <Divider className="w-full" />

                <div className="grid grid-cols-2 gap-4">
                  <NumberInput
                    label="Plate Appearances"
                    value={season.plateAppearances}
                    onChange={(val) => handleChange("plateAppearances", val)}
                    minValue={0}
                    maxValue={800}
                  />
                  <NumberInput
                    label="Runs"
                    value={season.runs}
                    onChange={(val) => handleChange("runs", val)}
                    minValue={0}
                    maxValue={200}
                  />
                  <NumberInput
                    label="Singles"
                    value={season.singles}
                    onChange={(val) => handleChange("singles", val)}
                    minValue={0}
                    maxValue={300}
                  />
                  <NumberInput
                    label="Doubles"
                    value={season.doubles}
                    onChange={(val) => handleChange("doubles", val)}
                    minValue={0}
                    maxValue={100}
                  />
                  <NumberInput
                    label="Triples"
                    value={season.triples}
                    onChange={(val) => handleChange("triples", val)}
                    minValue={0}
                    maxValue={30}
                  />
                  <NumberInput
                    label="Homeruns"
                    value={season.homeruns}
                    onChange={(val) => handleChange("homeruns", val)}
                    minValue={0}
                    maxValue={80}
                  />
                  <NumberInput
                    label="Unintentional Bases on Balls"
                    value={season.walks}
                    onChange={(val) => handleChange("walks", val)}
                    minValue={0}
                    maxValue={200}
                  />
                  <NumberInput
                    label="Intentional Bases on Balls"
                    value={season.intentionalWalks}
                    onChange={(val) => handleChange("intentionalWalks", val)}
                    minValue={0}
                    maxValue={60}
                  />
                </div>
              </ModalBody>
              <ModalFooter>
                <Button onPress={onClose} variant="light" color="danger">Cancel</Button>
                <Button
                  color="primary"
                  onPress={() => {
                    handleSave();
                    onClose();
                  }}
                  isDisabled={!firstName || !lastName || !position || !battingHand}
                >
                  Submit
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
};

export default CustomPlayerModal;
