// Enums (mirroring your Prisma schema)
export enum Position {
  PITCHER = "PITCHER",
  CATCHER = "CATCHER",
  FIRST_BASE = "FIRST_BASE",
  SECOND_BASE = "SECOND_BASE",
  THIRD_BASE = "THIRD_BASE",
  LEFT_FIELD = "LEFT_FIELD",
  CENTER_FIELD = "CENTER_FIELD",
  RIGHT_FIELD = "RIGHT_FIELD",
  SHORTSTOP = "SHORTSTOP",
  DESIGNATED_HITTER = "DESIGNATED_HITTER",
}

export enum BattingHand {
  LEFT = "LEFT",
  RIGHT = "RIGHT",
  SWITCH = "SWITCH",
}

export enum League {
  MLB = "MLB",
  ALPB = "ALPB",
  AAA = "AAA",
  AA = "AA",
  A = "A",
  CUSTOM = "CUSTOM",
}

// Player type (matching your Prisma model)
export type Player = {
  id: string;
  fullName: string;
  position: Position;
  seasons: Season[];
  battingHand: BattingHand;
  jerseyNumber?: number | null;
  salary?: number | null;
  birthday?: Date | null;
};

// Season type (matching your Prisma model)
export type Season = {
  id: string;
  year?: number | null;
  plateAppearances: number;
  runs: number;
  hits: number;
  singles: number;
  doubles: number;
  triples: number;
  homeruns: number;
  walks: number;
  hitByPitch: number;
  intentionalWalks: number;
  player?: Player | null;
  playerId?: string | null;
  teamId?: string | null;
  teamName: string;
  league: League;
};

// PlayerSeason type used for composite player-season logic
export type PlayerSeason = {
  compositeId: string;
  player: Player;
  season?: Season;
  seasonSplits?: {
    vsLeft: Season;
    vsRight: Season;
  };
  isCustom?: boolean;
};

// Final type used in lineups
export type DisplayLineupPlayer = {
  id: string;
  playerSeason: PlayerSeason;
  isSelected: boolean;
  isUnassigned: boolean;
};
