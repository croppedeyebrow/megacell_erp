import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Page } from '@/components/layout/AppShell'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable } from '@/components/data/DataTable'
import {
  Alert,
  Button,
  DescriptionList,
  Panel,
  StatusBadge,
  Tabs,
  TextArea,
  TextField,
  useToast,
} from '@/components/ui'
import {
  MOCK_AS,
  MOCK_INVENTORY,
  MOCK_MIGRATION_JOBS,
  MOCK_MOVEMENTS,
  MOCK_PRODUCTION,
  MOCK_SHIPMENTS,
  MOCK_USERS,
} from '@/mocks/data'
import { useClientList } from '@/hooks/useClientList'
import { formatDate, formatDateTime, formatQuantity } from '@/lib/format'
import { useAuth } from '@/auth/AuthContext'

export function ProductionRequestsPage() {
  const navigate = useNavigate()
  const list = useClientList(
    MOCK_PRODUCTION,
    [(r) => r.requestNo, (r) => r.orderNo, (r) => r.product],
    { status: (r) => r.status },
  )

  return (
    <Page>
      <PageHeader
        title="생산 요청"
        description="수주와 연결된 생산 요청을 조회합니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '생산' },
          { label: '생산 요청' },
        ]}
      />
      <DataTable
        columns={[
          { id: 'requestNo', header: '요청번호', accessor: (r) => r.requestNo, sortable: true },
          { id: 'orderNo', header: '수주번호', accessor: (r) => r.orderNo },
          { id: 'product', header: '품목', accessor: (r) => r.product },
          {
            id: 'quantity',
            header: '수량',
            accessor: (r) => formatQuantity(r.quantity, 'EA'),
            align: 'right',
          },
          { id: 'dueDate', header: '납기', accessor: (r) => formatDate(r.dueDate), sortable: true },
          { id: 'status', header: '상태', accessor: (r) => <StatusBadge code={r.status} /> },
          { id: 'owner', header: '담당자', accessor: (r) => r.owner },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filters={[
          {
            id: 'status',
            label: '상태',
            options: [
              { value: 'requested', label: '요청' },
              { value: 'in_progress', label: '진행 중' },
              { value: 'delayed', label: '지연' },
              { value: 'completed', label: '완료' },
            ],
          },
        ]}
        filteredEmpty={list.filteredEmpty}
        getRowHref={(r) => `/production/requests/${r.id}`}
        emptyTitle="생산 요청이 없습니다"
        emptyDescription="연결된 생산 요청이 아직 없습니다."
        onEmptyAction={() => navigate('/sales/orders')}
      />
    </Page>
  )
}

export function ProductionRequestDetailPage() {
  const { id } = useParams()
  const [tab, setTab] = useState('overview')
  const row = useMemo(
    () => MOCK_PRODUCTION.find((r) => r.id === id) ?? MOCK_PRODUCTION[0],
    [id],
  )

  return (
    <Page>
      <PageHeader
        title={row.requestNo}
        status={<StatusBadge code={row.status} />}
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '생산' },
          { label: '생산 요청', to: '/production/requests' },
          { label: row.requestNo },
        ]}
        meta={
          <>
            <span>
              수주 <strong><Link to="/sales/orders/1">{row.orderNo}</Link></strong>
            </span>
            <span>
              담당자 <strong>{row.owner}</strong>
            </span>
            <span>
              납기 <strong>{formatDate(row.dueDate)}</strong>
            </span>
          </>
        }
        actions={
          row.status === 'requested'
            ? [{ label: '생산 시작', variant: 'primary' }]
            : [{ label: '진행 갱신', variant: 'primary' }]
        }
      />
      <Tabs
        tabs={[
          { id: 'overview', label: '개요' },
          { id: 'items', label: '품목' },
          { id: 'links', label: '연결 업무' },
          { id: 'history', label: '변경 이력' },
        ]}
        value={tab}
        onChange={setTab}
      />
      <Panel>
        <DescriptionList
          items={[
            { label: '요청번호', value: row.requestNo },
            { label: '수주번호', value: row.orderNo },
            { label: '품목', value: row.product },
            { label: '수량', value: formatQuantity(row.quantity, 'EA') },
            { label: '상태', value: <StatusBadge code={row.status} /> },
          ]}
        />
      </Panel>
    </Page>
  )
}

export function ProductStockPage() {
  const list = useClientList(
    MOCK_INVENTORY,
    [(r) => r.sku, (r) => r.name, (r) => r.warehouse],
    { status: (r) => r.status },
  )

  return (
    <Page>
      <PageHeader
        title="제품 현재고"
        description="창고별 제품 현재고를 조회합니다. 합계는 필터 결과 기준입니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '재고·출고' },
          { label: '제품 현재고' },
        ]}
      />
      <DataTable
        columns={[
          { id: 'sku', header: '품목코드', accessor: (r) => r.sku, sortable: true },
          { id: 'name', header: '품목명', accessor: (r) => r.name },
          { id: 'warehouse', header: '창고', accessor: (r) => r.warehouse },
          {
            id: 'quantity',
            header: '현재고',
            accessor: (r) => formatQuantity(r.quantity, r.unit),
            align: 'right',
            sortable: true,
          },
          { id: 'status', header: '상태', accessor: (r) => <StatusBadge code={r.status} /> },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filters={[
          {
            id: 'status',
            label: '상태',
            options: [
              { value: 'active', label: '정상' },
              { value: 'shortage', label: '부족' },
            ],
          },
        ]}
        filteredEmpty={list.filteredEmpty}
        emptyTitle="재고 데이터가 없습니다"
        emptyDescription="이관 또는 입고 후 현재고가 표시됩니다."
      />
    </Page>
  )
}

export function ProductMovementsPage() {
  const list = useClientList(MOCK_MOVEMENTS, [
    (r) => r.sku,
    (r) => r.name,
    (r) => r.refNo,
    (r) => r.type,
  ])

  return (
    <Page>
      <PageHeader
        title="제품 입출고"
        description="재고 이동 원장(inventory_movements) 기준 이력입니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '재고·출고' },
          { label: '제품 입출고' },
        ]}
      />
      <DataTable
        columns={[
          {
            id: 'movedAt',
            header: '일시',
            accessor: (r) => formatDateTime(r.movedAt),
            sortable: true,
          },
          { id: 'sku', header: '품목코드', accessor: (r) => r.sku },
          { id: 'name', header: '품목명', accessor: (r) => r.name },
          { id: 'type', header: '유형', accessor: (r) => r.type },
          {
            id: 'quantity',
            header: '수량',
            accessor: (r) => formatQuantity(r.quantity, 'EA'),
            align: 'right',
          },
          { id: 'warehouse', header: '창고', accessor: (r) => r.warehouse },
          { id: 'refNo', header: '참조번호', accessor: (r) => r.refNo },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filteredEmpty={list.filteredEmpty}
      />
    </Page>
  )
}

export function ShipmentsPage() {
  const { hasPermission } = useAuth()
  const { toast } = useToast()
  const [confirmId, setConfirmId] = useState<string | null>(null)
  const list = useClientList(
    MOCK_SHIPMENTS,
    [(r) => r.shipmentNo, (r) => r.orderNo, (r) => r.customer],
    { status: (r) => r.status },
  )

  return (
    <Page>
      <PageHeader
        title="출고 관리"
        description="출고 요청부터 완료까지 처리합니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '재고·출고' },
          { label: '출고 관리' },
        ]}
      />
      <DataTable
        columns={[
          { id: 'shipmentNo', header: '출고번호', accessor: (r) => r.shipmentNo, sortable: true },
          { id: 'orderNo', header: '수주번호', accessor: (r) => r.orderNo },
          { id: 'customer', header: '거래처', accessor: (r) => r.customer },
          {
            id: 'quantity',
            header: '수량',
            accessor: (r) => formatQuantity(r.quantity, 'EA'),
            align: 'right',
          },
          {
            id: 'requestedAt',
            header: '요청일',
            accessor: (r) => formatDate(r.requestedAt),
          },
          { id: 'status', header: '상태', accessor: (r) => <StatusBadge code={r.status} /> },
          {
            id: 'actions',
            header: '작업',
            accessor: (r) =>
              r.status === 'requested' || r.status === 'in_progress' ? (
                <Button
                  size="sm"
                  variant="primary"
                  onClick={() => setConfirmId(r.id)}
                >
                  출고 완료
                </Button>
              ) : (
                '—'
              ),
          },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filters={[
          {
            id: 'status',
            label: '상태',
            options: [
              { value: 'requested', label: '요청' },
              { value: 'in_progress', label: '진행 중' },
              { value: 'completed', label: '완료' },
            ],
          },
        ]}
        filteredEmpty={list.filteredEmpty}
      />

      {confirmId && (
        <div className="overlay" role="presentation" onMouseDown={() => setConfirmId(null)}>
          <div
            className="modal"
            role="dialog"
            aria-modal
            onMouseDown={(e) => e.stopPropagation()}
          >
            <div className="modal__header">
              <h2 className="modal__title">출고 완료</h2>
            </div>
            <div className="modal__body">
              <p>
                출고를 완료하면 재고가 차감됩니다. 서버 처리가 끝나기 전에는 완료로
                표시되지 않습니다.
              </p>
              {!hasPermission('inventory.adjust') && (
                <Alert tone="warning" title="권한 안내">
                  출고 완료 권한이 없을 수 있습니다. API에서도 거부됩니다.
                </Alert>
              )}
            </div>
            <div className="modal__footer">
              <Button variant="ghost" onClick={() => setConfirmId(null)}>
                닫기
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  setConfirmId(null)
                  toast('출고가 완료되었습니다.', 'success')
                }}
              >
                출고 완료
              </Button>
            </div>
          </div>
        </div>
      )}
    </Page>
  )
}

export function AsListPage() {
  const navigate = useNavigate()
  const { hasPermission } = useAuth()
  const list = useClientList(
    MOCK_AS,
    [(r) => r.asNo, (r) => r.customer, (r) => r.product, (r) => r.symptom],
    { status: (r) => r.status },
  )

  return (
    <Page>
      <PageHeader
        title="AS 처리"
        description="접수·배정·처리 중인 AS를 관리합니다."
        breadcrumbs={[{ label: '홈', to: '/' }, { label: 'AS' }, { label: 'AS 처리' }]}
        actions={
          hasPermission('as.edit')
            ? [{ label: 'AS 접수', variant: 'primary', to: '/as/new' }]
            : undefined
        }
      />
      <DataTable
        columns={[
          { id: 'asNo', header: 'AS번호', accessor: (r) => r.asNo, sortable: true },
          { id: 'customer', header: '고객', accessor: (r) => r.customer },
          { id: 'product', header: '제품', accessor: (r) => r.product },
          { id: 'symptom', header: '증상', accessor: (r) => r.symptom },
          { id: 'assignee', header: '담당자', accessor: (r) => r.assignee },
          {
            id: 'receivedAt',
            header: '접수일',
            accessor: (r) => formatDate(r.receivedAt),
            sortable: true,
          },
          { id: 'status', header: '상태', accessor: (r) => <StatusBadge code={r.status} /> },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filters={[
          {
            id: 'status',
            label: '상태',
            options: [
              { value: 'received', label: '접수' },
              { value: 'assigned', label: '배정' },
              { value: 'in_progress', label: '진행 중' },
              { value: 'closed', label: '종결' },
            ],
          },
        ]}
        filteredEmpty={list.filteredEmpty}
        getRowHref={(r) => `/as/${r.id}`}
        emptyActionLabel={hasPermission('as.edit') ? 'AS 접수' : undefined}
        onEmptyAction={() => navigate('/as/new')}
      />
    </Page>
  )
}

export function AsDetailPage() {
  const { id } = useParams()
  const row = MOCK_AS.find((r) => r.id === id) ?? MOCK_AS[0]

  return (
    <Page>
      <PageHeader
        title={row.asNo}
        status={<StatusBadge code={row.status} />}
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: 'AS', to: '/as' },
          { label: row.asNo },
        ]}
        meta={
          <>
            <span>
              고객 <strong>{row.customer}</strong>
            </span>
            <span>
              담당자 <strong>{row.assignee}</strong>
            </span>
            <span>
              접수일 <strong>{formatDate(row.receivedAt)}</strong>
            </span>
          </>
        }
        actions={
          row.status !== 'closed'
            ? [{ label: '처리 진행', variant: 'primary' }]
            : undefined
        }
      />
      <Panel>
        <DescriptionList
          items={[
            { label: 'AS번호', value: row.asNo },
            { label: '고객', value: row.customer },
            { label: '제품', value: row.product },
            { label: '증상', value: row.symptom },
            { label: '상태', value: <StatusBadge code={row.status} /> },
          ]}
        />
      </Panel>
    </Page>
  )
}

export function AsCreatePage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [customer, setCustomer] = useState('')
  const [product, setProduct] = useState('')
  const [symptom, setSymptom] = useState('')

  return (
    <Page narrow>
      <PageHeader
        title="AS 접수"
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: 'AS', to: '/as' },
          { label: '접수' },
        ]}
      />
      <form
        className="panel"
        onSubmit={(e) => {
          e.preventDefault()
          if (!customer || !product || !symptom) {
            toast('고객, 제품, 증상을 입력하세요.', 'warning')
            return
          }
          toast('AS가 접수되었습니다.', 'success')
          navigate('/as')
        }}
      >
        <div className="form-grid">
          <TextField
            label="고객"
            required
            value={customer}
            onChange={(e) => setCustomer(e.target.value)}
          />
          <TextField
            label="제품"
            required
            value={product}
            onChange={(e) => setProduct(e.target.value)}
          />
        </div>
        <div style={{ marginTop: 16 }}>
          <TextArea
            label="증상"
            required
            value={symptom}
            onChange={(e) => setSymptom(e.target.value)}
          />
        </div>
        <div className="form-actions">
          <Button variant="ghost" type="button" onClick={() => navigate(-1)}>
            취소
          </Button>
          <Button variant="primary" type="submit">
            접수
          </Button>
        </div>
      </form>
    </Page>
  )
}

export function DocumentConvertPage() {
  const { toast } = useToast()
  const [step, setStep] = useState(1)
  const [fileName, setFileName] = useState<string | null>(null)

  return (
    <Page narrow>
      <PageHeader
        title="문서 변환"
        description="PDF 견적·발주서를 추출하고 XLSM을 생성합니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '영업' },
          { label: '문서 변환' },
        ]}
      />
      <Panel>
        <ol style={{ margin: '0 0 24px', paddingLeft: 20, color: 'var(--color-neutral-700)' }}>
          <li style={{ fontWeight: step === 1 ? 600 : 400 }}>PDF 업로드</li>
          <li style={{ fontWeight: step === 2 ? 600 : 400 }}>추출 진행</li>
          <li style={{ fontWeight: step === 3 ? 600 : 400 }}>추출 결과와 원문 비교</li>
          <li style={{ fontWeight: step === 4 ? 600 : 400 }}>필드·품목 수정</li>
          <li style={{ fontWeight: step === 5 ? 600 : 400 }}>사용자 확정</li>
          <li style={{ fontWeight: step === 6 ? 600 : 400 }}>XLSM 생성 및 이력 저장</li>
        </ol>

        {step === 1 && (
          <div>
            <TextField
              label="PDF 파일"
              type="file"
              accept="application/pdf"
              onChange={(e) => {
                const file = e.target.files?.[0]
                setFileName(file?.name ?? null)
              }}
            />
            {fileName && (
              <p style={{ marginTop: 8, fontSize: 13 }}>선택됨: {fileName}</p>
            )}
            <div className="form-actions">
              <Button
                variant="primary"
                disabled={!fileName}
                onClick={() => {
                  setStep(2)
                  window.setTimeout(() => setStep(3), 800)
                }}
              >
                추출 시작
              </Button>
            </div>
          </div>
        )}

        {step === 2 && <Alert tone="info" title="추출 중">문서를 분석하고 있습니다…</Alert>}

        {step >= 3 && step < 6 && (
          <div>
            <Alert tone="warning" title="확인 필요 필드">
              납기 confidence가 낮습니다. 원문과 비교 후 수정하세요.
            </Alert>
            <div className="form-grid" style={{ marginTop: 16 }}>
              <TextField label="거래처" defaultValue="한빛에너지" hint="자동 추출" />
              <TextField label="납기" defaultValue="2026-07-25" hint="신뢰도 낮음 · 수정됨 표시 가능" />
              <TextField label="품목" defaultValue="MC-Pack 48V 100Ah" />
              <TextField label="수량" defaultValue="20" />
            </div>
            <div className="form-actions">
              <Button variant="secondary" onClick={() => setStep(Math.max(3, step - 1))}>
                이전
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  if (step < 5) setStep(step + 1)
                  else {
                    setStep(6)
                    toast('XLSM이 생성되었습니다. (템플릿 v1.2)', 'success')
                  }
                }}
              >
                {step === 5 ? '확정 후 생성' : '다음'}
              </Button>
            </div>
          </div>
        )}

        {step === 6 && (
          <Alert tone="success" title="생성 완료">
            문서 이력이 저장되었습니다. 원본 PDF를 다시 올릴 필요 없이 재시도할 수 있습니다.
            <div style={{ marginTop: 12 }}>
              <Button variant="secondary" size="sm" onClick={() => setStep(1)}>
                새 변환 시작
              </Button>
            </div>
          </Alert>
        )}
      </Panel>
    </Page>
  )
}

export function UsersPage() {
  const list = useClientList(
    MOCK_USERS,
    [(r) => r.name, (r) => r.email, (r) => r.department],
    { status: (r) => r.status },
  )

  return (
    <Page>
      <PageHeader
        title="사용자/권한"
        description="사용자 계정과 역할을 관리합니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '관리' },
          { label: '사용자/권한' },
        ]}
        actions={[{ label: '사용자 초대', variant: 'primary' }]}
      />
      <DataTable
        columns={[
          { id: 'name', header: '이름', accessor: (r) => r.name, sortable: true },
          { id: 'email', header: '이메일', accessor: (r) => r.email },
          { id: 'department', header: '부서', accessor: (r) => r.department },
          { id: 'role', header: '역할', accessor: (r) => r.role },
          { id: 'status', header: '상태', accessor: (r) => <StatusBadge code={r.status} /> },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filters={[
          {
            id: 'status',
            label: '상태',
            options: [
              { value: 'active', label: '활성' },
              { value: 'inactive', label: '비활성' },
            ],
          },
        ]}
        filteredEmpty={list.filteredEmpty}
      />
    </Page>
  )
}

export function MigrationJobsPage() {
  const list = useClientList(MOCK_MIGRATION_JOBS, [
    (r) => r.jobNo,
    (r) => r.source,
    (r) => r.startedBy,
  ], { status: (r) => r.status })

  return (
    <Page>
      <PageHeader
        title="Excel 이관·동기화"
        description="이관 작업 상태, 성공·실패 건수, 오류 파일을 확인합니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '관리' },
          { label: 'Excel 이관·동기화' },
        ]}
        actions={[{ label: '이관 실행', variant: 'primary' }]}
      />
      <DataTable
        columns={[
          { id: 'jobNo', header: '작업번호', accessor: (r) => r.jobNo, sortable: true },
          { id: 'source', header: '원본', accessor: (r) => r.source },
          { id: 'startedBy', header: '시작자', accessor: (r) => r.startedBy },
          {
            id: 'startedAt',
            header: '시작',
            accessor: (r) => formatDateTime(r.startedAt),
          },
          {
            id: 'endedAt',
            header: '종료',
            accessor: (r) => formatDateTime(r.endedAt),
          },
          { id: 'status', header: '상태', accessor: (r) => <StatusBadge code={r.status} /> },
          {
            id: 'counts',
            header: '성공/경고/실패',
            accessor: (r) =>
              `${r.successCount} / ${r.warningCount} / ${r.failCount}`,
            align: 'right',
          },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filters={[
          {
            id: 'status',
            label: '상태',
            options: [
              { value: 'waiting', label: '대기' },
              { value: 'processing', label: '처리 중' },
              { value: 'success', label: '성공' },
              { value: 'partial_success', label: '일부 성공' },
              { value: 'failed', label: '실패' },
            ],
          },
        ]}
        filteredEmpty={list.filteredEmpty}
        toolbarExtra={
          <Button variant="secondary" size="sm">
            오류 파일 다운로드
          </Button>
        }
      />
    </Page>
  )
}
