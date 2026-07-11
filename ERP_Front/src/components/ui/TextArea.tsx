import { forwardRef, type TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string
  hint?: string
  error?: string
  requiredMark?: boolean
}

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ id, label, hint, error, requiredMark, className, required, ...props }, ref) => {
    const fieldId = id ?? props.name
    const errorId = error && fieldId ? `${fieldId}-error` : undefined

    return (
      <div className="field">
        <label htmlFor={fieldId} className="field__label">
          {label}
          {(required || requiredMark) && <span className="required">*</span>}
        </label>
        <textarea
          ref={ref}
          id={fieldId}
          className={cn('textarea', error && 'textarea--error', className)}
          aria-invalid={!!error}
          aria-describedby={errorId}
          required={required}
          {...props}
        />
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

TextArea.displayName = 'TextArea'
