export type HittingTotalStats = {
  ab: number;    // At bats
  runs: number;  // Runs scored
  s: number;     // Singles
  d: number;     // Doubles
  t: number;     // Triples
  hr: number;    // Home runs
  rbi: number;   // Runs batted in
  bb: number;    // Walks (Base on Balls)
  ibb: number;   // Intentional walks
  hbp: number;   // Hit by pitch
  sb: number;    // Stolen bases
  cs: number;    // Caught stealing
  obp: number;   // On-base percentage
  slg: number;   // Slugging percentage
  ops: number;   // On-base plus slugging
  h: number;     // Hits
  ktotal: number;// Total strikeouts
  avg: string;   // Batting average as a string (e.g., ".189")
}

export type Player = {
  preferred_name: string;
  first_name: string;
  last_name: string;
  jersey_number: string;
  id: string;
  full_name: string;
  position: string;
  primary_position: string;
  splits: {
    hitting: {
      overall: [{
        total: [HittingTotalStats]
      }];
    }
  }
}

export type Split = {
  player: {
    id: string;
    full_name?: string;
    [key: string]: any;
  };
  [key: string]: any;
}

export type TeamSplitsResponse = {
  splits: Split[];
  [key: string]: any;
}

export type PlayerProfileResponse = {
  bat_hand: string;
  jersey_number?: string;
  salary?: number;
  birthdate?: Date;
}