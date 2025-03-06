import { z } from "zod";

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

export const userRouter = createTRPCRouter({
  upsertUser: publicProcedure
    .input(z.object({
      email: z.string(),
    }))
    .mutation(({ input, ctx }) => {
      return ctx.db.user.upsert({
        where: {
          email: input.email,
        },
        create: {
          email: input.email,
        },
        update: {
          email: input.email,
        }
      });
    }),
});
