import { Progress } from "@heroui/react";
import type { GetServerSidePropsContext } from "next";
import { createClient } from "utils/supabase/server-props";
import { api } from "~/utils/api";
import SavedLineupCard, { SavedLineup } from "~/components/saved/lineupCard";

export default function Saved() {
  const {
    data: savedLineups,
    isLoading,
  } = api.lineup.getSavedLineups.useQuery();

  return (
    <>
      <main className="flex min-h-screen flex-col items-center">
        {isLoading ? (
          <div className="flex flex-col gap-4 min-h-screen w-full items-center justify-center">
            <h2 className="text-xl">Loading lineups...</h2>
            <Progress
              isIndeterminate
              aria-label="Loading..."
              className="max-w-md"
              size="md"
            />
          </div>
        ) : (
          <div className="flex flex-col gap-12 px-4 py-16 items-center w-full">
            {savedLineups && savedLineups.length > 0 ? (
              savedLineups.map((lineup: SavedLineup) => (
                <SavedLineupCard
                  key={lineup.id}
                  lineup={lineup}
                />
              ))
            ) : (
              <p>No saved lineups found.</p>
            )}
          </div>
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
    };
  }

  return {
    props: {
      user: data.user,
    },
  };
}
