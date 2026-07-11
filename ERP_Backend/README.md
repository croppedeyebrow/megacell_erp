# ERP_Backend

MegaCell ERP의 **FastAPI** 백엔드입니다.  
업무 규칙, 권한, 트랜잭션, API 계약의 기준 구현체입니다.

## 구조

```text
ERP_Backend/
  app/
    main.py              FastAPI 엔트리
    api/                 HTTP 라우터 (/api/v1)
    core/                설정·보안·DB·권한
    domains/             도메인 모듈
    integrations/        Excel/PDF/스토리지 등
    workers/             장시간 작업
    tests/
  requirements.txt
  legacy/
    streamlit/           전환용 레거시 (조회 전용, 신규 쓰기 금지)
```

## 인증

- 회원가입: `POST /api/v1/auth/register`
- 로그인: `POST /api/v1/auth/login` (HttpOnly 세션 쿠키)
- 현재 사용자: `GET /api/v1/auth/me`
- 로그아웃 / 비밀번호 변경: `/api/v1/auth/logout`, `/change-password`

첫 가입 계정은 `admin`, 이후는 `staff` 권한입니다.  
로컬 DB 기본값: `ERP_Backend/instance/megacell.db` (SQLite)

## 실행

```bash
cd ERP_Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

또는 저장소 루트 `run_server.bat` / `dev.bat`

- API: http://localhost:8000/docs

## 레거시 Streamlit

병행 운영·대사 검증이 필요할 때만 사용합니다.

```bat
run_legacy.bat
```

경로: `ERP_Backend/legacy/streamlit`
