import { League } from "@prisma/client";
import type { GetServerSidePropsContext } from "next";
import { useEffect } from "react";
import { createClient } from "utils/supabase/server-props";
import BuildPage from "~/components/build/buildPage";
import { useLeague } from "~/context/leagueContext";

export default function Build() {
  const { setLeague } = useLeague();

  useEffect(() => {
    setLeague(League.ALPB);
  }, [setLeague]);

  return <BuildPage />
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
