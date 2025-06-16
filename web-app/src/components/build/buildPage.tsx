import { Progress } from "@heroui/react";
import { useState } from "react";
import BuildController from "~/components/build/buildController";
import HomeRunAnimation from "~/components/homeRunAnimation";
import FinalLineup from "~/components/build/finalLineup";
import { DisplayLineupPlayer, PlayerSeason } from "~/data/types";

export default function BuildPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [lineup, setLineup] = useState<Record<number, DisplayLineupPlayer>>();
  const [expectedRuns, setExpectedRuns] = useState<number>();

  const handleSubmit = async (
    lineupInput: Record<number, string | undefined>, // batting spot -> compositeId
    unassignedPlayerSeasons: PlayerSeason[],
    selectedPlayerSeasons: PlayerSeason[]
  ) => {
    setIsLoading(true);

    try {
      const selectedLineup: Record<number, { name: string; data: any } | null> = {};

      const assignedCompositeIds = new Set(
        Object.values(lineupInput).filter((id): id is string => !!id)
      );

      // Assigned players
      for (const [spot, compositeId] of Object.entries(lineupInput)) {
        if (!compositeId) {
          selectedLineup[parseInt(spot)] = null;
          continue;
        }

        const playerSeason = selectedPlayerSeasons.find((p) => p.compositeId === compositeId);
        if (!playerSeason) {
          selectedLineup[parseInt(spot)] = null;
          continue;
        }

        selectedLineup[parseInt(spot)] = {
          name: `${playerSeason.player.firstName} ${playerSeason.player.lastName}`,
          data: playerSeason.season
            ? {
              pa: playerSeason.season.plateAppearances,
              h: playerSeason.season.hits,
              "2b": playerSeason.season.doubles,
              "3b": playerSeason.season.triples,
              hr: playerSeason.season.homeruns,
              bb: playerSeason.season.walks,
              hbp: playerSeason.season.hitByPitch,
              ibb: playerSeason.season.intentionalWalks,
              sb: 0,
            }
            : null,
        };
      }

      // Unassigned players
      const unassignedPlayers = unassignedPlayerSeasons
        .filter((ps) => !assignedCompositeIds.has(ps.compositeId))
        .map((playerSeason) => ({
          name: `${playerSeason.player.firstName} ${playerSeason.player.lastName}`,
          data: playerSeason.season
            ? {
              pa: playerSeason.season.plateAppearances,
              h: playerSeason.season.hits,
              "2b": playerSeason.season.doubles,
              "3b": playerSeason.season.triples,
              hr: playerSeason.season.homeruns,
              bb: playerSeason.season.walks,
              hbp: playerSeason.season.hitByPitch,
              ibb: playerSeason.season.intentionalWalks,
              sb: 0,
            }
            : null,
        }));

      const json_input = {
        ...selectedLineup,
        ...Object.fromEntries(unassignedPlayers.map((p, i) => [i + 10, p]))
      };

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/optimize-lineup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          json_input,
          method: "exhaustive",
          max_iterations: 1000
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Something went wrong!");
      }

      const data = await response.json();

      console.log("DATA", data);

      if (!data.lineup || !data.expectedRuns) {
        throw new Error("Invalid server response: missing lineup or expectedRuns");
      }

      const displayLineup: Record<number, DisplayLineupPlayer> = {};

      for (const [spotStr, name] of Object.entries(data.lineup)) {
        const spot = parseInt(spotStr);
        if (isNaN(spot)) continue;

        const match = selectedPlayerSeasons.find(
          (ps) => `${ps.player.firstName} ${ps.player.lastName}` === name
        );

        if (!match) continue;

        displayLineup[spot] = {
          id: match.compositeId,
          playerSeason: match,
          isSelected: true,
          isUnassigned: false,
        };
      }

      setLineup(displayLineup);
      setExpectedRuns(data.expectedRuns);
    } catch (error: any) {
      console.error("Error submitting lineup:", error.message);
    } finally {
      setTimeout(() => setIsLoading(false), 5000);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center w-full">
      {isLoading ? (
        <div className="flex flex-col gap-20 min-h-screen w-full items-center justify-center">
          <HomeRunAnimation />
          <div className="flex flex-col gap-4 w-full items-center">
            <Progress isIndeterminate aria-label="Loading..." className="max-w-md" size="md" />
            <h2 className="text-xl text-white">Creating lineup...</h2>
          </div>
        </div>
      ) : (
        <>
          {lineup ? (
            <div className="flex flex-col gap-12 items-center w-full min-h-screen justify-center">
              <FinalLineup lineup={lineup} expectedRuns={expectedRuns} />
            </div>
          ) : (
            <div className="flex w-full min-h-screen justify-center items-center">
              <BuildController handleSubmit={handleSubmit} />
            </div>
          )}
        </>
      )}
    </main>
  );
}
