
import Head from "next/head";
import AuthModal from "~/components/auth/authModal";

export default function Home() {
  return (
    <>
      <Head>
        <title>Lineup Optimization</title>
        <meta name="description" content="Johns Hopkins Sports Analytics Group" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-white to-slate-500">
        <div className="flex flex-col items-center justify-center gap-12 px-4 py-16">
          <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-[5rem]">
            Lineup <span className="text-red-500">Optimization</span>
          </h1>
          <div>
            <AuthModal />
          </div>
        </div>
      </main>
    </>
  );
}
