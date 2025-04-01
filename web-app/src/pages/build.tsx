import { Progress } from "@heroui/react";
import { useState } from "react";
import BuildController, { PlayerSeason } from "~/components/build/buildController";
import type { GetServerSidePropsContext } from "next";
import { createClient } from "utils/supabase/server-props";
import HomeRunAnimation from "~/components/homeRunAnimation";
import FinalLineup from "~/components/build/finalLineup";

export type DisplayLineupPlayer = {
  id: string,
  playerName: string,
  isSelected: boolean;
  isUnassigned: boolean;
};

export default function Build() {
  const [isLoading, setIsLoading] = useState(false);
  const [lineup, setLineup] = useState<Record<number, DisplayLineupPlayer>>();
  const [expectedRuns, setExpectedRuns] = useState<number>();

  const handleSubmit = async (
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
                pa: season.plateAppearances,
                h: season.hits,
                "2b": season.doubles,
                "3b": season.triples,
                hr: season.homeruns,
                sb: 0, // Stolen bases not in schema; default to 0
                bb: season.walks,
                hbp: season.hitByPitch,
                ibb: season.intentionalWalks,
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
            pa: season.plateAppearances,
            h: season.hits,
            "2b": season.doubles,
            "3b": season.triples,
            hr: season.homeruns,
            sb: 0,
            bb: season.walks,
            hbp: season.hitByPitch,
            ibb: season.intentionalWalks,
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

    console.log("Submitting payload:", payload);

    try {
      const response = await fetch("http://127.0.0.1:8000/optimize-lineup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      console.log("Response:", response);

      if (response.ok) {
        const data = await response.json();
        const lineupObj: Record<number, DisplayLineupPlayer> = {};
        for (let pos = 1; pos <= 9; pos++) {
          const playerName = data[pos.toString()];
          lineupObj[pos] = {
            id: playerName,
            playerName,
            isSelected: false,
            isUnassigned: false,
          };
        }
        console.log("Formatted lineup:", lineupObj);

        setLineup(lineupObj);
        setExpectedRuns(data.expectedRuns);
      } else {
        console.error("Failed to submit lineup");
      }
    } catch (error) {
      console.error("Error submitting lineup:", error);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <main className="flex min-h-screen flex-col items-center w-full">
      {
        isLoading ? (
          <div className="flex flex-col gap-20 min-h-screen w-full items-center justify-center">
            <HomeRunAnimation />
            <div className="flex flex-col gap-4 w-full items-center">
              <Progress isIndeterminate aria-label="Loading..." className="max-w-md" size="md" />
              <h2 className="text-xl">Creating lineup...</h2>
            </div>
          </div>
        ) : (
          <>
            {
              lineup ? (
                <div className="flex flex-col gap-12 items-center w-full min-h-screen justify-center w-full">
                  <FinalLineup lineup={lineup} expectedRuns={expectedRuns} />
                </div>
              ) : (
                <div className="flex w-full min-h-screen justify-center items-center">
                  <BuildController handleSubmit={handleSubmit} />
                </div>
              )
            }
          </>
        )}
    </main>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const supabase = createClient(context);

  const { data, error } = await supabase.auth.getUser();

  if (error || !data) {
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }

  return {
    props: {
      user: data.user,
    },
  };
}
