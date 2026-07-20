# MegaCell ERP 실행 가이드

## 1. Front + Backend 한 번에 (권장)

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
dev.bat
```

- API: http://localhost:8000/docs
- Front: http://localhost:5173

종료:

```bat
stop_dev.bat
```

## 2. FastAPI만

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
run_server.bat
```

또는:

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp\ERP_Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

접속: http://localhost:8000/docs  
종료: `Ctrl + C` 또는 `stop_server.bat`

## 3. React Front만

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp\ERP_Front
yarn dev
```

접속: http://localhost:5173

## 4. Legacy Streamlit (전환용)

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
run_legacy.bat
```

접속: http://localhost:8501  
신규 업무 쓰기는 FastAPI로만 수행합니다.

## 5. 외부 접속

Cloudflare Tunnel/Access는 점진적으로 FastAPI(+정적 Front)를 바라보도록 전환합니다.  
공유기 포트 직접 개방은 권장하지 않습니다.
