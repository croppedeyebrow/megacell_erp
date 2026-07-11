import { forwardRef, type SelectHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export interface SelectOption {
  value: string
  label: string
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string
  options: SelectOption[]
  placeholder?: string
  hint?: string
  error?: string
  requiredMark?: boolean
  hideLabel?: boolean
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      id,
      label,
      options,
      placeholder,
      hint,
      error,
      requiredMark,
      hideLabel,
      className,
      required,
      ...props
    },
    ref,
  ) => {
    const fieldId = id ?? props.name
    const errorId = error && fieldId ? `${fieldId}-error` : undefined

    return (
      <div className="field">
        <label htmlFor={fieldId} className={cn('field__label', hideLabel && 'sr-only')}>
          {label}
          {(required || requiredMark) && <span className="required">*</span>}
        </label>
        <select
          ref={ref}
          id={fieldId}
          className={cn('select', error && 'select--error', className)}
          aria-invalid={!!error}
          aria-describedby={errorId}
          required={required}
          {...props}
        >
          {placeholder && <option value="">{placeholder}</option>}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {hint && !error && <span className="field__hint">{hint}</span>}
        {error && (
          <span id={errorId} className="field__error" role="alert">
            {error}
          </span>
        )}
      </div>
    )
  },
)

Select.displayName = 'Select'
