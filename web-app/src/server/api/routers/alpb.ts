import { z } from "zod";
import { League, Season } from "~/data/types";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";
import { getBattingHand, getPosition } from "~/utils/helper";

const BASE_URL = "https://api.pointstreak.com/baseball";
const API_KEY = process.env.POINTSTREAK_API_KEY!;

async function fetchJSON(url: string) {
  const res = await fetch(url, {
    headers: { apikey: API_KEY }
  });
  if (!res.ok) throw new Error(`Failed to fetch: ${url}`);
  return res.json();
}

export const alpbRouter = createTRPCRouter({
  getPlayerStats: publicProcedure
    .input(z.object({
      playerId: z.string(),
      seasonId: z.string(),
    }))
    .mutation(async ({ input }) => {
      const url = `${BASE_URL}/player/stats/${input.playerId}/${input.seasonId}/json`;
      const data = await fetchJSON(url);

      const p = data.player;

      const season: Season = {
        id: input.seasonId,
        year: parseInt(data?.season?.split("-")[1]?.trim() ?? "0") || 9999,
        plateAppearances: parseInt(p.ab ?? "0"),
        runs: parseInt(p.runs ?? "0"),
        hits: parseInt(p.hits ?? "0"),
        singles: p.hits && p.bib && p.trib && p.hr
          ? parseInt(p.hits) - (parseInt(p.bib ?? "0") + parseInt(p.trib ?? "0") + parseInt(p.hr ?? "0"))
          : 0,
        doubles: parseInt(p.bib ?? "0"),
        triples: parseInt(p.trib ?? "0"),
        homeruns: parseInt(p.hr ?? "0"),
        walks: parseInt(p.bb ?? "0"),
        hitByPitch: parseInt(p.hp ?? "0"),
        intentionalWalks: 0,
        playerId: input.playerId,
        teamId: p.teamname?.teamlinkid ?? null,
        teamName: p.teamname?.fullname ?? "",
        league: League.ALPB,
      };

      return season;
    }),
  getSeasons: publicProcedure.query(async () => {
      const res = await fetch("https://api.pointstreak.com/baseball/league/structure/174/json", {
        headers: { apikey: API_KEY },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch Pointstreak seasons");
      }

      const data = await res.json();
      const seasons = data.league?.season ?? [];

      return seasons.map((s: any) => ({
        id: s.seasonid,
        name: s.name,
      }));
    }),
  getTeamsBySeason: publicProcedure
    .input(z.object({
      leagueId: z.string(),
      seasonId: z.string(),
    }))
    .query(async ({ input }) => {
      const url = `${BASE_URL}/league/structure/${input.leagueId}/json`;

      console.log("URL", url)

      const res = await fetch(url, {
        headers: { apikey: API_KEY },
      });

      if (!res.ok) throw new Error("Failed to fetch league structure");

      const data = await res.json();
      const seasons = data?.league?.season ?? [];
      const season = seasons.find((s: any) => s.seasonid === input.seasonId);
      if (!season) return [];

      const teams: { id: string; name: string }[] = [];

      for (const division of Array.isArray(season.division) ? season.division : [season.division]) {
        for (const team of division.team ?? []) {
          teams.push({
            id: team.teamlinkid,
            name: team.teamname,
          });
        }
      }

      return teams;
    }),
  getPlayersByFilter: publicProcedure
    .input(z.object({
      teamId: z.string().optional(),
      seasonId: z.string().optional(),
    }))
    .query(async ({ input }) => {
      if (!input.seasonId) throw new Error("seasonId is required");

      const url = `${BASE_URL}/season/stats/${input.seasonId}/json`;
      const data = await fetchJSON(url);

      const rawPlayers = data?.stats?.batting?.player;
      const players = Array.isArray(rawPlayers) ? rawPlayers : [];

      const filtered = players.filter((p: any) => {
        const matchesTeam = input.teamId ? p.teamname?.teamlinkid === input.teamId : true;
        return matchesTeam;
      });

      const mapped = filtered.map((p: any) => {
        const player = {
          id: p.playerlinkid,
          fullName: p.firstname + " " + p.lastname,
          position: getPosition(p.position ?? "DH"),
          battingHand: getBattingHand(p.bats ?? "R"),
          jerseyNumber: p.jersey ? parseInt(p.jersey) : null,
          birthday: null,
          salary: null,
          seasons: [],
          lineupEntry: [],
        };

        const season = {
          id: input.seasonId!,
          year: parseInt(data?.stats?.season?.split("-")[1]?.trim() ?? "0") || undefined,
          plateAppearances: parseInt(p.ab ?? "0"),
          runs: parseInt(p.runs ?? "0"),
          hits: parseInt(p.hits ?? "0"),
          singles: p.hits && p.bib && p.trib && p.hr
            ? parseInt(p.hits) - (parseInt(p.bib ?? "0") + parseInt(p.trib ?? "0") + parseInt(p.hr ?? "0"))
            : 0,
          doubles: parseInt(p.bib ?? "0"),
          triples: parseInt(p.trib ?? "0"),
          homeruns: parseInt(p.hr ?? "0"),
          walks: parseInt(p.bb ?? "0"),
          hitByPitch: parseInt(p.hp ?? "0"),
          intentionalWalks: 0, // Not provided by Pointstreak API
          playerId: p.playerlinkid,
          player: undefined,
          teamId: p.teamname?.teamlinkid ?? null,
          teamName: p.teamname?.fullname ?? "",
          league: League.ALPB,
        };

        return {
          compositeId: `${player.id}_${season.id}`,
          player,
          season,
        };
      });

      return mapped;
    })

});
