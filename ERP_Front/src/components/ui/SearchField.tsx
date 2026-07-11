import { Search } from 'lucide-react'
import { forwardRef, type InputHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export interface SearchFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string
  hideLabel?: boolean
}

export const SearchField = forwardRef<HTMLInputElement, SearchFieldProps>(
  ({ id, label, hideLabel = true, className, ...props }, ref) => {
    const fieldId = id ?? props.name ?? 'search'

    return (
      <div className="field" style={{ minWidth: 220, flex: 1 }}>
        <label htmlFor={fieldId} className={cn('field__label', hideLabel && 'sr-only')}>
          {label}
        </label>
        <div className="search-field">
          <Search size={16} className="search-field__icon" aria-hidden />
          <input
            ref={ref}
            id={fieldId}
            type="search"
            className={cn('input', className)}
            placeholder={props.placeholder ?? label}
            {...props}
          />
        </div>
      </div>
    )
  },
)

SearchField.displayName = 'SearchField'
