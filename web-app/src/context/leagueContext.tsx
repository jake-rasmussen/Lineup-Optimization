import { createContext, useContext, useState, ReactNode } from "react";
import { League } from "~/data/types";

type LeagueContextType = {
  league: League;
  setLeague: (league: League) => void;
};

const LeagueContext = createContext<LeagueContextType | undefined>(undefined);

export const LeagueProvider = ({ children }: { children: ReactNode }) => {
  const [league, setLeague] = useState<League>(League.MLB); // default to MLB

  return (
    <LeagueContext.Provider value={{ league, setLeague }}>
      {children}
    </LeagueContext.Provider>
  );
};

export const useLeague = (): LeagueContextType => {
  const context = useContext(LeagueContext);
  if (!context) {
    throw new Error("useLeague must be used within a LeagueProvider");
  }
  return context;
};
