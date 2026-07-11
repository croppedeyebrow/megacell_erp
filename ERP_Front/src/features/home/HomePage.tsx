import { Link } from 'react-router-dom'
import { Page } from '@/components/layout/AppShell'
import { PageHeader } from '@/components/layout/PageHeader'
import { Panel, StatCard, StatusBadge } from '@/components/ui'
import { useAuth } from '@/auth/AuthContext'
import { todayLabel } from '@/lib/format'

export function HomePage() {
  const { user } = useAuth()

  return (
    <Page>
      <PageHeader
        title={`안녕하세요, ${user?.name ?? ''}님`}
        description={todayLabel()}
        breadcrumbs={[{ label: '홈' }]}
      />

      <div className="stat-grid">
        <StatCard label="승인 대기" value={3} meta="오늘 기준" to="/sales/orders?f.status=pending" />
        <StatCard label="생산 요청" value={5} meta="진행·대기" to="/production/requests" />
        <StatCard label="출고 준비" value={2} meta="오늘 출고 예정" to="/inventory/shipments?f.status=requested" />
        <StatCard label="AS 배정" value={4} meta="미종결" to="/as?f.status=assigned" />
      </div>

      <div className="home-grid">
        <Panel title="주요 예외">
          <ul className="list-plain">
            <li>
              <div>
                <Link to="/sales/orders/2">SO-2026-0141</Link>
                <div style={{ color: 'var(--color-neutral-500)', fontSize: 13 }}>
                  납기 지연 · 그린모빌리티
                </div>
              </div>
              <StatusBadge code="delayed" />
            </li>
            <li>
              <div>
                <Link to="/inventory/product-stock">MC-Module 12S</Link>
                <div style={{ color: 'var(--color-neutral-500)', fontSize: 13 }}>
                  재고 부족 · 현재고 3 EA
                </div>
              </div>
              <StatusBadge code="shortage" />
            </li>
            <li>
              <div>
                <Link to="/admin/migration">MIG-2026-0012</Link>
                <div style={{ color: 'var(--color-neutral-500)', fontSize: 13 }}>
                  이관 일부 실패 · 오류 3건
                </div>
              </div>
              <StatusBadge code="partial_success" />
            </li>
          </ul>
        </Panel>

        <Panel title="빠른 메뉴">
          <ul className="list-plain">
            <li>
              <Link to="/sales/orders/new">수주 등록</Link>
            </li>
            <li>
              <Link to="/as/new">AS 접수</Link>
            </li>
            <li>
              <Link to="/sales/document-convert">PDF 문서 변환</Link>
            </li>
            <li>
              <Link to="/inventory/shipments">출고 관리</Link>
            </li>
          </ul>
        </Panel>

        <Panel title="최근 활동">
          <ul className="list-plain">
            <li>
              <span>수주 SO-2026-0142 확정</span>
              <span style={{ color: 'var(--color-neutral-500)', fontSize: 12 }}>오늘 09:12</span>
            </li>
            <li>
              <span>출고 SH-2026-0048 완료</span>
              <span style={{ color: 'var(--color-neutral-500)', fontSize: 12 }}>어제 16:40</span>
            </li>
            <li>
              <span>AS-2026-0033 배정</span>
              <span style={{ color: 'var(--color-neutral-500)', fontSize: 12 }}>어제 11:05</span>
            </li>
          </ul>
        </Panel>

        <Panel title="내 할 일">
          <ul className="list-plain">
            <li>
              <Link to="/sales/shipment-requests">출고 요청 검토 2건</Link>
            </li>
            <li>
              <Link to="/production/requests/2">생산 지연 대응 1건</Link>
            </li>
            <li>
              <Link to="/as/1">AS 접수 확인 1건</Link>
            </li>
          </ul>
        </Panel>
      </div>
    </Page>
  )
}
