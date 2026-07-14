import { Link, useParams } from 'react-router-dom'
import { Page } from '@/components/layout/AppShell'
import { PageHeader } from '@/components/layout/PageHeader'
import { Alert, Panel } from '@/components/ui'
import { findOrgNode, ORG_ROOT } from './orgData'

export function OrgDepartmentPage() {
  const { slug } = useParams<{ slug: string }>()
  const team = slug ? findOrgNode(ORG_ROOT, slug) : undefined

  if (!team) {
    return (
      <Page>
        <PageHeader
          title="조직을 찾을 수 없습니다"
          breadcrumbs={[{ label: '홈', to: '/' }, { label: '조직도', to: '/org' }]}
        />
        <Alert tone="info" title="잘못된 주소">
          요청하신 조직 정보가 없습니다.
        </Alert>
        <div style={{ marginTop: 16 }}>
          <Link to="/org">조직도로 이동</Link>
        </div>
      </Page>
    )
  }

  return (
    <Page>
      <PageHeader
        title={team.title}
        description={`${team.members.length}명`}
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '조직도', to: '/org' },
          { label: team.title },
        ]}
      />

      <Panel>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>이름</th>
                <th>직급</th>
                <th>휴대폰</th>
                <th>내선</th>
                <th>이메일</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              {team.members.map((member, index) => (
                <tr key={`${member.name}-${index}`}>
                  <td>{member.name}</td>
                  <td>{member.role}</td>
                  <td>{member.phone ?? '-'}</td>
                  <td>{member.extension ?? '-'}</td>
                  <td>{member.email ?? '-'}</td>
                  <td>{member.tag ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {team.children && team.children.length > 0 && (
        <Panel title="하위 조직">
          <ul className="list-plain">
            {team.children.map((child) => (
              <li key={child.slug}>
                <Link to={`/org/${child.slug}`}>{child.title}</Link>
                <span style={{ color: 'var(--color-neutral-500)', fontSize: 13 }}>
                  {child.members.length}명
                </span>
              </li>
            ))}
          </ul>
        </Panel>
      )}
    </Page>
  )
}
