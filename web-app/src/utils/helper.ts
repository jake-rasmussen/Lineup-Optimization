import { BattingHand, League, Player, Position, Season } from "~/data/types";
import { alpbTeamMap, mlbTeamNameMap } from "~/data/teams";
import { PlayerSeason } from "~/data/types";

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
    return mlbTeamNameMap.get(teamId) || "Unknown Team";
  } else {
    return alpbTeamMap.get(teamId) || "Unknown Team";
  }
};

export const getPosition = (abbr: string): Position => {
  switch (abbr) {
    case "P":
    case "SP":
    case "RP":
      return Position.PITCHER;
    case "C":
      return Position.CATCHER;
    case "1B":
      return Position.FIRST_BASE;
    case "2B":
      return Position.SECOND_BASE;
    case "3B":
      return Position.THIRD_BASE;
    case "SS":
      return Position.SHORTSTOP;
    case "LF":
      return Position.LEFT_FIELD;
    case "CF":
      return Position.CENTER_FIELD;
    case "RF":
      return Position.RIGHT_FIELD;
    case "DH":
      return Position.DESIGNATED_HITTER;
    default:
      return Position.DESIGNATED_HITTER;
  }
};

export const getBattingHand = (code: string): BattingHand => {
  switch (code) {
    case "L":
      return BattingHand.LEFT;
    case "R":
      return BattingHand.RIGHT;
    case "S":
      return BattingHand.SWITCH;
    default:
      return BattingHand.RIGHT;
  }
};

export const getPlayerSeasonCompositeId = (
  player: Player,
  season?: Season
): string => {
  if (!season) return player.id;

  const teamName = season.teamName || "Unknown";
  return `${player.fullName} - ${teamName} ${season.year}`;
};

export const getSeasonSelectKey = (season: Season) =>
  `${season.id}-${season.teamId}`;

export const getPlayerSeasonString = (playerSeason?: PlayerSeason) => {
  if (!playerSeason) {
    return "-";
  } else {
    const {
      player,
      season,
      isCustom
    } = playerSeason;

    if (playerSeason.season?.year === 9999) {
      return `${playerSeason.player.fullName.replace(/&apos;/g, "'")}`;
    } else {
      return `${playerSeason.player.fullName} ${isCustom ? "- Custom Player" : `${season?.teamName} ${season?.year ? season?.year : ""}`}`;
    }
  }
}

export function isMLBCareer(season: Season): boolean {
  return season.id.endsWith("-mlb-career") || season.teamName === "MLB Career";
}

export function formatSeasonLabel(season: Season): string {
  return isMLBCareer(season)
    ? "MLB Career"
    : `${season.year} (${season.teamName})`;
}