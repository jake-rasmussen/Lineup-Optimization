"use client";

import { RadioGroup, Radio, cn, Spinner } from "@heroui/react";
import { Dispatch, SetStateAction, useState } from "react";
import { api } from "~/utils/api";
import { PlayerSeason, Season } from "~/data/types";
import { getPlayerSeasonCompositeId } from "~/utils/helper";

type PitcherHandednessOption = "LEFT" | "RIGHT" | null;

export const CustomRadio = (props: any) => {
  const { children, ...otherProps } = props;

  return (
    <Radio
      {...otherProps}
      classNames={{
        base: cn(
          "inline-flex m-0 bg-content1 hover:bg-content2 items-center justify-between",
          "flex-row-reverse cursor-pointer rounded-lg gap-4 p-4 border-2 border-transparent",
          "data-[selected=true]:border-primary"
        ),
      }}
    >
      {children}
    </Radio>
  );
};

type PropType = {
  pitcherHandedness: PitcherHandednessOption;
  setPitcherHandedness: Dispatch<SetStateAction<PitcherHandednessOption>>;
  selectedPlayerSeasons: PlayerSeason[];
  setSelectedPlayerSeasons: Dispatch<SetStateAction<PlayerSeason[]>>;
};

const SelectPitcherHandedness = ({
  pitcherHandedness,
  setPitcherHandedness,
  selectedPlayerSeasons,
  setSelectedPlayerSeasons,
}: PropType) => {
  const [isLoading, setIsLoading] = useState(false);
  const { mutateAsync: getPlayerSplitStats } = api.mlb.getPlayerSplitStats.useMutation();

  const handleHandednessChange = async (handedness: PitcherHandednessOption) => {
    setPitcherHandedness(handedness);
    const oldPlayerseasons = selectedPlayerSeasons;

    setSelectedPlayerSeasons([]);
    setIsLoading(true);

    try {
      const updatedSeasons: PlayerSeason[] = await Promise.all(
        selectedPlayerSeasons.map(async (ps): Promise<PlayerSeason> => {
          const { player, season } = ps;
          if (!season) return ps;

          const { vsLeft, vsRight, overall } = await getPlayerSplitStats({
            playerId: player.id,
            seasonYear: season.year!,
          });
          const splitStats = handedness === "LEFT"
            ? vsLeft
            : handedness === "RIGHT"
              ? vsRight
              : overall;

          if (!splitStats) return ps;

          const selectedSplitSeason: Season = {
            ...season,
            ...splitStats,
          };

          return {
            ...ps,
            season: selectedSplitSeason,
            compositeId: getPlayerSeasonCompositeId(player, selectedSplitSeason),
          };
        })
      );

      console.log(updatedSeasons)
      setSelectedPlayerSeasons(updatedSeasons);
    } catch (err) {
      setSelectedPlayerSeasons(oldPlayerseasons)
      console.error("Failed to update splits", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full h-full">
      {isLoading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-lg h-full">
          <Spinner size="lg" color="primary" />
        </div>
      )}

      <div className="flex flex-col items-start w-full gap-6">
        <div className="space-y-1">
          <p className="text-sm text-gray-500">
            Simulate matchup-based stats by selecting the pitcher’s handedness. This will use each player’s split stats vs. left- or right-handed pitchers. If “No Constraint” is selected, full-season (combined) stats will be used instead.
          </p>
        </div>

        <RadioGroup
          label={<p className="text-black">Pitcher Handedness</p>}
          value={pitcherHandedness ?? "NONE"}
          onValueChange={(val) => {
            const newVal = val === "NONE" ? null : (val as PitcherHandednessOption);
            handleHandednessChange(newVal);
          }}
        >
          <CustomRadio description="Use player stats vs. left-handed pitchers" value="LEFT">
            Left-Handed Pitcher
          </CustomRadio>
          <CustomRadio description="Use player stats vs. right-handed pitchers" value="RIGHT">
            Right-Handed Pitcher
          </CustomRadio>
          <CustomRadio description="Use full-season stats with no split applied" value="NONE">
            No Constraint
          </CustomRadio>
        </RadioGroup>
      </div>
    </div>
  );
};

export default SelectPitcherHandedness;
