import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  hint?: string
  error?: string
  requiredMark?: boolean
  hideLabel?: boolean
  trailing?: ReactNode
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  (
    {
      id,
      label,
      hint,
      error,
      requiredMark,
      hideLabel,
      className,
      trailing,
      required,
      ...props
    },
    ref,
  ) => {
    const fieldId = id ?? props.name
    const errorId = error && fieldId ? `${fieldId}-error` : undefined
    const hintId = hint && fieldId ? `${fieldId}-hint` : undefined

    return (
      <div className="field">
        <label
          htmlFor={fieldId}
          className={cn('field__label', hideLabel && 'sr-only')}
        >
          {label}
          {(required || requiredMark) && <span className="required">*</span>}
        </label>
        <div style={{ position: 'relative' }}>
          <input
            ref={ref}
            id={fieldId}
            className={cn('input', error && 'input--error', className)}
            aria-invalid={!!error}
            aria-describedby={[hintId, errorId].filter(Boolean).join(' ') || undefined}
            required={required}
            {...props}
          />
          {trailing}
        </div>
        {hint && !error && (
          <span id={hintId} className="field__hint">
            {hint}
          </span>
        )}
        {error && (
          <span id={errorId} className="field__error" role="alert">
            {error}
          </span>
        )}
      </div>
    )
  },
)

TextField.displayName = 'TextField'
