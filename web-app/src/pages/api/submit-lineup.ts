import { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === "POST") {
    await new Promise((resolve) => setTimeout(resolve, 2000)); // Mock API delay

    const { lineup } = req.body;
    console.log("Received lineup:", lineup);

    return res.status(200).json({ message: "Lineup submitted successfully", lineup });
  }

  return res.status(405).json({ message: "Method not allowed" });
}
