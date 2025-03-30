import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

const destinations = [
  { left: "10%", top: "10%" },
  { left: "45%", top: "5%" },
  { left: "80%", top: "10%" }
];

const HomeRunAnimation = () => {
  const [dest, setDest] = useState({ left: "65%", top: "70%" });
  const [animKey, setAnimKey] = useState(0);

  useEffect(() => {
    let timeout: string | number | NodeJS.Timeout | undefined;
    const animate = () => {
      const randomDestination = destinations[Math.floor(Math.random() * destinations.length)];
      setDest(randomDestination!);
      setAnimKey(prev => prev + 1);
      timeout = setTimeout(animate, 1850);
    };

    timeout = setTimeout(animate, 1000);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <div className="relative max-w-xl w-full">
      <img src="Field.svg" alt="Field" className="w-full" />
      <motion.div
        key={animKey}
        initial={{ left: "65%", top: "70%" }}
        animate={{
          left: ["65%", dest.left],
          top: ["70%", "-20%", dest.top],
          opacity: [0, 1, 0],
          scale: [0.5, 1.2, 0.5]
        }}
        transition={{
          duration: 0.85,
          ease: "easeInOut"
        }}
        style={{ position: "absolute", fontSize: "2rem" }}
      >
        ⚾️
      </motion.div>
    </div>
  );
};

export default HomeRunAnimation;

