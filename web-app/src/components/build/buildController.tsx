"use client";

import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
} from "@heroui/react";
import { useEffect, useMemo, useState } from "react";
import AssignLineup from "./assignLineup";
import ConfirmLineup from "./confirmLineup";
import SelectPlayersMLB from "./selectPlayers";
import SelectPlayersALPB from "./alpb/selectPlayers";
import { PlayerSeason } from "~/data/types";
import { League } from "@prisma/client";
import { useLeague } from "~/context/leagueContext";
import toast from "react-hot-toast";

type PropType = {
  handleSubmit: (
    lineup: Record<number, string | undefined>,
    unassignedPlayerSeasons: PlayerSeason[],
    selectedPlayerSeasons: PlayerSeason[],
    maxConsecutiveHandedness: [number, number]
  ) => void;
};

const BuildController = ({ handleSubmit }: PropType) => {
  const [step, setStep] = useState(0);
  const [selectedPlayerSeasons, setSelectedPlayerSeasons] = useState<PlayerSeason[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  const [lineup, setLineup] = useState<Record<number, string | undefined>>(
    Object.fromEntries(Array.from({ length: 9 }, (_, i) => [i + 1, undefined]))
  );
  const [maxConsecutiveHandedness, setMaxConsecutiveHandedness] = useState<[number, number]>([0, 0]);

  const { league } = useLeague();

  useEffect(() => {
    try {
      const stored = localStorage.getItem("selectedPlayerSeasons");
      if (stored) {
        setSelectedPlayerSeasons(JSON.parse(stored));
      }
    } catch { } finally {
      setIsLoaded(true);
    }
  }, []);

  useEffect(() => {
    try {
      if (isLoaded) {
        localStorage.setItem("selectedPlayerSeasons", JSON.stringify(selectedPlayerSeasons));
      }
    } catch { }
  }, [selectedPlayerSeasons]);

  const isConstraintImpossible = useMemo(() => {
    if (step !== 1) return false;

    const hands = selectedPlayerSeasons
      .map((ps) => ps.player?.battingHand)
      .filter((h): h is "LEFT" | "RIGHT" => h === "LEFT" || h === "RIGHT");

    if (hands.length !== 9) return false;

    const dfs = (
      remaining: string[],
      last: string | null,
      leftStreak: number,
      rightStreak: number
    ): boolean => {
      if (remaining.length === 0) return true;

      for (let i = 0; i < remaining.length; i++) {
        const hand = remaining[i];
        const rest = [...remaining.slice(0, i), ...remaining.slice(i + 1)];

        if (hand === "LEFT") {
          if (last === "LEFT" && leftStreak + 1 > maxConsecutiveHandedness[0]) continue;
          if (dfs(rest, "LEFT", last === "LEFT" ? leftStreak + 1 : 1, 0)) return true;
        } else if (hand === "RIGHT") {
          if (last === "RIGHT" && rightStreak + 1 > maxConsecutiveHandedness[1]) continue;
          if (dfs(rest, "RIGHT", 0, last === "RIGHT" ? rightStreak + 1 : 1)) return true;
        }
      }

      return false;
    };

    const canSatisfy = dfs(hands, null, 0, 0);
    return !canSatisfy;
  }, [step, selectedPlayerSeasons, maxConsecutiveHandedness]);

  useEffect(() => {
    if (step === 1 && isConstraintImpossible) {
      toast.error("Impossible handedness constraint");
    }
  }, [step, isConstraintImpossible]);

  const nextStep = () => {
    if (selectedPlayerSeasons.length !== 9) {
      toast.error("Please select 9 players");
      return;
    }
    setStep((prev) => prev + 1);
  };

  const prevStep = () => setStep((prev) => prev - 1);

  const assignedPlayerIds = new Set(
    Object.values(lineup).filter((id): id is string => typeof id === "string")
  );
  const unassignedPlayerIds = selectedPlayerSeasons.filter(
    (selectedPlayerSeason) => !assignedPlayerIds.has(selectedPlayerSeason.compositeId)
  );

  if (!isLoaded) return null;

  return (
    <Card className="h-[90vh] w-full p-4 max-w-7xl shadow-blue-200 shadow-xl border">
      {step === 0 && (
        <CardHeader>
          <div>
            <h3>Select Players</h3>
            <p className="text-gray-500 font-normal text-sm">
              Use the dropdown and search bar below to pick players based on team, year and name.
              Please select 9 player's season.
            </p>
          </div>
        </CardHeader>
      )}
      {step === 1 && (
        <CardHeader>
          <div>
            <h3>Add Constraints</h3>
            <p className="text-gray-500 font-normal text-sm">
              Place handedness constraints to control lineup flow.
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
      <Divider />
      <CardBody className="max-h-[70vh] overflow-y-scroll flex items-center">
        {step === 0 && (
          <>
            {league === League.MLB ? (
              <SelectPlayersMLB
                selectedPlayerSeasons={selectedPlayerSeasons}
                setSelectedPlayerSeasons={setSelectedPlayerSeasons}
              />
            ) : (
              <SelectPlayersALPB
                selectedPlayerSeasons={selectedPlayerSeasons}
                setSelectedPlayerSeasons={setSelectedPlayerSeasons}
              />
            )}
          </>
        )}

        {step === 1 && (
          <AssignLineup
            lineup={lineup}
            setLineup={setLineup}
            maxConsecutiveHandedness={maxConsecutiveHandedness}
            setMaxConsecutiveHandedness={setMaxConsecutiveHandedness}
            selectedPlayerSeasons={selectedPlayerSeasons}
          />
        )}

        {step === 2 && (
          <ConfirmLineup
            lineup={lineup}
            selectedPlayerSeasons={selectedPlayerSeasons}
            unassignedPlayers={unassignedPlayerIds.map((entry) => `${entry.player.fullName}`)}
          />
        )}
      </CardBody>
      <Divider />
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
          <Button
            color="primary"
            onPress={nextStep}
            isDisabled={
              selectedPlayerSeasons.length !== 9 ||
              selectedPlayerSeasons.some((ps) => !ps.season) ||
              isConstraintImpossible
            }
          >
            Next
          </Button>
        )}
        {step === 2 && (
          <Button
            onPress={() => {
              handleSubmit(lineup, unassignedPlayerIds, selectedPlayerSeasons, maxConsecutiveHandedness);
            }}
            color="primary"
          >
            Submit
          </Button>
        )}

        {step === 0 && selectedPlayerSeasons.length > 0 && (
          <div className="grow flex justify-end items-center">
            {`Selected Players: ${selectedPlayerSeasons.length}/9`}
          </div>
        )}
      </CardFooter>
    </Card>
  );
};

export default BuildController;
