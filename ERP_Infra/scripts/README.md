# ERP_Infra / scripts

기본 서버는 **FastAPI** (`ERP_Backend`, port `8000`)입니다.

## FastAPI + React (개발)

- `run_dev.bat` — API·Front를 각각 새 창에서 실행 (루트 `dev.bat`)
- `stop_dev.bat` — 8000·5173 포트 종료 (루트 `stop_dev.bat`)

## FastAPI만

- `run_server.bat` — 현재 창에서 uvicorn 실행
- `start_server_bg.bat` — 백그라운드 실행
- `run_server_logged.bat` — 로그 파일로 실행
- `stop_server.bat` — 8000 포트 종료
- `status_server.bat` — 8000 포트 상태
- `deploy.bat` / `deploy_bg.bat` — pull 후 FastAPI 재시작

## Legacy Streamlit

- `run_legacy_streamlit.bat` — 8501 포트 (루트 `run_legacy.bat`)

운영 기본 경로는 FastAPI입니다.
