import { initTRPC } from "@trpc/server";
import { type CreateNextContextOptions } from "@trpc/server/adapters/next";
import superjson from "superjson";
import { ZodError } from "zod";

import { db } from "~/server/db";
import { createClient } from "utils/supabase/server-props"; // adjust the import path as needed
import { Session } from "@supabase/supabase-js";

// Define your context options to include the Supabase session.
// (Replace `any` with a proper type from @supabase/supabase-js if available.)
type CreateContextOptions = {
  session: Session | null;
};

// Create the inner context using the session
const createInnerTRPCContext = (opts: CreateContextOptions) => {
  return {
    db,
    session: opts.session,
  };
};

/**
 * Update the exported context function to be async so that we can
 * use our Supabase client to get the session from the incoming request.
 */
export const createTRPCContext = async (opts: CreateNextContextOptions) => {
  const { req, res } = opts;
  // Create a Supabase client with your req/res.
  // Note: The createClient function expects a full GetServerSidePropsContext,
  // so we build a minimal dummy object.
  const supabase = createClient({
    req,
    res,
    query: {},
    resolvedUrl: "",
  });
  const { data: { session } } = await supabase.auth.getSession();
  return createInnerTRPCContext({ session });
};

/**
 * 2. INITIALIZATION
 */
const t = initTRPC.context<typeof createTRPCContext>().create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

export const createCallerFactory = t.createCallerFactory;
export const createTRPCRouter = t.router;

const timingMiddleware = t.middleware(async ({ next, path }) => {
  const start = Date.now();
  if (t._config.isDev) {
    const waitMs = Math.floor(Math.random() * 400) + 100;
    await new Promise((resolve) => setTimeout(resolve, waitMs));
  }
  const result = await next();
  const end = Date.now();
  console.log(`[TRPC] ${path} took ${end - start}ms to execute`);
  return result;
});

export const publicProcedure = t.procedure.use(timingMiddleware);
