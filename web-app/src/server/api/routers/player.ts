import { League } from "@prisma/client";
import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

export const playerRouter = createTRPCRouter({
  getPlayersByFilter: publicProcedure
    .input(
      z.object({
        teamId: z.string().optional(),
        seasonYear: z.number().optional(),
        search: z.string().optional(),
        league: z.enum([
          League.ALPB,
          League.MLB,
          League.CUSTOM
        ])
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
        league: input.league,
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
