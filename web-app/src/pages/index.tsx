import Head from "next/head";
import { useRouter } from "next/router"
import { useState } from "react"
import { createClient } from "utils/supabase/component";

export default function Home() {
  const router = useRouter()
  const supabase = createClient()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  async function logIn() {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      console.error(error)
    }
    router.push("/")
  }

  async function signUp() {
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) {
      console.error(error)
    }
    router.push("/")
  }


  return (
    <>
      <Head>
        <title>Lineup Optimization</title>
        <meta name="description" content="Johns Hopkins Sports Analytics Group" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-white to-slate-500">
        <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
          <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-[5rem]">
            Lineup <span className="text-red-500">Optimization</span>
          </h1>
          <div>
            <form>
              <label htmlFor="email">Email:</label>
              <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <label htmlFor="password">Password:</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button type="button" onClick={logIn}>
                Log in
              </button>
              <button type="button" onClick={signUp}>
                Sign up
              </button>
            </form>
          </div>
        </div>
      </main>
    </>
  );
}
