import { Player, Season } from "@prisma/client";

// This is used for building a lineup, where we store the player and its respective season
export type PlayerSeason = {
  compositeId: string;
  player: Player;
  season?: Season;
  isCustom?: boolean;
}

export type DisplayLineupPlayer = {
  id: string,
  playerSeason: PlayerSeason;
  isSelected: boolean;
  isUnassigned: boolean;
};
