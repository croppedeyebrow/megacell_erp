# docs

MegaCell ERP의 기획·설계·운영 문서를 보관합니다.  
루트에는 `README.md`만 두고, 상세 문서는 이 폴더에서 관리합니다.

## 기준 문서 (현재)

| 문서 | 내용 |
| --- | --- |
| `MEGACELL_ERP_PRODUCT_PLAN.md` | 제품 목표, 사용자, 업무 범위, MVP·로드맵 |
| `DEVELOPMENT_POLICY.md` | AI·개발자 업무·데이터·보안 정책 |
| `SYSTEM_ARCHITECTURE.md` | 시스템 구조, 모듈 경계, 데이터 흐름, 배포 |
| `UI_SYSTEM_DESIGN.md` | UI 구조, 디자인 시스템, 공통 컴포넌트 |

## 운영 가이드

| 문서 | 내용 |
| --- | --- |
| `RUN_GUIDE.md` | 로컬 실행·점검 |
| `DEPLOYMENT.md` | 운영 배포·Cloudflare |
| `GIT_WORKFLOW.md` | Git 작업 흐름 |
| `DB_STRUCTURE.md` | 레거시/DB 구조 참고 |
| `DATA_MIGRATION.md` | 레거시 SQLite → 신규 DB 이관 |

## 보관 (archive)

Streamlit MVP 시절 문서로, 현재 기준 문서와 내용이 겹칩니다.  
참고용으로만 두고 **신규 구현 기준으로 사용하지 않습니다.**

- `archive/megacell_erp_development_plan.md`
- `archive/ERP_DEVELOPMENT_SPEC.md`

ADR은 `docs/adr/`에 추가합니다.
