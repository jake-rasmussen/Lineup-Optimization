import { Progress } from "@heroui/react";
import type { GetServerSidePropsContext } from "next";
import { createClient } from "utils/supabase/server-props";
import { api } from "~/utils/api";
import SavedLineupCard from "~/components/saved/savedLineupCard";

export default function Saved() {
  const {
    data: savedLineups,
    isLoading,
  } = api.lineup.getLineups.useQuery();

  return (
    <main className="flex min-h-screen flex-col items-center py-16 px-4 w-full">
      {isLoading ? (
        <div className="flex flex-col gap-4 items-center justify-center h-full w-full max-w-md">
          <h2 className="text-xl font-medium text-white">Loading lineups...</h2>
          <Progress
            isIndeterminate
            aria-label="Loading..."
            className="w-full"
          />
        </div>
      ) : (
        <div className="flex flex-col items-center gap-12 w-full max-w-5xl">
          <h1 className="text-4xl font-bold text-center text-white">Saved Lineups</h1>

          {savedLineups && savedLineups.length > 0 ? (
            <div className="w-full flex flex-wrap justify-center gap-8">
              {savedLineups.map((lineup: any) => (
                <SavedLineupCard key={lineup.id} lineup={lineup} />
              ))}
            </div>
          ) : (
            <p className="text-lg text-gray-500">No saved lineups found.</p>
          )}
        </div>
      )}
    </main>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const supabase = createClient(context);
  const { data: { user }, error } = await supabase.auth.getUser();

  if (error || !user) {
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }

  return {
    props: {
      user,
    },
  };
}
