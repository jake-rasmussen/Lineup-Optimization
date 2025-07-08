import { useEffect, useState } from "react";
import Head from "next/head";
import AuthModal from "~/components/auth/authModal";
import { Button, Progress } from "@heroui/react";
import Link from "next/link";
import { createClient } from "utils/supabase/component";
import { motion } from "framer-motion";
import RotatingTeamLogos from "~/aceternity-ui/infinite-moving-cards";

export default function Home() {
  const supabase = createClient();

  const [isLoading, setIsLoading] = useState<boolean>(true);
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

    fetchUser().then(() => setIsLoading(false));
  }, [supabase]);

  return (
    <>
      <Head>
        <title>Lineup Optimization</title>
        <meta name="description" content="Johns Hopkins Sports Analytics Group" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      {
        isLoading ? (
          <div className="flex flex-col gap-4 min-h-screen w-screen bg-black items-center justify-center">
            <h2 className="text-xl text-white">Welcome!</h2>
            <Progress isIndeterminate aria-label="Loading..." className="max-w-md" size="md" />
          </div>
        ) : (
          <div className="relative flex flex-col items-center justify-center max-w-screen min-h-screen bg-black w-screen overflow-hidden">
            <div className="absolute inset-y-0 left-0 h-full w-px bg-neutral-800/80">
              <div className="absolute top-0 h-40 w-px bg-gradient-to-b from-transparent via-blue-500 to-transparent" />
            </div>
            <div className="absolute inset-y-0 right-0 h-full w-px bg-neutral-800/80">
              <div className="absolute h-40 w-px bg-gradient-to-b from-transparent via-blue-500 to-transparent" />
            </div>
            <div className="absolute inset-x-0 bottom-0 h-px w-full bg-neutral-800/80">
              <div className="absolute mx-auto h-px w-40 bg-gradient-to-r from-transparent via-blue-500 to-transparent" />
            </div>
            <div className="px-4 py-10 md:py-20">
              <motion.div
                initial={{
                  opacity: 0,
                }}
                animate={{
                  opacity: 1,
                }}
                transition={{
                  duration: 0.3,
                  delay: 1,
                }}
                className="relative z-10 my-8 flex flex-wrap items-center justify-center gap-4"
              >
                <img src="/Field White.svg" alt="Field" style={{ width: "100%", height: "auto" }} className="max-w-40" />
              </motion.div>
              <h1 className="relative z-10 mx-auto max-w-xs sm:max-w-lg md:max-w-3xl text-center font-bold text-slate-300 text-xl sm:text-2xl md:text-4xl lg:text-7xl leading-tight">
                {"Ready to create your winning lineup?"
                  .split(" ")
                  .map((word, index) => (
                    <motion.span
                      key={index}
                      initial={{ opacity: 0, filter: "blur(4px)", y: 10 }}
                      animate={{ opacity: 1, filter: "blur(0px)", y: 0 }}
                      transition={{
                        duration: 0.3,
                        delay: index * 0.1,
                        ease: "easeInOut",
                      }}
                      className="mr-1 inline-block"
                    >
                      {word}
                    </motion.span>
                  ))}
              </h1>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.8 }}
                className="relative z-10 mx-auto mt-4 max-w-sm sm:max-w-md md:max-w-xl text-center text-base sm:text-lg text-neutral-400"
              >
                Creating the perfect baseball lineup is both an art and a science. Our lineup optimizer helps you select the best combination of
                players and arrange them in the most effective batting order. By using statistical insights and strategic placement, you can build a
                lineup that maximizes offensive potential and improves game performance.
              </motion.p>
              <motion.div
                initial={{
                  opacity: 0,
                }}
                animate={{
                  opacity: 1,
                }}
                transition={{
                  duration: 0.3,
                  delay: 1,
                }}
                className="relative z-10 mt-8 flex flex-wrap items-center justify-center gap-4"
              >
                {signedIn ? (
                  <Link href="/build">ƒ
                    <Button color="default" size="lg">
                      Build Your Lineup
                    </Button>
                  </Link>
                ) : (
                  <AuthModal />
                )}
              </motion.div>
              <motion.div
                initial={{
                  opacity: 0,
                  y: 10,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  duration: 0.3,
                  delay: 1.2,
                }}
                className="relative z-10 mt-20 rounded-3xl border p-4 shadow-md border-neutral-800 bg-neutral-900"
              >
                <div className="w-full rounded-xl border border-gray-700">
                  <RotatingTeamLogos />
                </div>
              </motion.div>
            </div>
          </div>
        )
      }

    </>
  );
}
