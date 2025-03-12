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

const mlbTeamIds = [
  "4f735188-37c8-473d-ae32-1f7e34ccf892", // Angels
  "eb21dadd-8f10-4095-8bf3-dfb3b779f107", // Astros
  "27a59d3b-ff7c-48ea-b016-4798f560f5e1", // Athletics
  "1d678440-b4b1-4954-9b39-70afb3ebbcfa", // Blue Jays
  "12079497-e414-450a-8bf2-29f91de646bf", // Braves
  "dcfd5266-00ce-442c-bc09-264cd20cf455", // Brewers
  "44671792-dc02-4fdd-a5ad-f5f17edaa9d7", // Cardinals
  "55714da8-fcaf-4574-8443-59bfb511a524", // Cubs
  "25507be1-6a68-4267-bd82-e097d94b359b", // Diamondbacks
  "ef64da7f-cfaf-4300-87b0-9313386b977c", // Dodgers
  "80715d0d-0d2a-450f-a970-1b9a3b18c7e7", // Guardians
  "43a39081-52b4-4f93-ad29-da7f329ea960", // Mariners
  "03556285-bdbb-4576-a06d-42f71f46ddc5", // Marlins
  "f246a5e5-afdb-479c-9aaa-c68beeda7af6", // Mets
  "d89bed32-3aee-4407-99e3-4103641b999a", // Nationals
  "75729d34-bca7-4a0f-b3df-6f26c6ad3719", // Orioles
  "d52d5339-cbdd-43f3-9dfa-a42fd588b9a3", // Padres
  "2142e1ba-3b40-445c-b8bb-f1f8b1054220", // Phillies
  "481dfe7e-5dab-46ab-a49f-9dcc2b6e2cfd", // Pirates
  "d99f919b-1534-4516-8e8a-9cd106c6d8cd", // Rangers
  "bdc11650-6f74-49c4-875e-778aeb7632d9", // Rays
  "93941372-eb4c-4c40-aced-fe3267174393", // Red Sox
  "c874a065-c115-4e7d-b0f0-235584fb0e6f", // Reds
  "29dd9a87-5bcc-4774-80c3-7f50d985068b", // Rockies
  "833a51a9-0d84-410f-bd77-da08c3e5e26e", // Royals
  "575c19b7-4052-41c2-9f0a-1c5813d02f99", // Tigers
  "aa34e0ed-f342-4ec6-b774-c79b47b60e2d", // Twins
  "47f490cd-2f58-4ef7-9dfd-2ad6ba6c1ae8", // White Sox
  "a09ec676-f887-43dc-bbb3-cf4bbaee9a18", // Yankees
  "a7723160-10b7-4277-a309-d8dd95a8ae65", // Giants
];

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

    for (const player of teamSplits.players) {
      const position = positionEnumMap.get(player.primary_position) as Position;

      if (position !== Position.PITCHER && player.splits.hitting) {
        const hittingStats = player.splits.hitting.overall[0].total[0];

        await prisma.player.upsert({
          where: { id: player.id },
          update: {},
          create: {
            id: player.id,
            firstName: player.first_name,
            lastName: player.last_name,
            position,
          },
        });

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
            teamId,
          }
        });
      }
    }
  } catch (error) {
    console.error(`Error fetching/storing players for team ${teamId}:`, error);
  }
};

// Main function to reset database and fetch data
const populateDatabase = async () => {
  try {
    console.log("Resetting database...");

    // Delete existing data before inserting new data
    await prisma.$transaction([
      prisma.season.deleteMany({}),
      prisma.player.deleteMany({})
    ]);

    console.log("Database reset complete. Fetching new data...");

    const seasonYear = 2024;

    for (const teamId of mlbTeamIds) {
      await fetchPlayersForTeam(teamId, seasonYear);
    }

    console.log("Database population complete.");
  } catch (error) {
    console.error("Error resetting and populating the database:", error);
  } finally {
    await prisma.$disconnect();
  }
};

populateDatabase()
  .catch(console.error);
