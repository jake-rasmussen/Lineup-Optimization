import { DisplayLineupPlayer } from "~/pages/build";
import PlayerTable from "../playerTableView";
import { Button, Card, CardBody, CardFooter, CardHeader } from "@heroui/react";
import { useRouter } from "next/router";
import toast from "react-hot-toast";
import { api } from "~/utils/api";
import ExpectedRuns from "./expectedRuns";

type PropType = {
  lineup: Record<number, DisplayLineupPlayer>,
  expectedRuns?: number;
}

const FinalLineup = ({ lineup, expectedRuns }: PropType) => {
  const router = useRouter();

  const saveLineup = api.lineup.saveLineup.useMutation({
    onSuccess() {
      toast.dismiss();
      toast.success("Saved lineup!");
    },
    onError() {
      toast.dismiss();
      toast.error("Error...")
    }
  });

  const convertDisplayLineupToRaw = (
    displayLineup: Record<number, DisplayLineupPlayer>
  ): Record<string, string> => {
    return Object.fromEntries(
      Object.entries(displayLineup).map(([spot, displayLineupPlayer]) => (
        [spot, displayLineupPlayer.player.id]
      ))
    );
  };

  const handleSave = async () => {
    if (!lineup) return;

    toast.dismiss();
    toast.loading("Saving lineup...");

    const selectedLineupForSaving = convertDisplayLineupToRaw(lineup);
    saveLineup.mutate({ selectedLineup: selectedLineupForSaving });
  };

  return (
    <Card className="w-1/2 overflow-visible">
      <CardHeader>
        <h1 className="text-4xl font-bold text-center">Generated Lineup</h1>
      </CardHeader>
      <CardBody className="flex flex-col items-center gap-8 relative overflow-visible">
        <PlayerTable lineup={lineup || []} />
        {
          expectedRuns && (
            <div className="absolute right-0 transform translate-x-1/2">
              <ExpectedRuns expectedRuns={expectedRuns} />
            </div>
          )
        }
      </CardBody>
      <CardFooter className="flex gap-4 justify-center">
        <Button onPress={() => router.reload()}>
          Back
        </Button>
        <Button onPress={handleSave} color="primary">
          Save
        </Button>
      </CardFooter>
    </Card>
  )

}

export default FinalLineup;