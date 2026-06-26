# MegaCell ERP 실행 가이드

## 1. 실행

CMD 또는 PowerShell에서 아래 명령을 실행합니다.

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
C:\Users\megaPC\AppData\Local\Python\bin\python.exe -m streamlit run app.py
```

`.streamlit/config.toml`에 아래 설정이 들어 있으므로 실행 명령을 길게 쓰지 않아도 됩니다.

```toml
[server]
address = "0.0.0.0"
port = 8501
headless = true
```

## 2. 접속

서버 PC에서 접속:

```text
http://localhost:8501
```

같은 사내 네트워크의 직원 PC에서 접속:

```text
http://서버PC_IP:8501
```

예시:

```text
http://172.30.1.71:8501
```

## 3. 종료

Streamlit 실행 창에서 `Ctrl + C`를 누릅니다.

## 4. 서버 상태 확인

CMD 또는 PowerShell에서 아래 명령으로 8501 포트 사용 여부를 확인할 수 있습니다.

```powershell
Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
```

결과가 없으면 서버가 꺼진 상태입니다.

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
- 서버 실행 창을 닫거나 `Ctrl + C`를 누르면 직원 접속도 종료됩니다.
- 엑셀 원본, DB, 고객 PDF는 Git에 올리지 않습니다.
- 외부 접속을 열기 전에는 권한 구조를 먼저 적용합니다.
