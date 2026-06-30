# MegaCell ERP

메가셀 업무 원장을 조회하고 일부 문서 생성 업무를 자동화하기 위한 Streamlit 기반 ERP입니다.

현재 목표는 기존 엑셀 원장을 유지하면서, ERP 화면에서는 DB에 적재된 데이터를 안정적으로 조회하고 영업, 구매/자재, 재고, 배터리, AS 업무를 통합해서 확인하는 것입니다.

## 주요 기능

- 대시보드: 수주, 재고, 자재 발주, AS 현황 요약
- 영업관리: 수주/미출고 현황, 견적/발주서 기반 주문서 변환
- 구매-자재관리: 자재 현황, BOM 조회, 대수 반영 결과 확인
- 재고관리: 제품 재고, 재고 출납기록, 수요량 분석, 배터리 관리
- AS관리: AS 이력 조회

## 운영 주소

```text
https://erp.megacell-erp.com
```

Cloudflare Tunnel과 Cloudflare Access를 통해 외부 접속을 보호합니다.

## 폴더 구조

```text
megacell_erp/
├─ app.py                 Streamlit 앱 진입점
├─ config.py              경로/환경 설정
├─ init_db.py             엑셀 원장 DB 적재 스크립트
├─ requirements.txt       Python 의존성
├─ core/                  공통 DB, 포맷, 기반 로직
├─ services/              업무 데이터 처리, 변환, 조회 로직
├─ views/                 Streamlit 화면 코드
├─ utils/                 보조 유틸리티
├─ templates/             문서/출력 양식
├─ infra/                 배포, 서버 실행, Cloudflare 운영 자료
├─ docs/                  기획/운영/개발 문서
├─ data/                  업무 원장 파일, Git 제외
├─ instance/              SQLite DB 및 산출물, Git 제외
└─ logs/                  실행 로그, Git 제외
```

## 실행

운영 PC에서 서버를 실행할 때는 루트의 호출 파일을 사용합니다.

```bat
run_server.bat
```

직접 실행하려면 아래 명령을 사용합니다.

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
C:\Users\megaPC\AppData\Local\Python\bin\python.exe -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 배포

개발한 내용을 GitHub에 push한 뒤 운영 PC에서 아래 파일을 실행합니다.

```bat
deploy.bat
```

`deploy.bat`은 `git pull`, 기존 ERP 서버 종료, 최신 코드로 서버 재실행을 순서대로 처리합니다.

자세한 내용은 `docs/DEPLOYMENT.md`를 참고합니다.

## 문서

- `docs/DEPLOYMENT.md`: 배포와 운영 절차
- `docs/RUN_GUIDE.md`: 로컬 실행 가이드
- `docs/GIT_WORKFLOW.md`: Git 작업 흐름
- `docs/megacell_erp_development_plan.md`: ERP 개발 기획
- `infra/README.md`: 인프라 폴더 구조

## Git 저장소

```text
https://github.com/croppedeyebrow/megacell_erp.git
```
