import { NextApiRequest, NextApiResponse } from "next";
import { mockPlayers } from "~/data/players";

type LineupResponse = Record<number, { name: string; isSelected: boolean; isUnassigned: boolean }>;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  await new Promise((resolve) => setTimeout(resolve, 2000)); // Mock API delay

  const { selectedLineup, unassignedPlayers }: { selectedLineup: Record<number, string | null>, unassignedPlayers: string[] } = req.body;

  const selectedPlayerIds = new Set(Object.values(selectedLineup).filter(Boolean));
  const selectedPlayers = mockPlayers.filter((player) => selectedPlayerIds.has(player.id));

  const lineup: LineupResponse = {};

  Object.entries(selectedLineup).forEach(([spot, playerId]) => {
    if (playerId) {
      const player = selectedPlayers.find((p) => p.id === playerId);
      if (player) {
        lineup[parseInt(spot)] = { name: player.name, isSelected: true, isUnassigned: false };
      }
    }
  });

  const shuffledUnassigned = [...unassignedPlayers].sort(() => Math.random() - 0.5);
  const emptySpots = Array.from({ length: 9 }, (_, i) => i + 1).filter((spot) => !lineup[spot]);

  shuffledUnassigned.forEach((playerId) => {
    const player = mockPlayers.find((p) => p.id === playerId);
    if (player && emptySpots.length > 0) {
      const randomSpot = emptySpots.splice(Math.floor(Math.random() * emptySpots.length), 1)[0];
      lineup[randomSpot!] = { name: player.name, isSelected: false, isUnassigned: true };
    }
  });

  const remainingPlayers = mockPlayers
    .filter((player) => !selectedPlayerIds.has(player.id) && !unassignedPlayers.includes(player.id))
    .sort(() => Math.random() - 0.5);

  let remainingPoolIndex = 0;
  for (const spot of emptySpots) {
    if (remainingPoolIndex < remainingPlayers.length) {
      lineup[spot] = { name: remainingPlayers[remainingPoolIndex]!.name, isSelected: false, isUnassigned: false };
      remainingPoolIndex++;
    }
  }

  return res.status(200).json({ message: "Lineup generated successfully", lineup });
}
