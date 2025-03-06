import { Button, Progress, Tooltip } from "@heroui/react";
import { useRouter } from "next/router";
import { useState } from "react";
import BuildController from "~/components/build/buildController";
import type { GetServerSidePropsContext } from "next";
import { createClient } from "utils/supabase/server-props";
import { api } from "~/utils/api";
import toast from "react-hot-toast";

type DisplayLineupPlayer = {
  id: string;
  name: string;
  isSelected: boolean;
  isUnassigned: boolean;
};

export default function Build() {
  const [loading, setLoading] = useState(false);
  const [lineup, setLineup] = useState<Record<number, DisplayLineupPlayer>>();

  const router = useRouter();

  const saveLineup = api.lineup.saveLineup.useMutation({
    onSuccess() {
      toast.dismiss();
      toast.success("Saved lineup!");
    },
    onError() {
      toast.dismiss();
      toast.error("Error...")
    }
  });

  const handleSubmit = async (lineup: Record<number, string | undefined>, unassignedPlayers: string[]) => {
    setLoading(true);

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
      } else {
        console.error("Failed to submit lineup");
      }
    } catch (error) {
      console.error("Error submitting lineup:", error);
    } finally {
      setLoading(false);
    }
  };

  const convertDisplayLineupToRaw = (
    displayLineup: Record<number, DisplayLineupPlayer>
  ): Record<string, string> => {
    return Object.fromEntries(
      Object.entries(displayLineup).map(([spot, player]) => [spot, player.id])
    );
  };

  const handleSave = async () => {
    if (!lineup) return;

    toast.dismiss();
    toast.loading("Saving lineup...");

    const selectedLineupForSaving = convertDisplayLineupToRaw(lineup);
    saveLineup.mutate({ selectedLineup: selectedLineupForSaving });
  };

  const renderPlayerDesignation = (player: { name: string; isSelected: boolean; isUnassigned: boolean }) => {
    if (player.isSelected) return (
      <div className="flex flex-row">{player.name} <Tooltip content="Player assigned to lineup position" placement="right">🔒</Tooltip></div>
    );
    if (player.isUnassigned) return (
      <div className="flex flex-row">{player.name} <Tooltip content="Player unassigned to lineup position" placement="right">🔓</Tooltip></div>
    );
    return <p className="text-red-500">{player.name}</p>;
  };

  return (
    <>
      <main className="flex min-h-screen flex-col items-center">
        {
          loading ? (
            <div className="flex flex-col gap-4 min-h-screen w-full items-center justify-center">
              <h2 className="text-xl">Creating lineup...</h2>
              <Progress isIndeterminate aria-label="Loading..." className="max-w-md" size="md" />
            </div>
          ) : (
            <>
              {
                lineup ? (
                  <div className="flex flex-col gap-12 items-center w-full h-full">
                    <h1 className="text-4xl font-bold text-center">Generated Lineup</h1>

                    {lineup ? (
                      <ul className="bg-gray-100 p-4 rounded-md mt-4">
                        {Object.entries(lineup).map(([spot, player]) => (
                          <li key={spot} className="text-lg flex flex-row gap-1">
                            <strong>Batting Spot {spot}:</strong> {renderPlayerDesignation(player)}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500 mt-4">No lineup found.</p>
                    )}

                    <div className="flex gap-6">
                      <Button onPress={() => router.reload()}>
                        Back
                      </Button>
                      <Button onPress={handleSave} color="primary">
                        Save
                      </Button>
                    </div>
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
