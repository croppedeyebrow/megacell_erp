import { useMemo, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Page } from '@/components/layout/AppShell'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable } from '@/components/data/DataTable'
import {
  Alert,
  Button,
  ConfirmDialog,
  DescriptionList,
  Panel,
  StatusBadge,
  Tabs,
  TextArea,
  TextField,
  Select,
  useToast,
} from '@/components/ui'
import { MOCK_ORDERS } from '@/mocks/data'
import { useClientList } from '@/hooks/useClientList'
import { formatCurrency, formatDate, formatQuantity } from '@/lib/format'
import { useAuth } from '@/auth/AuthContext'

const STATUS_FILTER = {
  id: 'status',
  label: '상태',
  options: [
    { value: 'draft', label: '초안' },
    { value: 'confirmed', label: '확정' },
    { value: 'in_progress', label: '진행 중' },
    { value: 'delayed', label: '지연' },
    { value: 'completed', label: '완료' },
    { value: 'cancelled', label: '취소' },
  ],
}

export function OrdersPage() {
  const navigate = useNavigate()
  const { hasPermission } = useAuth()
  const list = useClientList(
    MOCK_ORDERS,
    [
      (r) => r.orderNo,
      (r) => r.customer,
      (r) => r.product,
      (r) => r.owner,
    ],
    { status: (r) => r.status },
  )

  return (
    <Page>
      <PageHeader
        title="수주"
        description="수주 목록을 검색·필터하고 상세로 이동합니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '영업' },
          { label: '수주' },
        ]}
        actions={
          hasPermission('sales.edit')
            ? [{ label: '수주 등록', variant: 'primary', to: '/sales/orders/new' }]
            : undefined
        }
      />
      <DataTable
        columns={[
          { id: 'orderNo', header: '수주번호', accessor: (r) => r.orderNo, sortable: true },
          { id: 'customer', header: '거래처', accessor: (r) => r.customer, sortable: true },
          { id: 'product', header: '품목', accessor: (r) => r.product },
          {
            id: 'quantity',
            header: '수량',
            accessor: (r) => formatQuantity(r.quantity, 'EA'),
            align: 'right',
          },
          {
            id: 'amount',
            header: '금액 (VAT 별도)',
            accessor: (r) => formatCurrency(r.amount),
            align: 'right',
            sortable: true,
          },
          {
            id: 'dueDate',
            header: '납기',
            accessor: (r) => formatDate(r.dueDate),
            sortable: true,
          },
          {
            id: 'status',
            header: '상태',
            accessor: (r) => <StatusBadge code={r.status} />,
          },
          { id: 'owner', header: '담당자', accessor: (r) => r.owner },
        ]}
        rows={list.items}
        total={list.total}
        rowKey={(r) => r.id}
        filters={[STATUS_FILTER]}
        filteredEmpty={list.filteredEmpty}
        getRowHref={(r) => `/sales/orders/${r.id}`}
        emptyTitle="수주가 없습니다"
        emptyDescription="첫 수주를 등록하면 목록에 표시됩니다."
        emptyActionLabel={hasPermission('sales.edit') ? '수주 등록' : undefined}
        onEmptyAction={() => navigate('/sales/orders/new')}
        toolbarExtra={
          hasPermission('report.export') ? (
            <Button variant="secondary" size="sm">
              내보내기
            </Button>
          ) : null
        }
      />
    </Page>
  )
}

export function OrderDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { hasPermission } = useAuth()
  const [tab, setTab] = useState('overview')
  const [cancelOpen, setCancelOpen] = useState(false)
  const [reason, setReason] = useState('')
  const order = useMemo(
    () => MOCK_ORDERS.find((o) => o.id === id) ?? MOCK_ORDERS[0],
    [id],
  )

  if (!order) {
    return (
      <Page>
        <Alert tone="danger" title="수주를 찾을 수 없습니다">
          요청한 수주가 없거나 권한이 없습니다.
        </Alert>
      </Page>
    )
  }

  return (
    <Page>
      <PageHeader
        title={order.orderNo}
        status={<StatusBadge code={order.status} />}
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '영업' },
          { label: '수주', to: '/sales/orders' },
          { label: order.orderNo },
        ]}
        meta={
          <>
            <span>
              거래처 <strong>{order.customer}</strong>
            </span>
            <span>
              담당자 <strong>{order.owner}</strong>
            </span>
            <span>
              납기 <strong>{formatDate(order.dueDate)}</strong>
            </span>
            <span>
              금액 <strong>{formatCurrency(order.amount, { vatIncluded: false })}</strong>
            </span>
          </>
        }
        actions={[
          ...(hasPermission('sales.edit') && order.status !== 'cancelled'
            ? [
                {
                  label: '수정',
                  variant: 'secondary' as const,
                  to: `/sales/orders/${order.id}/edit`,
                },
              ]
            : []),
          ...(order.status === 'confirmed' || order.status === 'in_progress'
            ? [
                {
                  label: '출고 요청',
                  variant: 'primary' as const,
                  to: '/sales/shipment-requests',
                },
              ]
            : []),
          ...(hasPermission('sales.edit') &&
          order.status !== 'cancelled' &&
          order.status !== 'completed'
            ? [
                {
                  label: '수주 취소',
                  variant: 'danger' as const,
                  onClick: () => setCancelOpen(true),
                },
              ]
            : []),
        ]}
      />

      <Tabs
        tabs={[
          { id: 'overview', label: '개요' },
          { id: 'items', label: '품목' },
          { id: 'links', label: '연결 업무' },
          { id: 'docs', label: '문서' },
          { id: 'history', label: '변경 이력' },
        ]}
        value={tab}
        onChange={setTab}
      />

      {tab === 'overview' && (
        <Panel>
          <DescriptionList
            items={[
              { label: '수주번호', value: order.orderNo },
              { label: '거래처', value: order.customer },
              { label: '품목', value: order.product },
              { label: '수량', value: formatQuantity(order.quantity, 'EA') },
              {
                label: '금액',
                value: formatCurrency(order.amount, { vatIncluded: false }),
              },
              { label: '납기', value: formatDate(order.dueDate) },
              { label: '상태', value: <StatusBadge code={order.status} /> },
              { label: '담당자', value: order.owner },
            ]}
          />
        </Panel>
      )}

      {tab === 'items' && (
        <Panel title="품목">
          <table className="data-table">
            <thead>
              <tr>
                <th>품목</th>
                <th className="cell-right">수량</th>
                <th className="cell-right">단가</th>
                <th className="cell-right">금액</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{order.product}</td>
                <td className="cell-right">{formatQuantity(order.quantity, 'EA')}</td>
                <td className="cell-right">
                  {formatCurrency(Math.round(order.amount / order.quantity))}
                </td>
                <td className="cell-right">{formatCurrency(order.amount)}</td>
              </tr>
            </tbody>
          </table>
        </Panel>
      )}

      {tab === 'links' && (
        <Panel title="연결 업무">
          <ul className="list-plain">
            <li>
              <Link to="/production/requests">생산 요청 PR-2026-0088</Link>
            </li>
            <li>
              <Link to="/inventory/shipments">출고 SH-2026-0051</Link>
            </li>
          </ul>
        </Panel>
      )}

      {tab === 'docs' && (
        <Panel title="문서">
          <p style={{ color: 'var(--color-neutral-500)' }}>첨부된 문서가 없습니다.</p>
        </Panel>
      )}

      {tab === 'history' && (
        <Panel title="변경 이력">
          <ul className="list-plain">
            <li>
              <div>
                <strong>상태</strong> 초안 → 확정
                <div style={{ fontSize: 12, color: 'var(--color-neutral-500)' }}>
                  사유: 고객 발주 확정 · {order.owner}
                </div>
              </div>
              <span style={{ fontSize: 12, color: 'var(--color-neutral-500)' }}>
                2026-07-09 14:20
              </span>
            </li>
          </ul>
        </Panel>
      )}

      <ConfirmDialog
        open={cancelOpen}
        title="수주 취소"
        confirmLabel="수주 취소"
        onClose={() => setCancelOpen(false)}
        onConfirm={() => {
          if (!reason.trim()) {
            toast('취소 사유를 입력하세요.', 'warning')
            return
          }
          setCancelOpen(false)
          toast(`${order.orderNo} 수주가 취소되었습니다.`, 'success')
          navigate('/sales/orders')
        }}
      >
        <p>
          <strong>{order.orderNo}</strong> ({order.customer}) 수주를 취소합니다.
        </p>
        <p>취소 후 새 생산·출고 요청을 만들 수 없습니다. 이 작업은 되돌릴 수 없습니다.</p>
        <TextArea
          label="취소 사유"
          required
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          style={{ marginTop: 12 }}
        />
      </ConfirmDialog>
    </Page>
  )
}

export function OrderFormPage() {
  const { id } = useParams()
  const isEdit = Boolean(id && id !== 'new')
  const navigate = useNavigate()
  const { toast } = useToast()
  const existing = MOCK_ORDERS.find((o) => o.id === id)
  const [customer, setCustomer] = useState(existing?.customer ?? '')
  const [product, setProduct] = useState(existing?.product ?? '')
  const [quantity, setQuantity] = useState(String(existing?.quantity ?? ''))
  const [amount, setAmount] = useState(String(existing?.amount ?? ''))
  const [dueDate, setDueDate] = useState(existing?.dueDate ?? '')
  const [memo, setMemo] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const validate = () => {
    const next: Record<string, string> = {}
    if (!customer.trim()) next.customer = '거래처를 입력하세요.'
    if (!product.trim()) next.product = '품목을 입력하세요.'
    if (!quantity || Number(quantity) <= 0) next.quantity = '수량은 1 이상이어야 합니다.'
    if (!amount || Number(amount) < 0) next.amount = '금액을 확인하세요.'
    if (!dueDate) next.dueDate = '납기를 선택하세요.'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const onSubmit = async (e: FormEvent, draft = false) => {
    e.preventDefault()
    if (!validate()) {
      toast('입력값을 확인하세요.', 'warning')
      return
    }
    setLoading(true)
    await new Promise((r) => setTimeout(r, 500))
    setLoading(false)
    toast(draft ? '임시 저장되었습니다.' : '수주가 저장되었습니다.', 'success')
    navigate(isEdit ? `/sales/orders/${id}` : '/sales/orders')
  }

  return (
    <Page narrow>
      <PageHeader
        title={isEdit ? '수주 수정' : '수주 등록'}
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '영업' },
          { label: '수주', to: '/sales/orders' },
          { label: isEdit ? '수정' : '등록' },
        ]}
      />
      {Object.keys(errors).length > 0 && (
        <Alert tone="danger" title="입력 오류">
          표시된 필드를 수정한 뒤 다시 저장하세요.
        </Alert>
      )}
      <form
        className="panel"
        onSubmit={(e) => onSubmit(e, false)}
        style={{ marginTop: 16 }}
      >
        <h2 className="section-title">기본 정보</h2>
        <div className="form-grid">
          <TextField
            label="거래처"
            required
            value={customer}
            error={errors.customer}
            onChange={(e) => setCustomer(e.target.value)}
          />
          <TextField
            label="품목"
            required
            value={product}
            error={errors.product}
            onChange={(e) => setProduct(e.target.value)}
          />
          <TextField
            label="수량"
            type="number"
            required
            value={quantity}
            error={errors.quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
          <TextField
            label="금액 (VAT 별도)"
            type="number"
            required
            value={amount}
            error={errors.amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <TextField
            label="납기"
            type="date"
            required
            value={dueDate}
            error={errors.dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
          <Select
            label="담당자"
            options={[
              { value: '이재성', label: '이재성' },
              { value: '김영업', label: '김영업' },
            ]}
            defaultValue="이재성"
          />
        </div>
        <div style={{ marginTop: 24 }}>
          <TextArea
            label="메모"
            value={memo}
            onChange={(e) => setMemo(e.target.value)}
          />
        </div>
        <div className="form-actions">
          <Button variant="ghost" type="button" onClick={() => navigate(-1)}>
            취소
          </Button>
          <Button
            variant="secondary"
            type="button"
            loading={loading}
            onClick={(e) => onSubmit(e as unknown as FormEvent, true)}
          >
            임시 저장
          </Button>
          <Button variant="primary" type="submit" loading={loading}>
            저장
          </Button>
        </div>
      </form>
    </Page>
  )
}
