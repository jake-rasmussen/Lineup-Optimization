import { useEffect, useState } from "react";
import Head from "next/head";
import AuthModal from "~/components/auth/authModal";
import { Button, Progress } from "@heroui/react";
import Link from "next/link";
import { createClient } from "utils/supabase/component";

export default function Home() {
  const supabase = createClient();

  const [loading, setLoading] = useState<boolean>(true);
  const [signedIn, setSignedIn] = useState<boolean>(false);

  useEffect(() => {
    async function fetchUser() {
      const { data, error } = await supabase.auth.getSession();

      if (!error) {
        setSignedIn(data.session !== null);
      } else {
        console.error("Error fetching user:", error);
      }
    }

    fetchUser().then(() => setLoading(false));
  }, [supabase]);

  return (
    <>
      <Head>
        <title>Lineup Optimization</title>
        <meta name="description" content="Johns Hopkins Sports Analytics Group" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      {
        loading ? (
          <div className="flex flex-col gap-4 min-h-screen w-full items-center justify-center">
            <h2 className="text-xl">Welcome!</h2>
            <Progress isIndeterminate aria-label="Loading..." className="max-w-md" size="md" />
          </div>
        ) : (
          <main className="flex min-h-screen flex-col items-center justify-center">
            <div className="flex flex-col items-center justify-center gap-12 px-4 py-16">
              <h1 className="text-5xl font-extrabold tracking-tight text-black sm:text-[5rem]">
                Lineup <span className="text-red-500">Optimization</span>
              </h1>
              <p className="text-lg text-center max-w-2xl text-gray-700">
                Creating the perfect baseball lineup is both an art and a science. Our lineup optimizer helps you select the best combination of players and arrange them in the most effective batting order. By using statistical insights and strategic placement, you can build a lineup that maximizes offensive potential and improves game performance.
              </p>
              <p className="text-lg text-center max-w-2xl text-gray-700">
                Ready to create your winning lineup? Click the button below to get started.
              </p>

              {signedIn ? (
                <Button color="primary">
                  <Link href="/build">
                    Get Started
                  </Link>
                </Button>
              ) : (
                <AuthModal />
              )}
            </div>
          </main>
        )
      }

    </>
  );
}
