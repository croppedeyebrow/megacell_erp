# MegaCell ERP Backend Architecture Plan

문서 버전: v0.1  
작성일: 2026-07-20  
대상 시스템: MegaCell ERP  
기준 스택: FastAPI + React(TypeScript) + SQLite

---

## 1. 문서 목적

이 문서는 MegaCell ERP를 단순 엑셀 조회기가 아니라 회사 업무 흐름을 기준으로 확장 가능한 ERP로 만들기 위한 메뉴 구조, 백엔드 도메인 구조, SQLite 테이블 설계 방향, API 라우터 기준을 정의한다.

현재 단계에서는 SQLite를 기준 DB로 사용한다. 엑셀 파일은 초기 원장, 일괄 적재 소스, 보조 입력 자료로 취급하고, ERP 화면에서 조회/수정/승인되는 기준 데이터는 SQLite에 저장한다.

---

## 2. 전체 시스템 흐름

```text
엑셀 원장 / 기존 업무 파일
        ↓
데이터 적재 로직
        ↓
SQLite DB
        ↓
FastAPI Backend
        ↓
React Frontend
```

### 2.1 기본 원칙

- 엑셀은 원본 참고 자료와 초기 적재 소스로 사용한다.
- SQLite는 ERP의 실제 기준 DB로 사용한다.
- 사용자가 ERP에서 수정한 데이터는 별도 운영 테이블에 저장한다.
- 엑셀 재적재 시 ERP에서 수정한 값이 덮어써지지 않도록 `source_*`, `erp_*`, `audit_*` 계층을 구분한다.
- 권한은 프론트 화면 숨김이 아니라 백엔드 API에서 최종 검증한다.

---

## 3. ERP 메뉴 구조

```text
MegaCell ERP
├─ 공통 시스템
│  ├─ 로그인 / 로그아웃
│  ├─ 회원 관리
│  ├─ 부서 / 직무 / 권한 관리
│  ├─ 거래처 / 담당자 관리
│  ├─ 품목 / 제품 / 자재 마스터
│  ├─ 첨부파일 / 문서 보관
│  └─ 변경이력 / 감사 로그
│
├─ 경영관리 / 경영지원팀
│  ├─ 회계 / 재무
│  ├─ 실적 관리
│  ├─ 계약서 관리
│  ├─ 인사 관리
│  ├─ 구매 / 발주 관리
│  ├─ 재고 현황
│  ├─ 입출고 기록
│  ├─ 파트리스트 관리
│  ├─ 전기공사 입찰 / 관리
│  └─ 문서 관리
│
├─ 기술영업부
│  ├─ 고객 / 거래처 영업 관리
│  ├─ 영업기회 / 상담 이력
│  ├─ 견적 관리
│  ├─ 수주 관리
│  ├─ 주문서 / 발주서 변환
│  ├─ 납품 일정
│  └─ 매출 진행 현황
│
├─ 연구실
│  ├─ 제품 개발 관리
│  ├─ BOM 관리
│  ├─ 제품 / 자재 사양 관리
│  ├─ 파트리스트 참조
│  ├─ 시험 / 검증 기록
│  ├─ 도면 / 기술문서 관리
│  └─ 설계 변경 관리
│
├─ 현장 엔지니어
│  ├─ 설치 일정
│  ├─ 작업 지시
│  ├─ 현장 방문 기록
│  ├─ AS 접수 / 처리
│  ├─ 배터리 점검
│  ├─ 현장 사진 / 첨부파일
│  └─ 작업 보고서
│
└─ 관리자
   ├─ 전체 현황 대시보드
   ├─ 데이터 적재 관리
   ├─ 사용자 / 권한 관리
   ├─ 마스터 데이터 관리
   ├─ 시스템 로그
   └─ DB / 백업 관리
```

---

## 4. 부서별 업무 기준

### 4.1 경영관리 / 경영지원팀

경영지원팀은 회사 운영 원장과 기준 데이터를 관리한다. 구매, 발주, 재고, 입출고, 파트리스트, 계약서, 입찰, 회계/재무, 실적, 인사 관련 업무를 포함한다.

주요 메뉴:

- 회계 / 재무
- 실적 관리
- 계약서 관리
- 인사 관리
- 구매 / 발주 관리
- 재고 현황
- 입출고 기록
- 파트리스트 관리
- 전기공사 입찰 / 관리
- 문서 관리

### 4.2 기술영업부

기술영업부는 고객 접점부터 견적, 수주, 납품 일정, 매출 진행 현황까지 관리한다.

주요 메뉴:

- 고객 / 거래처 영업 관리
- 영업기회 / 상담 이력
- 견적 관리
- 수주 관리
- 주문서 / 발주서 변환
- 납품 일정
- 매출 진행 현황

### 4.3 연구실

연구실은 제품, BOM, 사양, 시험 기록, 도면, 기술문서, 설계 변경을 관리한다. 파트리스트는 직접 소유하기보다 경영지원팀이 관리하는 기준 데이터를 참조한다.

주요 메뉴:

- 제품 개발 관리
- BOM 관리
- 제품 / 자재 사양 관리
- 파트리스트 참조
- 시험 / 검증 기록
- 도면 / 기술문서 관리
- 설계 변경 관리

### 4.4 현장 엔지니어

현장 엔지니어는 설치, AS, 방문, 점검, 작업 보고를 중심으로 사용한다.

주요 메뉴:

- 설치 일정
- 작업 지시
- 현장 방문 기록
- AS 접수 / 처리
- 배터리 점검
- 현장 사진 / 첨부파일
- 작업 보고서

### 4.5 관리자

관리자는 전체 시스템 운영, 권한, 데이터 적재, 로그, 백업을 관리한다.

주요 메뉴:

- 전체 현황 대시보드
- 데이터 적재 관리
- 사용자 / 권한 관리
- 마스터 데이터 관리
- 시스템 로그
- DB / 백업 관리

---

## 5. 백엔드 도메인 구조

```text
ERP_Backend/app/
├─ main.py
├─ api/
│  ├─ dependencies.py
│  └─ v1/
│     └─ router.py
├─ core/
│  ├─ config.py
│  ├─ database.py
│  ├─ security.py
│  ├─ permissions.py
│  └─ audit.py
├─ domains/
│  ├─ identity/
│  ├─ master_data/
│  ├─ management/
│  ├─ sales/
│  ├─ research/
│  ├─ field/
│  ├─ inventory/
│  ├─ documents/
│  └─ imports/
└─ shared/
   ├─ pagination.py
   ├─ exceptions.py
   └─ date_utils.py
```

### 5.1 도메인 책임

| 도메인 | 책임 |
|---|---|
| `identity` | 로그인, 회원, 부서, 직무, 권한 |
| `master_data` | 거래처, 담당자, 제품, 자재, 품목, 파트리스트 기준 데이터 |
| `management` | 회계/재무, 실적, 계약서, 인사, 전기공사 입찰 |
| `sales` | 영업기회, 견적, 수주, 납품 일정, 매출 진행 |
| `research` | BOM, 제품 사양, 자재 사양, 시험 기록, 설계 변경 |
| `field` | 작업 지시, 설치 일정, 현장 방문, AS, 배터리 점검, 보고서 |
| `inventory` | 재고 현황, 입출고 기록, 재고 이동, 배터리 재고 |
| `documents` | 첨부파일, 문서 생성, PDF/Excel 변환, 문서 이력 |
| `imports` | 엑셀 적재, 원장 동기화, 적재 로그, 컬럼 매핑 |

---

## 6. SQLite 테이블 초안

### 6.1 공통 시스템

```text
users
roles
departments
user_roles
permissions
customers
contacts
items
products
materials
part_lists
attachments
audit_logs
```

### 6.2 경영관리 / 경영지원팀

```text
financial_records
sales_performance
purchase_performance
contracts
employees
purchase_orders
purchase_order_items
inventory_items
inventory_movements
part_lists
bids
bid_documents
management_documents
```

### 6.3 기술영업부

```text
sales_leads
sales_activities
quotations
quotation_items
sales_orders
sales_order_items
delivery_schedules
order_documents
```

### 6.4 연구실

```text
bom_headers
bom_items
product_specs
material_specs
test_reports
engineering_changes
technical_documents
```

### 6.5 현장 엔지니어

```text
work_orders
installation_jobs
site_visits
service_cases
battery_inspections
field_reports
field_attachments
```

### 6.6 데이터 적재 / 동기화

```text
source_files
source_import_runs
source_import_rows
source_column_mappings
erp_sync_state
```

---

## 7. 핵심 데이터 관계

```text
part_lists
   ├─ materials
   ├─ bom_items
   ├─ purchase_order_items
   └─ inventory_items

products
   ├─ bom_headers
   ├─ sales_order_items
   └─ product_specs

customers
   ├─ sales_leads
   ├─ quotations
   ├─ sales_orders
   ├─ contracts
   └─ service_cases

sales_orders
   ├─ delivery_schedules
   ├─ work_orders
   └─ sales_performance

work_orders
   ├─ installation_jobs
   ├─ site_visits
   └─ field_reports
```

---

## 8. API 라우터 구조

```text
/api/v1/auth
/api/v1/users
/api/v1/departments
/api/v1/master-data
/api/v1/management
/api/v1/sales
/api/v1/research
/api/v1/field
/api/v1/inventory
/api/v1/documents
/api/v1/imports
/api/v1/admin
```

### 8.1 주요 API 예시

```text
GET    /api/v1/management/contracts
POST   /api/v1/management/contracts
GET    /api/v1/management/bids
GET    /api/v1/management/part-lists
POST   /api/v1/management/part-lists

GET    /api/v1/sales/orders
POST   /api/v1/sales/orders
GET    /api/v1/sales/delivery-schedules

GET    /api/v1/research/boms
GET    /api/v1/research/product-specs
POST   /api/v1/research/engineering-changes

GET    /api/v1/field/work-orders
POST   /api/v1/field/site-visits
GET    /api/v1/field/service-cases
POST   /api/v1/field/battery-inspections

GET    /api/v1/inventory/items
GET    /api/v1/inventory/movements
POST   /api/v1/inventory/movements

POST   /api/v1/imports/excel
GET    /api/v1/imports/runs
```

---

## 9. 권한 모델

| 역할 | 기본 권한 |
|---|---|
| `admin` | 전체 조회/생성/수정/삭제/권한/백업 |
| `management` | 경영지원팀 업무 조회/생성/수정, 기준 데이터 관리 |
| `sales` | 기술영업부 업무 조회/생성/수정 |
| `research` | 연구실 업무 조회/생성/수정, 파트리스트 조회 |
| `field_engineer` | 현장 업무 조회/생성/수정, 배정된 작업 중심 |
| `viewer` | 허용된 메뉴 조회 |

### 9.1 권한 원칙

- 관리자는 모든 권한을 가진다.
- 일반 직원은 본인 부서 업무를 기본으로 접근한다.
- 파트리스트는 경영지원팀이 관리하고 연구실, 구매, 재고, BOM에서 참조한다.
- 문서 출력/PDF/Excel 생성은 별도 권한으로 관리한다.
- 금액 수정, 재고 조정, 출고 처리, 계약 삭제는 감사 로그를 필수로 남긴다.

---

## 10. 엑셀 적재 기준

### 10.1 기본 흐름

```text
엑셀 파일 등록
  ↓
시트/컬럼 분석
  ↓
컬럼 매핑
  ↓
source 테이블 원본 적재
  ↓
ERP 운영 테이블 반영
  ↓
적재 로그/오류 로그 저장
```

### 10.2 적재 원칙

- 엑셀 파일명, 시트명, 행 번호를 저장해 원본 추적이 가능해야 한다.
- 원본 값과 표준화 값을 분리한다.
- ERP에서 수정한 운영 데이터는 엑셀 재적재로 덮어쓰지 않는다.
- 중복 판단 기준은 업무별로 정의한다.
- 적재 실패 행은 삭제하지 않고 오류 로그로 남긴다.

---

## 11. 개발 순서

### 11.1 1단계: 구조 고정

- 메뉴 구조 확정
- 도메인 구조 확정
- SQLite 테이블 초안 작성
- 엑셀 파일별 업무 도메인 매핑

### 11.2 2단계: 공통 기반

- 사용자/권한 테이블 정리
- 감사 로그 구조 추가
- 첨부파일/문서 기본 구조 추가
- 데이터 적재 로그 구조 추가

### 11.3 3단계: 경영지원팀 우선 구현

- 파트리스트 관리
- 구매 / 발주 관리
- 재고 현황
- 입출고 기록
- 계약서 관리
- 전기공사 입찰 / 관리

### 11.4 4단계: 기술영업부 구현

- 고객 / 거래처 영업 관리
- 견적 관리
- 수주 관리
- 납품 일정
- 매출 진행 현황

### 11.5 5단계: 연구실 구현

- BOM 관리
- 제품 / 자재 사양 관리
- 시험 / 검증 기록
- 설계 변경 관리

### 11.6 6단계: 현장 엔지니어 구현

- 설치 일정
- 작업 지시
- 현장 방문 기록
- AS 접수 / 처리
- 배터리 점검
- 작업 보고서

---

## 12. 현재 결정 사항

- 현재 DB는 SQLite를 기준으로 한다.
- 추후 동시접속, 외부 운영, 대량 데이터, 트랜잭션 요구가 커지면 PostgreSQL 전환을 검토한다.
- 부서 기준 메뉴는 경영지원팀, 기술영업부, 연구실, 현장 엔지니어, 관리자로 구분한다.
- 경영지원팀에는 파트리스트 관리가 포함된다.
- 파트리스트는 BOM, 구매, 재고, 자재 관리에서 참조하는 기준 마스터 데이터로 사용한다.
- 프론트는 React, 백엔드는 FastAPI로 분리한다.
- 패키지 매니저는 Yarn 기준으로 운영한다.
