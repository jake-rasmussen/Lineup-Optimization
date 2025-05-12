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

  const handleSubmitMock = async (
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
              plateAppearances: playerSeason.season.plateAppearances,
              hits: playerSeason.season.hits,
              doubles: playerSeason.season.doubles,
              triples: playerSeason.season.triples,
              homeruns: playerSeason.season.homeruns,
              walks: playerSeason.season.walks,
              hitByPitch: playerSeason.season.hitByPitch,
              intentionalWalks: playerSeason.season.intentionalWalks,
              singles: playerSeason.season.singles,
              runs: playerSeason.season.runs,
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
              plateAppearances: playerSeason.season.plateAppearances,
              hits: playerSeason.season.hits,
              doubles: playerSeason.season.doubles,
              triples: playerSeason.season.triples,
              homeruns: playerSeason.season.homeruns,
              walks: playerSeason.season.walks,
              hitByPitch: playerSeason.season.hitByPitch,
              intentionalWalks: playerSeason.season.intentionalWalks,
              singles: playerSeason.season.singles,
              runs: playerSeason.season.runs,
            }
            : null,
        }));

      const response = await fetch("/api/submit-lineup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selectedLineup, unassignedPlayers }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Something went wrong!");
      }

      const data = await response.json();

      if (!data.lineup || !data.expectedRuns) {
        throw new Error("Invalid server response: missing lineup or expectedRuns");
      }

      setLineup(data.lineup);
      setExpectedRuns(data.expectedRuns);

      createJSON(lineupInput, unassignedPlayerSeasons, selectedPlayerSeasons); 
    } catch (error: any) {
      console.error("Error submitting lineup:", error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Used to get JSON object to run algorithm locally
  const createJSON = async (
    lineupInput: Record<number, string | undefined>,
    unassignedPlayerSeasons: PlayerSeason[],
    selectedPlayerSeasons: PlayerSeason[]
  ) => {
    setIsLoading(true);

    const json_input: Record<number, { name: string; data: any }> = {};

    // Fixed positions: keys 1–9.
    for (let pos = 1; pos <= 9; pos++) {
      const compositeId = lineupInput[pos];
      if (compositeId) {
        const ps = selectedPlayerSeasons.find((ps) => ps.compositeId === compositeId);
        if (ps) {
          const { player, season } = ps;
          json_input[pos] = {
            name: `${player.firstName} ${player.lastName}`,
            data: season
              ? {
                plateAppearances: season.plateAppearances,
                runs: season.runs,
                hits: season.hits,
                singles: season.singles,
                doubles: season.doubles,
                triples: season.triples,
                homeruns: season.homeruns,
                walks: season.walks,
                hitByPitch: season.hitByPitch,
                intentionalWalks: season.intentionalWalks,
              }
              : null,
          };
        } else {
          json_input[pos] = { name: "", data: null };
        }
      } else {
        json_input[pos] = { name: "", data: null };
      }
    }

    // Unassigned players: keys starting at 10.
    let key = 10;
    for (const ps of unassignedPlayerSeasons) {
      const { player, season } = ps;
      json_input[key] = {
        name: `${player.firstName} ${player.lastName}`,
        data: season
          ? {
            plateAppearances: season.plateAppearances,
            runs: season.runs,
            hits: season.hits,
            singles: season.singles,
            doubles: season.doubles,
            triples: season.triples,
            homeruns: season.homeruns,
            walks: season.walks,
            hitByPitch: season.hitByPitch,
            intentionalWalks: season.intentionalWalks,
          }
          : null,
      };
      key++;
    }

    const payload = {
      json_input,
      excel_file_path:
        "C:\\Users\\Jake Rasmussen\\Desktop\\Developer\\Lineup-Optimization\\web-server\\LO_Test.xlsx",
      method: "exhaustive",
      max_iterations: 1000,
    };

    console.log("PAYLOAD", payload);

    setIsLoading(false);
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
              <BuildController handleSubmit={handleSubmitMock} />
            </div>
          )}
        </>
      )}
    </main>
  );
}
