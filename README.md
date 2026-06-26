# MegaCell ERP

메가셀 내부 업무 데이터를 조회하고 일부 문서 생성 업무를 자동화하기 위한 Streamlit 기반 ERP입니다.

현재 목표는 기존 엑셀 원본을 유지하면서, ERP에서는 DB에 적재된 데이터를 기준으로 영업내역, 구매/자재, 재고, 배터리, AS 정보를 안정적으로 조회하는 것입니다.

## 주요 기능

- 영업관리: 수주 현황, 미출고 현황, 견적/발주서 기반 주문서 생성
- 구매-자재관리: 자재 현황, BOM 조회, 대수 반영 결과 확인
- 재고관리: 제품 재고, 재고 출납기록, 배터리 재고/입출고
- AS관리: AS 이력 조회
- 관리자 기능: 데이터 갱신, 원본 파일 상태, 동기화 로그, 권한 관리 예정

## 실행 방법

Windows에서 아래 파일을 더블클릭합니다.

```text
start_erp.bat
```

실행 후 브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:8501
```

같은 사내 네트워크의 다른 PC에서는 상태 확인 화면에 표시되는 내부 IP 주소로 접속합니다.

```text
http://서버PC_IP:8501
```

## 종료 방법

```text
stop_erp.bat
```

## 상태 확인

```text
erp_status.bat
```

상태 확인 스크립트는 서버 실행 여부, PID, 접속 주소, 로그 위치를 보여줍니다.

자동 점검용 옵션:

```powershell
start_erp.bat --no-pause --no-browser
erp_status.bat --no-pause
stop_erp.bat --no-pause
```

## 개발 환경

필수 Python 패키지는 `requirements.txt`에 정리되어 있습니다.

```powershell
pip install -r requirements.txt
```

직접 실행할 경우:

```powershell
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

## 데이터 원본

실제 엑셀 원본, DB, PDF, 로그 파일은 Git에 포함하지 않습니다.

Git에 포함하지 않는 주요 파일:

- `*.db`
- `*.xls`, `*.xlsx`, `*.xlsm`, `*.xlsb`
- `*.pdf`
- `logs/`
- `backup*/`
- `.env`
- `.streamlit/secrets.toml`

## Git 운영

현재 저장소:

```text
https://github.com/croppedeyebrow/megacell_erp.git
```

기본 흐름:

```powershell
git status
git add 변경파일
git commit -m "작업 내용"
git push
```

민감 파일은 `.gitignore`로 제외한 뒤 커밋합니다.

## 운영 방향

1. 로컬 실행 안정화
2. 조회용 ERP 화면 정리
3. 권한 구조 추가
4. 엑셀 원본 -> DB 동기화 안정화
5. Cloudflare Tunnel + Access 기반 외부 조회 테스트
6. 일부 업무의 ERP 직접 입력 기능 검토
