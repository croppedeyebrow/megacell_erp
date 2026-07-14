import { useState, type FormEvent, type ReactNode } from 'react'
import { Link, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { getErrorMessage, useAuth } from '@/auth/AuthContext'
import { Alert, Button, TextField, useToast } from '@/components/ui'
import { Page } from '@/components/layout/AppShell'
import { PageHeader } from '@/components/layout/PageHeader'
import logo from '@/assets/Logo_MEGACELL_shadow_A_En.png'

function AuthShell({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: ReactNode
}) {
  return (
    <div className="auth-layout">
      <div className="auth-card">
        <div className="auth-card__brand">
          <img src={logo} alt="MegaCell Co., Ltd." className="auth-card__logo-img" />
        </div>
        <h1>{title}</h1>
        <p>{description}</p>
        {children}
      </div>
    </div>
  )
}

export function LoginPage() {
  const { login, isAuthenticated, bootstrapping } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const { toast } = useToast()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  if (bootstrapping) {
    return <AuthShell title="로그인" description="세션 확인 중…"><p>불러오는 중…</p></AuthShell>
  }

  if (isAuthenticated) {
    const from = (location.state as { from?: string } | null)?.from ?? '/'
    return <Navigate to={from} replace />
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(email, password)
      toast('로그인되었습니다.', 'success')
      const from = (location.state as { from?: string } | null)?.from ?? '/'
      navigate(from, { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, '로그인에 실패했습니다.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell title="로그인" description="사내 계정으로 업무 시스템에 접속합니다.">
      {error && (
        <Alert tone="danger" title="로그인 실패">
          {error}
        </Alert>
      )}
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 16, marginTop: 16 }}>
        <TextField
          label="이메일"
          name="email"
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <TextField
          label="비밀번호"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button type="submit" variant="primary" loading={loading} style={{ width: '100%' }}>
          로그인
        </Button>
      </form>
      <p style={{ marginTop: 16, fontSize: 13 }}>
        계정이 없나요? <Link to="/signup">회원가입</Link>
      </p>
    </AuthShell>
  )
}

export function SignupPage() {
  const { register, isAuthenticated, bootstrapping } = useAuth()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [department, setDepartment] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  if (bootstrapping) {
    return <AuthShell title="회원가입" description="세션 확인 중…"><p>불러오는 중…</p></AuthShell>
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (password !== confirm) {
      setError('비밀번호 확인이 일치하지 않습니다.')
      return
    }
    if (password.length < 8) {
      setError('비밀번호는 8자 이상이어야 합니다.')
      return
    }
    setLoading(true)
    try {
      await register({ email, password, name, department })
      toast('회원가입이 완료되었습니다.', 'success')
      navigate('/', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, '회원가입에 실패했습니다.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      title="회원가입"
      description="첫 가입 계정은 관리자 권한이 부여됩니다. 이후 계정은 일반 직원 권한입니다."
    >
      {error && (
        <Alert tone="danger" title="가입 실패">
          {error}
        </Alert>
      )}
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 16, marginTop: 16 }}>
        <TextField
          label="이름"
          name="name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <TextField
          label="이메일"
          name="email"
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <TextField
          label="부서"
          name="department"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
        />
        <TextField
          label="비밀번호"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          hint="8자 이상"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <TextField
          label="비밀번호 확인"
          name="confirm"
          type="password"
          autoComplete="new-password"
          required
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />
        <Button type="submit" variant="primary" loading={loading} style={{ width: '100%' }}>
          가입하기
        </Button>
      </form>
      <p style={{ marginTop: 16, fontSize: 13 }}>
        이미 계정이 있나요? <Link to="/login">로그인</Link>
      </p>
    </AuthShell>
  )
}

export function ChangePasswordPage() {
  const { changePassword } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (next !== confirm) {
      setError('새 비밀번호 확인이 일치하지 않습니다.')
      return
    }
    setLoading(true)
    try {
      await changePassword(current, next)
      toast('비밀번호가 변경되었습니다. 다시 로그인해 주세요.', 'success')
      navigate('/login', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, '변경에 실패했습니다.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Page narrow>
      <PageHeader
        title="비밀번호 변경"
        breadcrumbs={[
          { label: '홈', to: '/' },
          { label: '비밀번호 변경' },
        ]}
      />
      <div className="panel">
        {error && (
          <Alert tone="danger" title="변경 실패">
            {error}
          </Alert>
        )}
        <form onSubmit={onSubmit} className="form-grid form-grid--1" style={{ marginTop: 16 }}>
          <TextField
            label="현재 비밀번호"
            type="password"
            required
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
          />
          <TextField
            label="새 비밀번호"
            type="password"
            required
            hint="8자 이상"
            value={next}
            onChange={(e) => setNext(e.target.value)}
          />
          <TextField
            label="새 비밀번호 확인"
            type="password"
            required
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
          <div className="form-actions">
            <Button variant="ghost" type="button" onClick={() => navigate(-1)}>
              취소
            </Button>
            <Button type="submit" variant="primary" loading={loading}>
              저장
            </Button>
          </div>
        </form>
      </div>
    </Page>
  )
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, bootstrapping } = useAuth()
  const location = useLocation()

  if (bootstrapping) {
    return (
      <div className="auth-layout">
        <p>세션 확인 중…</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return children
}

export function ForbiddenPage() {
  return (
    <Page>
      <PageHeader title="권한이 없습니다" />
      <Alert tone="warning" title="접근 권한이 없습니다">
        이 메뉴를 볼 수 있는 권한이 없습니다. 필요하면 관리자에게 요청하세요.
      </Alert>
      <div style={{ marginTop: 16 }}>
        <Link to="/">홈으로 이동</Link>
      </div>
    </Page>
  )
}

export function NotFoundPage() {
  return (
    <Page>
      <PageHeader title="페이지를 찾을 수 없습니다" />
      <Alert tone="info" title="잘못된 주소">
        요청하신 화면이 없거나 이동되었습니다.
      </Alert>
      <div style={{ marginTop: 16 }}>
        <Link to="/">홈으로 이동</Link>
      </div>
    </Page>
  )
}

export function HelpPage() {
  return (
    <Page narrow>
      <PageHeader
        title="도움말"
        breadcrumbs={[{ label: '홈', to: '/' }, { label: '도움말' }]}
        description="업무 화면 사용 방법과 문의 경로를 안내합니다."
      />
      <div className="panel">
        <p>계정은 MegaCell ERP에서 직접 가입·로그인합니다. Cloudflare Access 계정과 별개입니다.</p>
        <p>위험 작업(취소·재고 조정)은 사유 입력이 필요합니다.</p>
        <p>문의: 시스템 관리자</p>
      </div>
    </Page>
  )
}
