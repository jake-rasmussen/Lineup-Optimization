import { Position } from "@prisma/client";
import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

export const playerRouter = createTRPCRouter({
  fetchAndStorePlayers: publicProcedure
    .input(z.object({ teamId: z.string(), seasonYear: z.number() }))
    .mutation(async ({ ctx, input }) => {
      const { teamId, seasonYear } = input;
      const playersEndpoint = `https://api.sportradar.com/mlb/trial/v8/en/seasons/${seasonYear}/REG/teams/${teamId}/splits.json?api_key=YOUR_API_KEY`;
      const response = await fetch(playersEndpoint);

      if (!response.ok) {
        throw new Error(`HTTP error fetching players for team ${teamId}: ${response.status}`);
      }

      const teamSplits = await response.json();

      for (const split of teamSplits.splits) {
        const playerData = split.player;
        const hittingStats = split.hitting?.overall?.[0]?.total;
        const position = playerData.primary_position.toUpperCase() as Position;

        if (hittingStats && position != Position.PITCHER) {
          const player = await ctx.db.player.upsert({
            where: { id: playerData.id },
            update: {},
            create: {
              id: playerData.id,
              firstName: playerData.first_name,
              lastName: playerData.last_name,
              position,
            },
          });

          await ctx.db.season.create({
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
            },
          });
        }
      }
      return { message: "Players and seasons stored successfully." };
    }),
  getPlayersByFilter: publicProcedure
    .input(
      z.object({
        teamId: z.string().optional(),
        seasonYear: z.number().optional(),
        search: z.string().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      // Build search filter by splitting the search string into terms.
      const searchFilter = input.search
        ? {
          AND: input.search
            .split(/\s+/)
            .filter(Boolean)
            .map((term) => ({
              OR: [
                { firstName: { contains: term, mode: "insensitive" as const } },
                { lastName: { contains: term, mode: "insensitive" as const } },
              ],
            })),
        }
        : {};

      // Build the season filter using both teamId and seasonYear.
      const seasonWhere = {
        ...(input.teamId ? { teamId: input.teamId } : {}),
        ...(input.seasonYear ? { year: input.seasonYear } : {}),
      };

      return ctx.db.player.findMany({
        where: {
          ...searchFilter,
          // Only include players that have at least one season matching both filters.
          ...(input.teamId || input.seasonYear ? { seasons: { some: seasonWhere } } : {}),
        },
        include: {
          // Restrict the included seasons to those that match both team and season.
          seasons: input.teamId || input.seasonYear
            ? { where: seasonWhere }
            : true,
        },
      });
    }),
  getSeasonsByPlayerId: publicProcedure
    .input(z.object({ playerId: z.string() }))
    .query(async ({ ctx, input }) => {
      return ctx.db.season.findMany({
        where: { playerId: input.playerId },
        orderBy: { year: 'desc' },
      });
    }),
});
