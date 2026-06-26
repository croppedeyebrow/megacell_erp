# MegaCell ERP 실행 가이드

## 1. 서버 시작

`start_erp.bat`를 더블클릭합니다.

스크립트가 수행하는 작업:

- 이미 8501 포트에서 서버가 실행 중인지 확인
- `logs` 폴더 생성
- Streamlit 서버 실행
- 실행 로그를 `logs/streamlit.log`에 저장
- 브라우저에서 `http://localhost:8501` 열기
- 사내 접속용 IP 주소 표시

## 2. 서버 종료

`stop_erp.bat`를 더블클릭합니다.

8501 포트에서 실행 중인 ERP 서버 프로세스를 찾아 종료합니다.

## 3. 상태 확인

`erp_status.bat`를 더블클릭합니다.

확인 가능한 정보:

- 서버 실행 여부
- 실행 중인 프로세스 PID
- 로컬 접속 주소
- 사내 네트워크 접속 주소
- 로그 파일 위치
- 최근 로그 일부

자동 점검처럼 멈춤 없이 실행해야 할 때는 아래 옵션을 사용할 수 있습니다.

```powershell
erp_status.bat --no-pause
start_erp.bat --no-pause --no-browser
stop_erp.bat --no-pause
```

## 4. 직원 접속

같은 사내 네트워크에 있는 직원은 아래 형식으로 접속합니다.

```text
http://서버PC_IP:8501
```

예시:

```text
http://172.30.1.71:8501
```

직원이 접속하지 못하면 서버 PC에서 `firewall_allow_8501_admin.bat`를 관리자 권한으로 실행합니다.

## 5. 외부 접속 방향

공유기 포트를 직접 여는 방식은 권장하지 않습니다.

외부 직원 조회는 다음 구조를 목표로 합니다.

```text
Cloudflare Access 로그인
  -> Cloudflare Tunnel
  -> 사내 ERP 서버
  -> Streamlit ERP
```

## 6. 주의사항

- ERP 서버 PC가 켜져 있어야 접속할 수 있습니다.
- `stop_erp.bat`를 실행하면 직원 접속도 종료됩니다.
- 엑셀 원본, DB, 고객 PDF는 Git에 올리지 않습니다.
- 외부 접속을 열기 전에는 권한 구조를 먼저 적용합니다.
