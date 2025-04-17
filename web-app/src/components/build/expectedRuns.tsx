import { Card, CardBody, CardHeader, Divider } from "@heroui/react";
import Image from "next/image";

const ExpectedRuns = ({ expectedRuns }: { expectedRuns: number }) => {
  return (
    <Card>
      <CardHeader>Expected Runs</CardHeader>
      <CardBody className="flex flex-col items-center gap-2">
        <div className="relative w-20 h-20">
          <Image
            src="/hitter.png"
            alt="Hitter Icon"
            fill
            className="object-contain"
          />
        </div>
        <Divider />
        <div className="flex flex-col items-center">
          <h2 className="text-red-500 font-black uppercase text-5xl">
            {expectedRuns}
          </h2>
          <p className="text-gray-500 text-xs">
            Runs per game
          </p>
        </div>
      </CardBody>
    </Card>
  );
};

export default ExpectedRuns;
