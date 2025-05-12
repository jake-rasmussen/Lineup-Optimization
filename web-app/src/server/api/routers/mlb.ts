import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";
import { League } from "@prisma/client";
import { getBattingHand, getPosition } from "~/utils/helper";

type StatSplit = {
  season: string;
  stat: {
    plateAppearances: number;
    runs: number;
    hits: number;
    doubles: number;
    triples: number;
    homeRuns: number;
    baseOnBalls: number;
    hitByPitch: number;
    intentionalWalks: number;
  };
  team?: {
    id?: number;
    name?: string;
  };
}

type StatsResponse = {
  people?: {
    stats?: {
      splits?: StatSplit[];
    }[];
  }[];
}

interface PlayerSplit {
  id: number;
  firstName: string;
  lastName: string;
  primaryNumber?: string;
  birthDate?: string;
  primaryPosition?: { abbreviation: string; type: string };
  batSide?: { code: string };
}

export const mlbRouter = createTRPCRouter({
  searchPlayerByName: publicProcedure
    .input(z.string())
    .mutation(async ({ input }) => {
      const query = input.trim();
      const url = `https://statsapi.mlb.com/api/v1/people/search?names=${encodeURIComponent(query)}`;
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Failed to search players: ${res.status}`);
      }

      const data = await res.json();
      const players = data.people || [];

      const mappedPlayers = players.map((p: any) => ({
        id: p.id.toString(),
        firstName: p.firstName,
        lastName: p.lastName,
        position: getPosition(p.primaryPosition?.abbreviation ?? "DH"),
        battingHand: getBattingHand(p.batSide?.code ?? "R"),
        jerseyNumber: p.primaryNumber ? parseInt(p.primaryNumber) : undefined,
        birthday: p.birthDate ? new Date(p.birthDate) : undefined,
        salary: undefined,
        seasons: [],
        lineupEntry: [],
      }));

      return mappedPlayers;
    }),
  getPlayerStats: publicProcedure
    .input(z.object({
      playerId: z.string(),
    }))
    .mutation(async ({ input }) => {
      const personId = input.playerId;
      const baseUrl = `https://statsapi.mlb.com/api/v1/people?personIds=${personId}`;

      const levels = [
        { url: `${baseUrl}&hydrate=stats(group=[hitting],type=[yearByYear])`, league: "MLB" },
        { url: `${baseUrl}&hydrate=stats(group=[hitting],type=[yearByYear],sportId=11)`, league: "AAA" },
        { url: `${baseUrl}&hydrate=stats(group=[hitting],type=[yearByYear],sportId=12)`, league: "AA" },
        { url: `${baseUrl}&hydrate=stats(group=[hitting],type=[yearByYear],sportId=13)`, league: "A+" },
        { url: `${baseUrl}&hydrate=stats(group=[hitting],type=[yearByYear],sportId=14)`, league: "A" },
      ];

      const responses = await Promise.all(levels.map(l => fetch(l.url)));

      if (responses.some(res => !res.ok)) {
        throw new Error("Failed to fetch stats");
      }

      const data: StatsResponse[] = await Promise.all(responses.map(res => res.json()));

      const allSplits = data.flatMap((res, index) => {
        const splits = res.people?.[0]?.stats?.[0]?.splits ?? [];
        const league = levels[index]!.league;

        return splits
          .filter(s => s.stat?.plateAppearances)
          .map(s => ({
            id: `${personId}-${s.season}`,
            year: parseInt(s.season),
            plateAppearances: s.stat.plateAppearances,
            runs: s.stat.runs,
            hits: s.stat.hits,
            singles: s.stat.hits - (s.stat.doubles + s.stat.triples + s.stat.homeRuns),
            doubles: s.stat.doubles,
            triples: s.stat.triples,
            homeruns: s.stat.homeRuns,
            walks: s.stat.baseOnBalls,
            hitByPitch: s.stat.hitByPitch,
            intentionalWalks: s.stat.intentionalWalks,
            playerId: personId.toString(),
            teamId: s.team?.id?.toString() || "",
            teamName: s.team?.name || "Unknown Team",
            league: league as League,
          }));
      });

      return allSplits.sort((a, b) => {
        if (a.league === "MLB" && b.league !== "MLB") return -1;
        if (a.league !== "MLB" && b.league === "MLB") return 1;
        return b.year - a.year;
      });
    }),
  getPlayersByFilter: publicProcedure
    .input(z.object({
      teamId: z.string().optional(),
      seasonYear: z.number().optional(),
      search: z.string().optional(),
    }))
    .query(async ({ input }) => {
      const mapPlayers = (players: PlayerSplit[]) => players
        .filter((p) => p.primaryPosition?.type !== "Pitcher")
        .map((p) => ({
          id: p.id.toString(),
          firstName: p.firstName,
          lastName: p.lastName,
          position: getPosition(p.primaryPosition?.abbreviation ?? "DH"),
          battingHand: getBattingHand(p.batSide?.code ?? "R"),
          jerseyNumber: p.primaryNumber ? parseInt(p.primaryNumber) : null,
          birthday: p.birthDate ? new Date(p.birthDate) : null,
          salary: null,
          seasons: [],
          lineupEntry: []
        }));

      if (input.teamId) {
        const rosterUrl = `https://statsapi.mlb.com/api/v1/teams/${input.teamId}/roster${input.seasonYear ? `?season=${input.seasonYear}` : ""}`;
        const rosterRes = await fetch(rosterUrl);
        if (!rosterRes.ok) throw new Error("Failed to fetch team roster");

        const rosterData = await rosterRes.json();
        const playerIds = rosterData.roster?.map((r: any) => r.person.id) ?? [];
        if (!playerIds.length) return [];

        const playerDetailsRes = await fetch(`https://statsapi.mlb.com/api/v1/people?personIds=${playerIds.join(",")}`);
        if (!playerDetailsRes.ok) throw new Error("Failed to fetch player details");

        const { people }: { people: PlayerSplit[] } = await playerDetailsRes.json();
        const mapped = mapPlayers(people || []);

        if (input.search?.trim()) {
          const lowerSearch = input.search.trim().toLowerCase();
          return mapped.filter(p =>
            `${p.firstName} ${p.lastName}`.toLowerCase().includes(lowerSearch)
          );
        }

        return mapped;
      }

      if (input.search?.trim()) {
        const query = input.search.trim();
        const searchUrl = `https://statsapi.mlb.com/api/v1/people/search?names=${encodeURIComponent(query)}`;
        const res = await fetch(searchUrl);
        if (!res.ok) {
          throw new Error(`Failed to search players: ${res.status}`);
        }

        const data = await res.json();
        const players: PlayerSplit[] = data.people || [];
        return mapPlayers(players);
      }

      return [];
    }),
});
