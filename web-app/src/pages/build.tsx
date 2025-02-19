import { Progress, Spinner } from "@heroui/react";
import { useRouter } from "next/router";
import { useState } from "react";
import BuildModal from "~/components/build/buildModal";

export default function Build() {
  const [loading, setLoading] = useState(false);

  const router = useRouter();

  const handleSubmit = async (lineup: Record<number, string>) => {
    setLoading(true);

    // Mock API delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    try {
      const response = await fetch("/api/submit-lineup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lineup }),
      });

      if (response.ok) {
        setLoading(false);
        // router.push("/confirmation");
      } else {
        console.error("Failed to submit lineup");
      }
    } catch (error) {
      console.error("Error submitting lineup:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <main className="flex min-h-screen flex-col items-center">
        {
          loading ? (
            <div className="flex flex-col gap-4 min-h-screen w-full items-center justify-center">
              <h2 className="text-xl">Creating lineup...</h2>
              <Progress isIndeterminate aria-label="Loading..." className="max-w-md" size="md" />
            </div>
          ) : (
            <div className="flex flex-col gap-12 px-4 py-16 items-center">
         
              <div>
                <BuildModal handleSubmit={handleSubmit} />
              </div>
            </div>
          )}

      </main>
    </>
  );
}
