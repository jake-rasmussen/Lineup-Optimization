import { NextApiRequest, NextApiResponse } from "next";

type SeasonStats = {
  plateAppearances: number;
  hits: number;
  doubles: number;
  triples: number;
  homeruns: number;
  walks: number;
  hitByPitch: number;
  intentionalWalks: number;
  runs: number;
  singles: number;
};

type LineupInput = Record<
  number,
  {
    name: string;
    data: SeasonStats | null;
  }
>;

type InputPayload = {
  selectedLineup: LineupInput;
  unassignedPlayers: Array<{
    name: string;
    data: SeasonStats | null;
  }>;
};

type PlayerSeason = {
  player: {
    firstName: string;
    lastName: string;
  };
  season: SeasonStats | null;
};

type LineupResponseEntry = {
  id: string;
  playerSeason: PlayerSeason;
  isSelected: boolean;
  isUnassigned: boolean;
};

type LineupResponse = {
  lineup: Record<number, LineupResponseEntry>;
  expectedRuns: number;
  message: string;
};

function parseName(fullName: string): { firstName: string; lastName: string } {
  let [firstName, ...lastParts] = fullName.trim().split(" ");
  const lastName = lastParts.join(" ") || "";
  firstName = firstName || "Unknown";
  return { firstName, lastName };
}

function makeId(firstName: string, lastName: string) {
  return `${firstName}-${lastName}`.toLowerCase().replace(/\s+/g, "-");
}

function getRandomElement<T>(arr: T[]): T | undefined {
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled[0];
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<LineupResponse | { message: string }>
) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const { selectedLineup, unassignedPlayers }: InputPayload = req.body;

  const lineup: Record<number, LineupResponseEntry> = {};

  // Step 1: Track filled spots (1–9)
  const filledSpots = new Set<number>();

  for (let spot = 1; spot <= 9; spot++) {
    const entry = selectedLineup[spot];
    if (!entry || !entry.name) continue;

    const { firstName, lastName } = parseName(entry.name);
    const id = makeId(firstName, lastName);

    lineup[spot] = {
      id,
      playerSeason: {
        player: { firstName, lastName },
        season: entry.data ?? null,
      },
      isSelected: true,
      isUnassigned: false,
    };

    filledSpots.add(spot);
  }

  // Step 2: Fill remaining spots from unassigned players
  const availableSpots = Array.from({ length: 9 }, (_, i) => i + 1).filter(
    (s) => !filledSpots.has(s)
  );

  for (const player of unassignedPlayers) {
    if (!player.name || availableSpots.length === 0) break;

    const { firstName, lastName } = parseName(player.name);
    const id = makeId(firstName, lastName);

    const randomSpot = getRandomElement(availableSpots);
    if (!randomSpot) continue;

    lineup[randomSpot] = {
      id,
      playerSeason: {
        player: { firstName, lastName },
        season: player.data ?? null,
      },
      isSelected: false,
      isUnassigned: true,
    };

    const index = availableSpots.indexOf(randomSpot);
    if (index !== -1) availableSpots.splice(index, 1);
  }

  return res.status(200).json({
    message: "Lineup generated successfully",
    lineup,
    expectedRuns: 7.5,
  });
}
