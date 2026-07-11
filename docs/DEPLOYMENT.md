# MegaCell ERP Deployment

## 배포 구조

현재 ERP의 **기본 백엔드는 FastAPI**입니다. 회사 PC에서 API를 실행하고, React Front와 Cloudflare Tunnel/Access로 접근하는 구조로 전환합니다. Streamlit은 레거시 조회용으로만 유지합니다.

```text
GitHub repository
  -> 회사 PC: megacell_erp
  -> FastAPI: http://localhost:8000
  -> React Front: http://localhost:5173 (개발) / 정적 배포
  -> Cloudflare Tunnel
  -> https://erp.megacell-erp.com
```

## 운영 주소

```text
https://erp.megacell-erp.com
```

## 관련 파일

```text
ERP_Infra/scripts/run_server.bat
ERP_Infra/scripts/stop_server.bat
ERP_Infra/scripts/deploy.bat
ERP_Infra/scripts/deploy_bg.bat
ERP_Infra/scripts/start_server_bg.bat
ERP_Infra/scripts/status_server.bat
```

루트의 `run_server.bat`, `stop_server.bat`, `deploy.bat`은 위 실제 스크립트를 호출하는 바로가기입니다.

## 일반 실행

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
run_server.bat
```

## 서버 종료

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
stop_server.bat
```

`stop_server.bat`은 `8000` 포트에서 실행 중인 FastAPI 서버만 종료합니다.


## 반자동 배포

개발한 내용을 GitHub에 push한 뒤, 운영 PC에서 아래 파일을 실행합니다.

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
deploy_bg.bat
```

`deploy_bg.bat`은 CMD 창을 점유하지 않고 백그라운드로 서버를 실행합니다.

수동 확인용으로 현재 창에서 서버 로그를 보면서 실행하려면 `deploy.bat`을 사용합니다.

배포 스크립트는 다음 순서로 동작합니다.

```text
1. git pull
2. 8000 포트의 기존 FastAPI 서버 종료
3. 최신 코드로 FastAPI 재실행
```

## DB 재적재

엑셀 원장을 갱신해서 DB를 다시 만들 때는 운영 PC에서 아래 명령을 실행합니다.

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp\ERP_Backend\legacy\streamlit
C:\Users\megaPC\AppData\Local\Python\bin\python.exe init_db.py
```

레거시 SQLite 재적재용입니다. 신규 원장은 PostgreSQL + Alembic 마이그레이션을 사용합니다.

## Cloudflare 설정

Cloudflare 관련 값은 `ERP_Infra/cloudflare/README.md`에 기록합니다.


## Git 관리 원칙

- 코드는 GitHub에 올립니다.
- 업무 원장, SQLite DB, 로그, PDF, 엑셀 파일은 GitHub에 올리지 않습니다.
- 운영 PC에서는 GitHub에서 코드를 `pull`하고, 실제 업무 파일은 `data/` 또는 지정한 데이터 폴더에 따로 배치합니다.

## 로그 확인

```text
ERP_Backend/logs/server.log
ERP_Backend/logs/deploy.log
```

`server.log`에는 FastAPI 실행 로그가 남고, `deploy.log`에는 배포 실행 이력이 남습니다.
