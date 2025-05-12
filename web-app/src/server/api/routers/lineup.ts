import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";
import { db } from "~/server/db";

export const lineupRouter = createTRPCRouter({
  saveLineup: publicProcedure
    .input(
      z.object({
        name: z.string().optional(),
        selectedLineup: z.record(z.string(), z.any()),
        expectedRuns: z.number().optional(),
      })
    )
    .mutation(async ({ input }) => {
      const { name = "Untitled Lineup", selectedLineup, expectedRuns } = input;

      await db.savedLineup.create({
        data: {
          name,
          data: selectedLineup,
          expectedRuns,
        },
      });

      return { success: true };
    }),
  getLineups: publicProcedure.query(async () => {
    const lineups = await db.savedLineup.findMany({
      orderBy: { createdAt: "desc" },
      select: {
        id: true,
        name: true,
        data: true,
        expectedRuns: true,
        createdAt: true,
      },
    });

    return lineups;
  }),
  deleteLineup: publicProcedure
    .input(
      z.object({
        id: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      await db.savedLineup.delete({
        where: { id: input.id },
      });

      return { success: true };
    }),
});
