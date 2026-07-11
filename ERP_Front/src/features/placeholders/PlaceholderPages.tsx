import { Page } from '@/components/layout/AppShell'
import { PageHeader } from '@/components/layout/PageHeader'
import { Alert, Panel } from '@/components/ui'
import type { BreadcrumbItem, PageAction } from '@/types'

/** 메뉴 구조에 포함된 2차 화면용 플레이스홀더 */
export function PlaceholderPage({
  title,
  description,
  breadcrumbs,
  actions,
}: {
  title: string
  description?: string
  breadcrumbs: BreadcrumbItem[]
  actions?: PageAction[]
}) {
  return (
    <Page>
      <PageHeader
        title={title}
        description={description}
        breadcrumbs={breadcrumbs}
        actions={actions}
      />
      <Panel>
        <Alert tone="info" title="초기 UI 골격">
          이 화면은 정보 구조와 내비게이션을 위한 초기 골격입니다. API·업무 규칙
          연동 시 DataTable·상세·폼 패턴으로 확장합니다.
        </Alert>
      </Panel>
    </Page>
  )
}

export function QuotesPage() {
  return (
    <PlaceholderPage
      title="견적"
      description="견적 목록과 문서 추출 결과를 관리합니다."
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '영업' },
        { label: '견적' },
      ]}
      actions={[{ label: '견적 등록', variant: 'primary' }]}
    />
  )
}

export function UnshippedPage() {
  return (
    <PlaceholderPage
      title="미출고"
      description="수주 대비 미출고 잔량을 조회합니다."
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '영업' },
        { label: '미출고' },
      ]}
    />
  )
}

export function ShipmentRequestsPage() {
  return (
    <PlaceholderPage
      title="출고 요청"
      description="영업에서 요청한 출고를 등록·추적합니다."
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '영업' },
        { label: '출고 요청' },
      ]}
      actions={[{ label: '출고 요청', variant: 'primary' }]}
    />
  )
}

export function CustomersPage() {
  return (
    <PlaceholderPage
      title="고객/거래처"
      description="거래처 기준정보를 조회·관리합니다."
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '영업' },
        { label: '고객/거래처' },
      ]}
    />
  )
}

export function ProductionProgressPage() {
  return (
    <PlaceholderPage
      title="생산 계획/진행"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '생산' },
        { label: '생산 계획/진행' },
      ]}
    />
  )
}

export function BomRequirementsPage() {
  return (
    <PlaceholderPage
      title="BOM 소요량"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '생산' },
        { label: 'BOM 소요량' },
      ]}
    />
  )
}

export function MaterialShortagePage() {
  return (
    <PlaceholderPage
      title="부족 자재"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '생산' },
        { label: '부족 자재' },
      ]}
    />
  )
}

export function InspectionPage() {
  return (
    <PlaceholderPage
      title="검수/출고 준비"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '생산' },
        { label: '검수/출고 준비' },
      ]}
    />
  )
}

export function PurchaseRequestsPage() {
  return (
    <PlaceholderPage
      title="구매 요청"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '구매·자재' },
        { label: '구매 요청' },
      ]}
      actions={[{ label: '구매 요청', variant: 'primary' }]}
    />
  )
}

export function PurchaseOrdersPage() {
  return (
    <PlaceholderPage
      title="발주"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '구매·자재' },
        { label: '발주' },
      ]}
    />
  )
}

export function MaterialStockPage() {
  return (
    <PlaceholderPage
      title="자재 현재고"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '구매·자재' },
        { label: '자재 현재고' },
      ]}
    />
  )
}

export function MaterialMovementsPage() {
  return (
    <PlaceholderPage
      title="자재 입출고"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '구매·자재' },
        { label: '자재 입출고' },
      ]}
    />
  )
}

export function SuppliersPage() {
  return (
    <PlaceholderPage
      title="공급업체"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '구매·자재' },
        { label: '공급업체' },
      ]}
    />
  )
}

export function BatteryStockPage() {
  return (
    <PlaceholderPage
      title="배터리 재고/이력"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '재고·출고' },
        { label: '배터리 재고/이력' },
      ]}
    />
  )
}

export function AsHistoryPage() {
  return (
    <PlaceholderPage
      title="고객·제품별 이력"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: 'AS' },
        { label: '고객·제품별 이력' },
      ]}
    />
  )
}

export function ProductsMasterPage() {
  return (
    <PlaceholderPage
      title="제품"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '기준정보' },
        { label: '제품' },
      ]}
    />
  )
}

export function MaterialsMasterPage() {
  return (
    <PlaceholderPage
      title="자재"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '기준정보' },
        { label: '자재' },
      ]}
    />
  )
}

export function BomMasterPage() {
  return (
    <PlaceholderPage
      title="BOM/리비전"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '기준정보' },
        { label: 'BOM/리비전' },
      ]}
    />
  )
}

export function WarehousesPage() {
  return (
    <PlaceholderPage
      title="창고"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '기준정보' },
        { label: '창고' },
      ]}
    />
  )
}

export function CodesPage() {
  return (
    <PlaceholderPage
      title="코드 관리"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '기준정보' },
        { label: '코드 관리' },
      ]}
    />
  )
}

export function AnalyticsDashboardPage() {
  return (
    <PlaceholderPage
      title="업무 대시보드"
      description="역할별 KPI와 예외를 표시합니다. 최종 갱신 시각이 함께 노출됩니다."
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '분석' },
        { label: '업무 대시보드' },
      ]}
    />
  )
}

export function ExecutiveSummaryPage() {
  return (
    <PlaceholderPage
      title="경영 요약"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '분석' },
        { label: '경영 요약' },
      ]}
    />
  )
}

export function DemandPage() {
  return (
    <PlaceholderPage
      title="수요·적정재고"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '분석' },
        { label: '수요·적정재고' },
      ]}
    />
  )
}

export function AuditLogsPage() {
  return (
    <PlaceholderPage
      title="감사 로그"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '관리' },
        { label: '감사 로그' },
      ]}
    />
  )
}

export function DocumentTemplatesPage() {
  return (
    <PlaceholderPage
      title="문서 템플릿"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '관리' },
        { label: '문서 템플릿' },
      ]}
    />
  )
}

export function SystemStatusPage() {
  return (
    <PlaceholderPage
      title="시스템 상태"
      breadcrumbs={[
        { label: '홈', to: '/' },
        { label: '관리' },
        { label: '시스템 상태' },
      ]}
    />
  )
}
