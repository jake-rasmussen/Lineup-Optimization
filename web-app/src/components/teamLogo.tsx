
import { useLeague } from "~/context/leagueContext";
import { League } from "~/data/types";
import { getTeamName } from "~/utils/helper";

const TeamLogo = ({ teamId, className }: { teamId: string; className?: string }) => {
  const { league } = useLeague();

  return (
    <div className={`w-10 h-10 overflow-hidden ${className}`}>
      <img
        src={`/${league === League.MLB ? "mlb" : "alpb"}-team-logos/${getTeamName(league, teamId)}.png`}
        alt={`${getTeamName(league, teamId)} logo`}
        className="w-full h-full object-contain"
      />
    </div>
  );
};

export default TeamLogo;
