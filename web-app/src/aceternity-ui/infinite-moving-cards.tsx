"use client";

import React, { useEffect, useState } from "react";
import { cn } from "~/utils/aceternity-utils";

// Constant array of team names.
const teamNames: string[] = [
  "Angels",
  "Astros",
  "Athletics",
  "Blue Jays",
  "Braves",
  "Brewers",
  "Cardinals",
  "Cubs",
  "Diamondbacks",
  "Dodgers",
  "Guardians",
  "Mariners",
  "Marlins",
  "Mets",
  "Nationals",
  "Orioles",
  "Padres",
  "Phillies",
  "Pirates",
  "Rangers",
  "Rays",
  "Red Sox",
  "Reds",
  "Rockies",
  "Royals",
  "Tigers",
  "Twins",
  "White Sox",
  "Yankees",
  "Giants",
];

export const InfiniteMovingCards = ({
  direction = "left",
  speed = "fast",
  pauseOnHover = true,
  className,
}: {
  direction?: "left" | "right";
  speed?: "fast" | "normal" | "slow";
  pauseOnHover?: boolean;
  className?: string;
}) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const scrollerRef = React.useRef<HTMLUListElement>(null);
  const [start, setStart] = useState(false);

  useEffect(() => {
    addAnimation();
  }, []);

  function addAnimation() {
    if (containerRef.current && scrollerRef.current) {
      const scrollerContent = Array.from(scrollerRef.current.children);
      // Duplicate each item so the list repeats
      scrollerContent.forEach((item) => {
        const duplicatedItem = item.cloneNode(true);
        scrollerRef.current?.appendChild(duplicatedItem);
      });
      getDirection();
      getSpeed();
      setStart(true);
    }
  }

  const getDirection = () => {
    if (containerRef.current) {
      containerRef.current.style.setProperty(
        "--animation-direction",
        direction === "left" ? "forwards" : "reverse"
      );
    }
  };

  const getSpeed = () => {
    if (containerRef.current) {
      const duration =
        speed === "fast" ? "40s" : speed === "normal" ? "80s" : "160s";
      containerRef.current.style.setProperty("--animation-duration", duration);
    }
  };

  return (
    <div
      ref={containerRef}
      className={cn(
        "scroller relative z-20 max-w-7xl overflow-hidden [mask-image:linear-gradient(to_right,transparent,white_20%,white_80%,transparent)]",
        className
      )}
    >
      <ul
        ref={scrollerRef}
        className={cn(
          "flex w-max min-w-full shrink-0 flex-nowrap gap-4 py-4",
          start && "animate-scroll",
          pauseOnHover && "hover:[animation-play-state:paused]"
        )}
      >
        {teamNames.map((teamName, idx) => (
          <li
            key={teamName + idx}
            className="relative w-[150px] max-w-full shrink-0 rounded-2xl border border-zinc-200 bg-white px-2 py-2 dark:border-zinc-700 dark:bg-gray-900"
          >
            <img
              src={`./team-logos/${teamName}.png`}
              alt={`${teamName} logo`}
              className="w-full h-full object-contain"
            />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default InfiniteMovingCards;
