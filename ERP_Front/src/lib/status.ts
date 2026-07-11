export type StatusTone =
  | 'neutral'
  | 'info'
  | 'primary'
  | 'warning'
  | 'success'
  | 'danger'

export interface StatusMeta {
  code: string
  label: string
  tone: StatusTone
}

/** API code → 한국어 display label + tone 매핑 */
export const STATUS_MAP: Record<string, StatusMeta> = {
  draft: { code: 'draft', label: '초안', tone: 'neutral' },
  pending: { code: 'pending', label: '대기', tone: 'info' },
  requested: { code: 'requested', label: '요청', tone: 'info' },
  in_progress: { code: 'in_progress', label: '진행 중', tone: 'primary' },
  confirmed: { code: 'confirmed', label: '확정', tone: 'primary' },
  delayed: { code: 'delayed', label: '지연', tone: 'warning' },
  shortage: { code: 'shortage', label: '부족', tone: 'warning' },
  completed: { code: 'completed', label: '완료', tone: 'success' },
  shipped: { code: 'shipped', label: '출고 완료', tone: 'success' },
  cancelled: { code: 'cancelled', label: '취소', tone: 'danger' },
  failed: { code: 'failed', label: '실패', tone: 'danger' },
  blocked: { code: 'blocked', label: '차단', tone: 'danger' },
  partial_success: { code: 'partial_success', label: '일부 성공', tone: 'warning' },
  waiting: { code: 'waiting', label: '대기', tone: 'info' },
  processing: { code: 'processing', label: '처리 중', tone: 'primary' },
  success: { code: 'success', label: '성공', tone: 'success' },
  active: { code: 'active', label: '활성', tone: 'success' },
  inactive: { code: 'inactive', label: '비활성', tone: 'neutral' },
  assigned: { code: 'assigned', label: '배정', tone: 'primary' },
  closed: { code: 'closed', label: '종결', tone: 'success' },
  received: { code: 'received', label: '접수', tone: 'info' },
}

export function resolveStatus(code: string): StatusMeta {
  return (
    STATUS_MAP[code] ?? {
      code,
      label: code,
      tone: 'neutral' as StatusTone,
    }
  )
}
