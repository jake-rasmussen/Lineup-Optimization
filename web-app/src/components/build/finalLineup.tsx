import { DisplayLineupPlayer } from "~/pages/build";
import PlayerTable from "../playerTableView";
import { Button, Card, CardBody, CardFooter, CardHeader } from "@heroui/react";
import { useRouter } from "next/router";
import toast from "react-hot-toast";
import { api } from "~/utils/api";

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
    <Card className="w-1/2">
      <CardBody className="flex flex-col items-center gap-8">
        <PlayerTable lineup={lineup || []} />
        {
          expectedRuns && (
            <span className="flex flex-row gap-2 text-2xl uppercase font-black">
              <h3>Expected runs: </h3>
              <p className="text-red-500 font-black underline">{expectedRuns}</p>
            </span>
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