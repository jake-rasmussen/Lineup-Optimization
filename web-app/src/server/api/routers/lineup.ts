import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";
import type { Position } from "@prisma/client";

// List of valid positions from your Prisma enum.
const positions: Position[] = [
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

export const lineupRouter = createTRPCRouter({
  saveLineup: publicProcedure
    .input(
      z.object({
        selectedLineup: z.record(z.string(), z.string()),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const session = ctx.session;

      if (!session || !session.user.email) {
        throw new Error("User not authenticated");
      }
      const userEmail = session.user.email;

      const lineup = await ctx.db.lineup.create({
        data: { userEmail },
      });

      for (const [spotStr, playerId] of Object.entries(input.selectedLineup)) {
        const player = await ctx.db.player.findUnique({ where: { id: playerId } });
        if (!player) {
          throw new Error(`Player with id ${playerId} not found`);
        }
        
        await ctx.db.lineupEntry.create({
          data: {
            lineupId: lineup.id,
            playerId,
            battingSpot: parseInt(spotStr),
          },
        });
      }

      return lineup;
    }),
  getSavedLineups: publicProcedure
    .query(async ({ ctx }) => {
      const session = ctx.session;
      if (!session || !session.user.email) {
        throw new Error("User not authenticated");
      }
      const userEmail = session.user.email;

      return ctx.db.lineup.findMany({
        where: { userEmail },
        include: {
          entries: {
            include: {
              player: true // this will include the nested Player data
            }
          }
        }
      });
    }),
});
