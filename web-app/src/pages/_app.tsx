import { GeistSans } from "geist/font/sans";
import { type AppType } from "next/app";

import { api } from "~/utils/api";

import "~/styles/globals.css";
import { HeroUIProvider } from "@heroui/react";
import { Poppins } from "@next/font/google";
import { createClient } from "utils/supabase/server-props";
import { GetServerSidePropsContext } from "next";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-poppins",
});

const MyApp: AppType = ({ Component, pageProps }) => {
  return (
    <HeroUIProvider>
      <div className={`${poppins.variable} font-sans`}>
        <style jsx global>{`
        :root {
          --font-poppins: ${poppins.style.fontFamily};
        }
      `}</style>
        <Component {...pageProps} />
      </div>
    </HeroUIProvider>
  );
};

export default api.withTRPC(MyApp);

