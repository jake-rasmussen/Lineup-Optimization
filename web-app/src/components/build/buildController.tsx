import { Button, Card, CardBody, CardFooter, CardHeader } from "@heroui/react";
import { useState } from "react";
import AssignLineup from "./assignLineup";
import ConfirmLineup from "./confirmLineup";
import { Player, Season } from "@prisma/client";
import SelectPlayers from "./selectPlayers";

export type PlayerSeason = {
  compositeId: string;
  player: Player;
  season: Season;
}

type PropType = {
  handleSubmit: (
    lineup: Record<number, string | undefined>,
    unassignedPlayerSeasons: PlayerSeason[],
    selectedPlayerSeasons: PlayerSeason[]
  ) => void;
};

const BuildController = ({ handleSubmit }: PropType) => {
  const [step, setStep] = useState(0);
  const [selectedPlayerSeasons, setSelectedPlayerSeasons] = useState<PlayerSeason[]>([]);
  
  const [lineup, setLineup] = useState<Record<number, string | undefined>>(
    Object.fromEntries(Array.from({ length: 9 }, (_, i) => [i + 1, undefined]))
  );

  const nextStep = () => {
    if (step === 0 && selectedPlayerSeasons.length > 9) {
      return;
    } else if (step === 0 && selectedPlayerSeasons.length === 0) {
      setStep((prev) => prev + 2);
    } else {
      setStep((prev) => prev + 1);
    }
  };

  const prevStep = () => setStep((prev) => prev - 1);

  // Determine which composite IDs are assigned in the lineup.
  const assignedComposite = new Set(Object.values(lineup).filter(Boolean));
  // Get unassigned player seasons (those not in the lineup).
  const unassignedPlayerSeasons = selectedPlayerSeasons.filter(
    (ps) => !assignedComposite.has(ps.compositeId)
  );

  return (
    <Card className="h-[75vh] w-full max-w-5xl shadow-blue-200 shadow-xl border">
      {step === 0 && (
        <CardHeader>
          <div>
            <h3>Select Players</h3>
            <p className="text-gray-500 font-normal text-sm">
              Use the dropdown and search bar below to pick players based on team, year and name.
            </p>
          </div>
        </CardHeader>
      )}
      {step === 1 && (
        <CardHeader>
          <div>
            <h3>Arrange Batting Order</h3>
            <p className="text-gray-500 font-normal text-sm">
              Place your selected players in the desired batting order.
            </p>
          </div>
        </CardHeader>
      )}
      {step === 2 && (
        <CardHeader>
          <div>
            <h3>Review & Submit</h3>
            <p className="text-gray-500 font-normal text-sm">
              Review your lineup and click submit when ready.
            </p>
          </div>
        </CardHeader>
      )}
      <CardBody className="max-h-[70vh] overflow-y-scroll">
        {step === 0 && (
          <SelectPlayers
            selectedPlayerSeasons={selectedPlayerSeasons}
            setSelectedPlayerSeasons={setSelectedPlayerSeasons}
          />
        )}

        {step === 1 && (
          <AssignLineup
            lineup={lineup}
            setLineup={setLineup}
            selectedPlayerSeasons={selectedPlayerSeasons}
          />
        )}

        {step === 2 && (
          <ConfirmLineup
            lineup={lineup}
            selectedPlayerSeasons={selectedPlayerSeasons}
            unassignedPlayers={unassignedPlayerSeasons.map(ps => ps.compositeId)}
          />
        )}
      </CardBody>
      <CardFooter className="flex flex-row gap-2">
        <Button
          color="danger"
          variant="light"
          onPress={step === 0 ? undefined : prevStep}
          isDisabled={step === 0}
        >
          Back
        </Button>
        {step < 2 && (
          <Button color="primary" onPress={nextStep}>
            Next
          </Button>
        )}
        {step === 2 && (
          <Button
            onPress={() =>
              handleSubmit(lineup, unassignedPlayerSeasons, selectedPlayerSeasons)
            }
            color="primary"
          >
            Submit
          </Button>
        )}
      </CardFooter>
    </Card>
  );
};

export default BuildController;
