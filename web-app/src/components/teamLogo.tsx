import { getTeamName } from "~/utils/helper";

const TeamLogo = ({ teamId, className }: { teamId: string; className?: string }) => {
  return (
    <div className={`w-10 h-10 overflow-hidden ${className}`}>
      <img
        src={`./team-logos/${getTeamName(teamId)}.png`}
        alt={`${getTeamName(teamId)} logo`}
        className="w-full h-full object-contain"
      />
    </div>
  );
};

export default TeamLogo;
