import { PrismaClient, Position } from "@prisma/client";
import { TeamSplitsResponse, Player } from "./types";

const prisma = new PrismaClient();

const accessLevel = "trial";
const languageCode = "en";
const format = "json";
const apiKey = process.env.SPORTS_RADAR_API_KEY;

const teamsEndpoint = `https://api.sportradar.com/mlb/${accessLevel}/v8/${languageCode}/league/teams.${format}?api_key=${apiKey}`;

const mlbTeamNames = new Set([
  "Angels", "Astros", "Athletics", "Blue Jays", "Braves", "Brewers", "Cardinals", "Cubs",
  "Diamondbacks", "Dodgers", "Guardians", "Mariners", "Marlins", "Mets", "Nationals", "Orioles",
  "Padres", "Phillies", "Pirates", "Rangers", "Rays", "Red Sox", "Reds", "Rockies", "Royals",
  "Tigers", "Twins", "White Sox", "Yankees", "Giants"
]);

const positionEnumMap = new Map<string, Position>([
  ["RP", Position.PITCHER],
  ["SP", Position.PITCHER],
  ["C", Position.CATCHER],
  ["1B", Position.FIRST_BASE],
  ["2B", Position.SECOND_BASE],
  ["3B", Position.THIRD_BASE],
  ["SS", Position.SHORTSTOP],
  ["CF", Position.CENTER_FIELD],
  ["LF", Position.LEFT_FIELD],
  ["RF", Position.RIGHT_FIELD],
  ["DH", Position.DESIGNATED_HITTER]
]);

// Fetch all MLB teams and return their IDs
const fetchMLBTeamIds = async (): Promise<string[]> => {
  try {
    const response = await fetch(teamsEndpoint);
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

    const data = await response.json();
    const mlbTeamIds = data.teams
      .filter((team: { name: string; }) => mlbTeamNames.has(team.name))
      .map((team: { id: any; }) => team.id);
    return mlbTeamIds;
  } catch (error) {
    console.error("Error fetching MLB teams:", error);
    return [];
  }
};

// Fetch players for a specific team and store them in the database
const fetchPlayersForTeam = async (
  teamId: string,
  seasonYear: number,
  seasonType: string = "REG"
) => {
  try {
    const playersEndpoint = `https://api.sportradar.com/mlb/${accessLevel}/v8/${languageCode}/seasons/${seasonYear}/${seasonType}/teams/${teamId}/splits.${format}?api_key=${apiKey}`;
    const response = await fetch(playersEndpoint);

    if (!response.ok) {
      throw new Error(`HTTP error fetching players for team ${teamId}: ${response.status}`);
    }

    const teamSplits: TeamSplitsResponse = await response.json();

    teamSplits.players.map(async (player: Player) => {
      const position = positionEnumMap.get(player.primary_position) as Position;
      await prisma.player.upsert({
        where: { id: player.id },
        update: {

        },
        create: {
          id: player.id,
          firstName: player.first_name,
          lastName: player.last_name,
          position,
        },
      });

      if (position !== Position.PITCHER && player.splits.hitting) {
        const hittingStats = player.splits.hitting.overall[0].total[0];

        await prisma.season.create({
          data: {
            year: seasonYear,
            plateAppearances: hittingStats.ab,
            runs: hittingStats.runs,
            hits: hittingStats.h,
            singles: hittingStats.s,
            doubles: hittingStats.d,
            triples: hittingStats.t,
            homeruns: hittingStats.hr,
            walks: hittingStats.bb,
            hitByPitch: hittingStats.hbp,
            intentionalWalks: hittingStats.ibb,
            player: { connect: { id: player.id } },
          }
        });
      }
    })
  } catch (error) {
    console.error(`Error fetching/storing players for team ${teamId}:`, error);
    return {} as TeamSplitsResponse;
  }
}

// Main function to fetch all team IDs and populate the database
const populateDatabase = async () => {
  // const teamIds = await fetchMLBTeamIds();
  const seasonYear = 2024;
  const teamIds = ["ef64da7f-cfaf-4300-87b0-9313386b977c"]; //2024 dodgers

  for (const teamId of teamIds) {
    await fetchPlayersForTeam(teamId, seasonYear);
  }

  console.log("Database population complete.");
};

populateDatabase()
  .catch(console.error);
