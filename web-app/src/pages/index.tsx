
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
      <main className="flex min-h-screen flex-col items-center justify-center">
        <div className="flex flex-col items-center justify-center gap-12 px-4 py-16">
          <h1 className="text-5xl font-extrabold tracking-tight text-black sm:text-[5rem]">
            Lineup <span className="text-red-500">Optimization</span>
          </h1>
          <p className="text-lg text-center max-w-2xl text-gray-700">
            Creating the perfect baseball lineup is both an art and a science. Our lineup optimizer helps you select the best combination of players and arrange them in the most effective batting order. By using statistical insights and strategic placement, you can build a lineup that maximizes offensive potential and improves game performance.
          </p>
          <p className="text-lg text-center max-w-2xl text-gray-700">
            Ready to create your winning lineup? Click the button below to get started.
          </p>
          <div>
            <AuthModal />
          </div>
        </div>
      </main>
    </>
  );
}
