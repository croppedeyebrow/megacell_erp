import { Page } from '@/components/layout/AppShell'
import { PageHeader } from '@/components/layout/PageHeader'
import { Panel } from '@/components/ui'
import { OrgChart } from './OrgChart'

export function OrgChartPage() {
  return (
    <Page>
      <PageHeader
        title="조직도"
        description="메가셀 조직 구성"
        breadcrumbs={[{ label: '홈', to: '/' }, { label: '조직도' }]}
      />

      <Panel>
        <OrgChart />
      </Panel>
    </Page>
  )
}
