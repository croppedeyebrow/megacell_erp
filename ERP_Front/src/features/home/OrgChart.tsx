import { Link } from 'react-router-dom'
import { cn } from '@/lib/cn'
import { ORG_ROOT, type OrgTeamNode } from './orgData'

function MemberList({ team }: { team: OrgTeamNode }) {
  if (team.members.length === 0) return null

  return (
    <ul className="org-chart__member-list">
      {team.members.map((member, index) => (
        <li
          key={`${team.slug}-${member.name}-${index}`}
          className={cn(
            'org-chart__member',
            index === 0 && 'org-chart__member--head',
          )}
        >
          <span className="org-chart__member-name">{member.name}</span>
          <span className="org-chart__member-role">{member.role}</span>
          {member.tag && <span className="org-chart__member-tag">{member.tag}</span>}
        </li>
      ))}
    </ul>
  )
}

function TeamBox({ team }: { team: OrgTeamNode }) {
  return (
    <div className="org-chart__team">
      <Link to={`/org/${team.slug}`} className="org-chart__node org-chart__node--team">
        <span className="org-chart__node-title">{team.title}</span>
        <MemberList team={team} />
      </Link>

      {team.children && team.children.length > 0 && (
        <>
          <div className="org-chart__connector" />
          <div className="org-chart__teams">
            {team.children.map((child) => (
              <TeamBox key={child.slug} team={child} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export function OrgChart() {
  const ceo = ORG_ROOT.members[0]

  return (
    <div className="org-chart">
      <Link
        to={`/org/${ORG_ROOT.slug}`}
        className="org-chart__node org-chart__node--ceo"
      >
        <span className="org-chart__node-title">{ceo?.role}</span>
        <span className="org-chart__node-name">{ceo?.name}</span>
      </Link>

      <div className="org-chart__connector" />

      <div className="org-chart__teams">
        {ORG_ROOT.children?.map((team) => (
          <TeamBox key={team.slug} team={team} />
        ))}
      </div>
    </div>
  )
}
