import { League } from "@prisma/client";
import { alpbTeamMap, mlbTeamMap } from "~/data/teams";

export function formatPosition(position: string): string {
  return position
    .toLowerCase()
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function formatBattingHand(battingHand: string): string {
  return battingHand
    .toLowerCase()
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export const getTeamName = (league: League, teamId: string | null) => {
  if (!teamId) return "Unkown Team";

  if (league === League.MLB) {
    return mlbTeamMap.get(teamId) || "Unknown Team";
  } else {
    return alpbTeamMap.get(teamId) || "Unknown Team";
  }
};