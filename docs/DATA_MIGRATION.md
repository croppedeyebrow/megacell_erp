# 레거시 SQLite → 신규 DB 이관

## 현재 상태

| DB | 역할 |
| --- | --- |
| Streamlit `legacy/streamlit/instance/megacell.db` | 엑셀 적재 + `erp_orders` 등 운영 테이블 |
| FastAPI `ERP_Backend/instance/megacell.db` | 신규 원장 (identity + `sales_orders`) |

신규 화면의 수주 목록은 **`sales_orders`** 를 봅니다.  
엑셀/레거시 SQLite 데이터는 이관 후에야 보입니다.

## 1차 이관 범위

- 소스: 레거시 `erp_orders`
- staging: `stg_erp_orders` (원본 보존)
- 반영: `sales_orders` (`source_key` 기준 upsert, 재실행 가능)
- `erp_modified=1` 인 신규 원장 건은 덮어쓰지 않음

재고·배터리·AS·엑셀 raw 테이블은 다음 슬라이스입니다.

## 준비

운영 PC의 Streamlit DB를 복사합니다.

```text
ERP_Backend/legacy/streamlit/instance/megacell.db
```

## 실행

```bat
cd ERP_Backend
import_legacy.bat
```

또는 경로 지정:

```bat
import_legacy.bat "C:\path\to\megacell.db"
```

관리자 로그인 후 수주 화면의 **레거시 DB 이관** 버튼으로도 실행할 수 있습니다.

## 확인

- API: `GET /api/v1/sales-orders`
- UI: `/sales/orders`
- 이관 결과: `import_jobs` 테이블

## 주의

- 레거시 `users`(PBKDF2)와 신규 로그인(Argon2)은 병합하지 않습니다. 신규에서 회원가입하세요.
- PostgreSQL 전환 시에도 동일 이관 스크립트를 `DATABASE_URL`만 바꿔 사용합니다.
- 양방향 동기화는 하지 않습니다. 이관 후 쓰기 주체는 신규 ERP입니다.
