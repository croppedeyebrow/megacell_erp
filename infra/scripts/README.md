# infra/scripts

운영 PC에서 ERP 서버를 실행, 종료, 배포하기 위한 배치 파일을 보관합니다.

## 파일 역할

- `run_server.bat`: Streamlit 서버 실행
- `stop_server.bat`: `8501` 포트에서 실행 중인 ERP 서버만 종료
- `deploy.bat`: `git pull` 후 ERP 서버 재시작

루트의 `run_server.bat`, `stop_server.bat`, `deploy.bat`은 이 폴더의 실제 스크립트를 호출하는 짧은 바로가기입니다.
