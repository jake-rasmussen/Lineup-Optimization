import { PrismaClient, Position, BattingHand, League } from "@prisma/client";

const prisma = new PrismaClient();

const apiKey = process.env.POINTSTREAK_API_KEY;

const seasonIds = [
  "33927", // ALPB 2024
  // Add more season IDs here
];

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const positionMap: Record<string, Position | undefined> = {
  "C": Position.CATCHER,
  "1B": Position.FIRST_BASE,
  "2B": Position.SECOND_BASE,
  "3B": Position.THIRD_BASE,
  "SS": Position.SHORTSTOP,
  "LF": Position.LEFT_FIELD,
  "CF": Position.CENTER_FIELD,
  "RF": Position.RIGHT_FIELD,
  "OF": Position.CENTER_FIELD,
  "IF": Position.SECOND_BASE,
  "DH": Position.DESIGNATED_HITTER,
};

const battingHandMap: Record<string, BattingHand | undefined> = {
  "R": BattingHand.RIGHT,
  "L": BattingHand.LEFT,
  "S": BattingHand.SWITCH,
  "B": BattingHand.SWITCH,
};

type RosterPlayer = {
  playerid: string;
  bats?: string;
  jersey?: string;
  birthday?: string;
};

const fetchRoster = async (teamLinkId: string, seasonId: string): Promise<Record<string, RosterPlayer>> => {
  const url = `https://api.pointstreak.com/baseball/team/roster/${teamLinkId}/${seasonId}/json`;
  try {
    await sleep(2000);
    const res = await fetch(url, {
      headers: {
        apikey: apiKey!,
      }
    });
    const json = await res.json();

    const players = json.league?.player ?? [];
    const mapped: Record<string, RosterPlayer> = {};

    for (const player of players) {
      mapped[player.playerid] = {
        playerid: player.playerid,
        bats: player.bats,
        jersey: typeof player.jersey === "string" ? player.jersey : undefined,
        birthday: player.birthday || undefined,
      };
    }

    return mapped;
  } catch (err) {
    console.error(`Error fetching roster for team ${teamLinkId}:`, err);
    return {};
  }
};

const parseValidDate = (dateString?: string): Date | undefined => {
  if (!dateString) return undefined;

  const date = new Date(dateString);
  return isNaN(date.getTime()) ? undefined : date;
};

const fetchStatsForSeason = async (seasonId: string) => {
  const url = `https://api.pointstreak.com/baseball/season/stats/${seasonId}/json`;
  try {
    console.log(`Fetching stats for season ${seasonId}`);
    await sleep(1350);
    const res = await fetch(url, {
      headers: {
        apikey: apiKey!,
      }
    });
    const json = await res.json();
    const players = json.stats?.batting?.player ?? [];

    // Collect all teams
    const teamLinkMap: Record<string, string> = {};
    players.forEach((p: { teamname: { teamid: any; teamlinkid: any; }; }) => {
      const teamId = p.teamname?.teamid;
      const teamLinkId = p.teamname?.teamlinkid;
      if (teamId && teamLinkId) {
        teamLinkMap[teamId] = teamLinkId;
      }
    });

    // Fetch rosters for teams in this season
    const teamRosterMap: Record<string, Record<string, RosterPlayer>> = {};
    for (const [teamId, teamLinkId] of Object.entries(teamLinkMap)) {
      teamRosterMap[teamId] = await fetchRoster(teamLinkId, seasonId);
    }

    const seasonYear = parseInt(json.stats.season.match(/\d{4}/)?.[0] ?? "2024");

    for (const player of players) {
      const playerId = player.playerid;
      const firstName = player.firstname;
      const lastName = player.lastname;
      const positionStr = player.position?.toUpperCase();
      const position = positionMap[positionStr];
      const teamId = player.teamname?.teamid;

      if (!position || !teamId) {
        console.warn(`Skipping player ${firstName} ${lastName} – bad position or team`);
        continue;
      }

      const rosterInfo = teamRosterMap[teamId]?.[playerId];

      const battingHand = rosterInfo?.bats ? battingHandMap[rosterInfo.bats] : BattingHand.RIGHT;
      const jerseyNumber = rosterInfo?.jersey ? parseInt(rosterInfo.jersey) : undefined;
      const birthday = parseValidDate(rosterInfo?.birthday);

      const existingPlayer = await prisma.player.findUnique({ where: { id: playerId } });

      if (!existingPlayer) {
        await prisma.player.create({
          data: {
            id: playerId,
            firstName,
            lastName,
            position,
            battingHand: battingHand || BattingHand.RIGHT,
            jerseyNumber,
            birthday,
          },
        });
      }

      const existingSeason = await prisma.season.findFirst({
        where: { playerId, year: seasonYear }
      });

      if (!existingSeason) {
        await prisma.season.create({
          data: {
            year: seasonYear,
            plateAppearances: parseInt(player.ab) || 0,
            runs: parseInt(player.runs) || 0,
            hits: parseInt(player.hits) || 0,
            singles: (
              parseInt(player.hits) -
              (parseInt(player.bib) || 0) -
              (parseInt(player.trib) || 0) -
              (parseInt(player.hr) || 0)
            ) || 0,
            doubles: parseInt(player.bib) || 0,
            triples: parseInt(player.trib) || 0,
            homeruns: parseInt(player.hr) || 0,
            walks: parseInt(player.bb) || 0,
            hitByPitch: parseInt(player.hp) || 0,
            intentionalWalks: 0,
            player: { connect: { id: playerId } },
            teamId,
            league: League.ALPB,
          }
        });
      }
    }

    console.log(`Finished season ${seasonId}`);
  } catch (err) {
    console.error(`Error processing season ${seasonId}:`, err);
  }
};

const run = async () => {
  for (const seasonId of seasonIds) {
    await fetchStatsForSeason(seasonId);
  }

  await prisma.$disconnect();
};

run().catch(console.error);
