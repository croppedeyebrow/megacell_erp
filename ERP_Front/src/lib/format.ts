const currencyFormatter = new Intl.NumberFormat('ko-KR')
const numberFormatter = new Intl.NumberFormat('ko-KR')

/** Asia/Seoul 기준 날짜 YYYY-MM-DD */
export function formatDate(value?: string | Date | null): string {
  if (!value) return '—'
  const date = typeof value === 'string' ? new Date(value) : value
  if (Number.isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date)
}

/** Asia/Seoul 기준 시각 YYYY-MM-DD HH:mm */
export function formatDateTime(value?: string | Date | null): string {
  if (!value) return '—'
  const date = typeof value === 'string' ? new Date(value) : value
  if (Number.isNaN(date.getTime())) return '—'
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(date)
  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((p) => p.type === type)?.value ?? ''
  return `${get('year')}-${get('month')}-${get('day')} ${get('hour')}:${get('minute')}`
}

export function formatCurrency(
  amount?: number | null,
  options?: { vatIncluded?: boolean; withSymbol?: boolean },
): string {
  if (amount == null || Number.isNaN(amount)) return '—'
  const formatted = currencyFormatter.format(amount)
  const symbol = options?.withSymbol === false ? '' : '₩'
  const base = symbol ? `${symbol}${formatted}` : `${formatted}원`
  if (options?.vatIncluded === true) return `${base} (VAT 포함)`
  if (options?.vatIncluded === false) return `${base} (VAT 별도)`
  return base
}

export function formatQuantity(value?: number | null, unit?: string): string {
  if (value == null || Number.isNaN(value)) return '—'
  const formatted = numberFormatter.format(value)
  return unit ? `${formatted} ${unit}` : formatted
}

export function todayLabel(): string {
  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  }).format(new Date())
}
