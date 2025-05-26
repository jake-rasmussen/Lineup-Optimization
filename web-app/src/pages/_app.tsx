import { type AppType } from "next/app";

import { api } from "~/utils/api";

import "~/styles/globals.css";
import { HeroUIProvider } from "@heroui/react";
import { Poppins } from "next/font/google";
import { Toaster } from "react-hot-toast";
import NavDrawer from "~/components/navDrawer";
import { LeagueProvider } from "~/context/leagueContext";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-poppins",
});

const MyApp: AppType = ({ Component, pageProps }) => {
  return (
    <HeroUIProvider>
      <LeagueProvider>
        <div className={`${poppins.variable} font-sans flex w-full bg-black`}>
          <style jsx global>{`
        :root {
          --font-poppins: ${poppins.style.fontFamily};
        }
      `}</style>
          <Toaster />
          <NavDrawer />
          <Component {...pageProps} />
        </div>
      </LeagueProvider>
    </HeroUIProvider>
  );
};

export default api.withTRPC(MyApp);

