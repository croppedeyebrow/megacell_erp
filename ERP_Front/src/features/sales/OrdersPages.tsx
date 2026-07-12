import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
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
import { formatCurrency, formatDate, formatQuantity } from '@/lib/format'
import { getErrorMessage, useAuth } from '@/auth/AuthContext'
import { salesApi, type SalesOrderDto } from '@/lib/api/sales'

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

type OrderRow = {
  id: string
  orderNo: string
  customer: string
  product: string
  quantity: number
  amount: number
  dueDate: string
  status: string
  owner: string
}

function toRow(dto: SalesOrderDto): OrderRow {
  return {
    id: dto.id,
    orderNo: dto.order_no,
    customer: dto.customer_name,
    product: dto.product_name,
    quantity: dto.quantity ?? 0,
    amount: dto.order_amount ?? 0,
    dueDate: dto.due_date ?? '',
    status: dto.status,
    owner: dto.owner_name ?? '—',
  }
}

export function OrdersPage() {
  const navigate = useNavigate()
  const { hasPermission } = useAuth()
  const { toast } = useToast()
  const [params] = useSearchParams()
  const [importing, setImporting] = useState(false)

  const page = Number(params.get('page') ?? '1') || 1
  const pageSize = Number(params.get('pageSize') ?? '20') || 20
  const q = params.get('q') ?? ''
  const status = params.get('f.status') ?? ''

  const query = useQuery({
    queryKey: ['sales-orders', page, pageSize, q, status],
    queryFn: () =>
      salesApi.list({
        page,
        pageSize,
        q: q || undefined,
        status: status || undefined,
      }),
  })

  const rows = useMemo(
    () => (query.data?.items ?? []).map(toRow),
    [query.data],
  )

  const onImport = async () => {
    if (!hasPermission('admin.manage')) return
    setImporting(true)
    try {
      const result = await salesApi.importLegacySqlite()
      toast(result.message, result.fail_count ? 'warning' : 'success')
      await query.refetch()
    } catch (err) {
      toast(getErrorMessage(err, '이관에 실패했습니다.'), 'danger')
    } finally {
      setImporting(false)
    }
  }

  return (
    <Page>
      <PageHeader
        title="수주"
        description="신규 DB(sales_orders) 기준 목록입니다. 레거시 SQLite는 이관 후 반영됩니다."
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '영업' },
          { label: '수주' },
        ]}
        actions={[
          ...(hasPermission('admin.manage')
            ? [
                {
                  label: importing ? '이관 중…' : '레거시 DB 이관',
                  variant: 'secondary' as const,
                  onClick: () => void onImport(),
                  disabled: importing,
                  loading: importing,
                },
              ]
            : []),
          ...(hasPermission('sales.edit')
            ? [{ label: '수주 등록', variant: 'primary' as const, to: '/sales/orders/new' }]
            : []),
        ]}
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
        rows={rows}
        total={query.data?.total ?? 0}
        rowKey={(r) => r.id}
        loading={query.isLoading}
        error={query.error ? getErrorMessage(query.error, '목록을 불러오지 못했습니다.') : null}
        onRetry={() => void query.refetch()}
        filters={[STATUS_FILTER]}
        filteredEmpty={!query.isLoading && (query.data?.total ?? 0) === 0 && (!!q || !!status)}
        getRowHref={(r) => `/sales/orders/${r.id}`}
        emptyTitle="수주가 없습니다"
        emptyDescription="레거시 megacell.db를 이관하거나 수주를 등록하세요."
        emptyActionLabel={hasPermission('sales.edit') ? '수주 등록' : undefined}
        onEmptyAction={() => navigate('/sales/orders/new')}
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

  const query = useQuery({
    queryKey: ['sales-order', id],
    queryFn: () => salesApi.get(id!),
    enabled: !!id,
  })

  const order = query.data

  if (query.isLoading) {
    return (
      <Page>
        <Alert tone="info" title="불러오는 중">
          수주 상세를 조회하고 있습니다.
        </Alert>
      </Page>
    )
  }

  if (query.error || !order) {
    return (
      <Page>
        <Alert tone="danger" title="수주를 찾을 수 없습니다">
          {query.error
            ? getErrorMessage(query.error, '요청한 수주가 없거나 권한이 없습니다.')
            : '요청한 수주가 없거나 권한이 없습니다.'}
        </Alert>
      </Page>
    )
  }

  return (
    <Page>
      <PageHeader
        title={order.order_no}
        status={<StatusBadge code={order.status} />}
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '영업' },
          { label: '수주', to: '/sales/orders' },
          { label: order.order_no },
        ]}
        meta={
          <>
            <span>
              거래처 <strong>{order.customer_name}</strong>
            </span>
            <span>
              담당자 <strong>{order.owner_name ?? '—'}</strong>
            </span>
            <span>
              납기 <strong>{formatDate(order.due_date)}</strong>
            </span>
            <span>
              금액{' '}
              <strong>
                {formatCurrency(order.order_amount, { vatIncluded: false })}
              </strong>
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
              { label: '수주번호', value: order.order_no },
              { label: '거래처', value: order.customer_name },
              { label: '품목', value: order.product_name },
              {
                label: '수량',
                value: formatQuantity(order.quantity, order.unit ?? 'EA'),
              },
              {
                label: '금액',
                value: formatCurrency(order.order_amount, { vatIncluded: false }),
              },
              { label: '납기', value: formatDate(order.due_date) },
              { label: '상태', value: <StatusBadge code={order.status} /> },
              { label: '담당자', value: order.owner_name ?? '—' },
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
                <th className="cell-right">금액</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{order.product_name}</td>
                <td className="cell-right">
                  {formatQuantity(order.quantity, order.unit ?? 'EA')}
                </td>
                <td className="cell-right">{formatCurrency(order.order_amount)}</td>
              </tr>
            </tbody>
          </table>
        </Panel>
      )}

      {tab === 'links' && (
        <Panel title="연결 업무">
          <ul className="list-plain">
            <li>
              <Link to="/production/requests">생산 요청</Link>
            </li>
            <li>
              <Link to="/inventory/shipments">출고</Link>
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
          <p style={{ color: 'var(--color-neutral-500)' }}>
            변경 이력 API 연동은 다음 단계에서 제공합니다.
          </p>
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
          toast('수주 취소 API는 다음 단계에서 연결됩니다.', 'warning')
          navigate('/sales/orders')
        }}
      >
        <p>
          <strong>{order.order_no}</strong> ({order.customer_name}) 수주를 취소합니다.
        </p>
        <p>취소 후 새 생산·출고 요청을 만들 수 없습니다.</p>
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
  const [customer, setCustomer] = useState('')
  const [product, setProduct] = useState('')
  const [quantity, setQuantity] = useState('')
  const [amount, setAmount] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [memo, setMemo] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const detail = useQuery({
    queryKey: ['sales-order', id],
    queryFn: () => salesApi.get(id!),
    enabled: isEdit && !!id,
  })

  useEffect(() => {
    if (!detail.data) return
    setCustomer(detail.data.customer_name)
    setProduct(detail.data.product_name)
    setQuantity(String(detail.data.quantity ?? ''))
    setAmount(String(detail.data.order_amount ?? ''))
    setDueDate(detail.data.due_date ?? '')
    setMemo(detail.data.memo ?? '')
  }, [detail.data])

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
    await new Promise((r) => setTimeout(r, 300))
    setLoading(false)
    toast(
      draft
        ? '임시 저장 API는 다음 단계에서 연결됩니다.'
        : '수주 저장 API는 다음 단계에서 연결됩니다.',
      'warning',
    )
    navigate('/sales/orders')
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
      <form className="panel" onSubmit={(e) => onSubmit(e, false)} style={{ marginTop: 16 }}>
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
          <TextArea label="메모" value={memo} onChange={(e) => setMemo(e.target.value)} />
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
