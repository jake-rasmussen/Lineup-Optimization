import { Progress } from "@heroui/react";
import { useState } from "react";
import BuildController from "~/components/build/buildController";
import type { GetServerSidePropsContext } from "next";
import { createClient } from "utils/supabase/server-props";
import { Player } from "@prisma/client";
import HomeRunAnimation from "~/components/homeRunAnimation";
import FinalLineup from "~/components/build/finalLineup";

export type DisplayLineupPlayer = {
  player: Player
  isSelected: boolean;
  isUnassigned: boolean;
};

export default function Build() {
  const [isLoading, setIsLoading] = useState(false);
  const [lineup, setLineup] = useState<Record<number, DisplayLineupPlayer>>();
  const [expectedRuns, setExpectedRuns] = useState<number>();

  const handleSubmit = async (lineup: Record<number, string | undefined>, unassignedPlayers: string[]) => {
    setIsLoading(true);

    const selectedLineup = Object.fromEntries(
      Object.entries(lineup).map(([spot, player]) => [spot, player ?? null])
    );

    try {
      const response = await fetch("/api/submit-lineup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selectedLineup, unassignedPlayers }),
      });

      if (response.ok) {
        const data = await response.json();
        setLineup(data.lineup);
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
    <>
      <main className="flex min-h-screen flex-col items-center">
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
                    <h1 className="text-4xl font-bold text-center">Generated Lineup</h1>
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
    </>
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
    }
  }

  return {
    props: {
      user: data.user,
    },
  }
}
