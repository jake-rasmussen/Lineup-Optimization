import { Player } from "@prisma/client";
import { NextApiRequest, NextApiResponse } from "next";
import { db } from "~/server/db";

// Extend the response type to include a position property.
type LineupResponse = Record<
  number,
  { player: Player; isSelected: boolean; isUnassigned: boolean; position: string }
>;

// Available positions (same as in your Prisma enum)
const positions = [
  "PITCHER",
  "CATCHER",
  "FIRST_BASE",
  "SECOND_BASE",
  "THIRD_BASE",
  "LEFT_FIELD",
  "CENTER_FIELD",
  "RIGHT_FIELD",
  "SHORTSTOP",
  "DESIGNATED_HITTER",
];

function getRandomPosition(): string {
  return positions[Math.floor(Math.random() * positions.length)]!;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 10000));

  // Expecting a selectedLineup (mapping spot to playerId or null) and an array of unassigned player IDs.
  const { selectedLineup, unassignedPlayers }: { selectedLineup: Record<number, string | null>, unassignedPlayers: string[] } = req.body;

  // Query players from your database.
  const players = await db.player.findMany();

  // Build a mapping from player ID to a computed object that includes a full name.
  const playerMap: Record<string, Player> = {};
  players.forEach((player: Player) => {
    playerMap[player.id] = {
      id: player.id,
      firstName: player.firstName,
      lastName: player.lastName,
      position: player.position,
      battingHand: player.battingHand,
      jerseyNumber: player.jerseyNumber,
      salary: player.salary,
      birthday: player.birthday,
    };
  });

  // Determine which players have been explicitly selected.
  const selectedPlayerIds = new Set(Object.values(selectedLineup).filter(Boolean));
  // (This filtered array is available if you need it later.)
  const selectedPlayersData = players.filter((player: Player) => selectedPlayerIds.has(player.id));

  // Build the lineup response.
  const lineup: LineupResponse = {};

  // For players in the selected lineup, assign them to their respective spot with their DB position.
  Object.entries(selectedLineup).forEach(([spot, playerId]) => {
    if (playerId && playerMap[playerId]) {
      const player = playerMap[playerId];
      lineup[parseInt(spot)] = {
        player: {
          id: player.id,
          firstName: player.firstName,
          lastName: player.lastName,
          position: player.position,
          battingHand: player.battingHand,
          jerseyNumber: player.jerseyNumber,
          salary: player.salary,
          birthday: player.birthday,
        },
        isSelected: true,
        isUnassigned: false,
        position: player.position,
      };
    }
  });

  // Find spots that haven't been assigned by the selected lineup.
  const allSpots = Array.from({ length: 9 }, (_, i) => i + 1);
  const emptySpots = allSpots.filter((spot) => !lineup[spot]);

  // For players provided in the unassignedPlayers list, fill empty spots randomly.
  const shuffledUnassigned = [...unassignedPlayers].sort(() => Math.random() - 0.5);
  shuffledUnassigned.forEach((playerId) => {
    if (emptySpots.length === 0) return;
    if (playerMap[playerId]) {
      const randomSpotIndex = Math.floor(Math.random() * emptySpots.length);
      const randomSpot = emptySpots.splice(randomSpotIndex, 1)[0];
      const player = playerMap[playerId];
      lineup[randomSpot!] = {
        player: {
          id: player.id,
          firstName: player.firstName,
          lastName: player.lastName,
          position: player.position,
          battingHand: player.battingHand,
          jerseyNumber: player.jerseyNumber,
          salary: player.salary,
          birthday: player.birthday,
        },
        isSelected: false,
        isUnassigned: true,
        position: getRandomPosition(),
      };
    }
  });

  // For any remaining empty spots, fill them with players that weren’t selected or marked as unassigned.
  const remainingPlayers = players
    .filter((player: Player) => !selectedPlayerIds.has(player.id) && !unassignedPlayers.includes(player.id))
    .sort(() => Math.random() - 0.5);

  let remainingPoolIndex = 0;
  for (const spot of emptySpots) {
    if (remainingPoolIndex < remainingPlayers.length) {
      const player = remainingPlayers[remainingPoolIndex];
      lineup[spot] = {
        player: {
          id: player!.id,
          firstName: player!.firstName,
          lastName: player!.lastName,
          position: player!.position,
          battingHand: player!.battingHand,
          jerseyNumber: player!.jerseyNumber,
          salary: player!.salary,
          birthday: player!.birthday,
        },
        isSelected: false,
        isUnassigned: false,
        position: getRandomPosition(),
      };
      remainingPoolIndex++;
    }
  }

  return res.status(200).json({ message: "Lineup generated successfully", lineup, expectedRuns: 4.3 });
}
