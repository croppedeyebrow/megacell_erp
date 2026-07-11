# ERP_Infra

배포, 실행 스크립트, Cloudflare 등 인프라 자산입니다.

## 구조

```text
ERP_Infra/
  scripts/       FastAPI 실행·배포 (기본), Legacy Streamlit 보조
  cloudflare/    Tunnel / Access
```

## 스크립트

| 루트 | 실제 경로 | 대상 |
| --- | --- | --- |
| `dev.bat` | `scripts/run_dev.bat` | FastAPI + React 동시 실행 |
| `stop_dev.bat` | `scripts/stop_dev.bat` | `:8000` / `:5173` 종료 |
| `run_server.bat` | `scripts/run_server.bat` | FastAPI `:8000` |
| `deploy.bat` / `deploy_bg.bat` | `scripts/deploy*.bat` | FastAPI |
| `run_legacy.bat` | `scripts/run_legacy_streamlit.bat` | Streamlit `:8501` |

기본 백엔드는 FastAPI입니다. Streamlit은 전환 기간 조회·대사 전용입니다.
