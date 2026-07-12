# MegaCell ERP 2.0

메가셀의 수주, 생산, 구매·자재, 재고·출고, 배터리, AS 업무를 하나의 흐름으로 연결하기 위한 사내 ERP 프로젝트입니다.

**백엔드: FastAPI** · **프론트: React(TypeScript)** · **원장: PostgreSQL**

## 저장소 구조

```text
ERP_Front/                 React + TypeScript UI
ERP_Backend/               FastAPI (업무 API·도메인)
  app/
  legacy/streamlit/        전환용 레거시 (조회 전용)
ERP_Infra/                 배포·실행 스크립트, Cloudflare
docs/                      기획·설계·운영 문서 (루트 MD는 README만)
```

## 로컬 실행

### Front + Backend 한 번에 (권장)

```bat
dev.bat
```

- API: http://localhost:8000/docs
- Front: http://localhost:5173

계정은 **앱에서 회원가입** 후 로그인합니다. (Cloudflare Access 계정과 별개)

첫 가입 사용자는 관리자(`admin`) 권한이 부여됩니다.

### 레거시 SQLite 수주 이관

운영 PC의 `megacell.db`를 `ERP_Backend/legacy/streamlit/instance/`에 복사한 뒤:

```bat
cd ERP_Backend
import_legacy.bat
```

상세: [`docs/DATA_MIGRATION.md`](docs/DATA_MIGRATION.md)

종료:

```bat
stop_dev.bat
```

창이 두 개 열립니다. `node_modules`가 없으면 Front 쪽에서 `npm install`을 먼저 실행합니다.

### Backend만

```bat
run_server.bat
```

### Front만

```bash
cd ERP_Front
npm run dev
```

### Legacy Streamlit (필요 시만)

```bat
run_legacy.bat
```

http://localhost:8501

## 프로젝트 문서

상세 문서는 [`docs/`](docs/)에서 관리합니다. 루트에는 이 README만 둡니다.

| 문서 | 내용 |
| --- | --- |
| [`docs/MEGACELL_ERP_PRODUCT_PLAN.md`](docs/MEGACELL_ERP_PRODUCT_PLAN.md) | 제품 목표, 범위, 로드맵 |
| [`docs/DEVELOPMENT_POLICY.md`](docs/DEVELOPMENT_POLICY.md) | 업무·데이터·보안 정책 |
| [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md) | 시스템 구조·모듈 경계 |
| [`docs/UI_SYSTEM_DESIGN.md`](docs/UI_SYSTEM_DESIGN.md) | UI 시스템·공통 컴포넌트 |

문서 목록·보관본 안내는 [`docs/README.md`](docs/README.md)를 참고하세요.

## 저장소

```text
https://github.com/croppedlemonade/megacell_erp.git
```
