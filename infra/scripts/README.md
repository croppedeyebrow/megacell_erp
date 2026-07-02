# infra/scripts

운영 PC에서 ERP 서버를 실행, 종료, 배포하기 위한 배치 파일을 보관합니다.

## 파일 역할

- `run_server.bat`: 현재 CMD 창에서 Streamlit 서버 실행
- `start_server_bg.bat`: Streamlit 서버를 백그라운드로 실행
- `run_server_logged.bat`: 로그 파일로 출력하면서 Streamlit 서버 실행
- `stop_server.bat`: `8501` 포트에서 실행 중인 ERP 서버만 종료
- `status_server.bat`: `8501` 포트 서버 실행 여부 확인
- `deploy.bat`: `git pull` 후 현재 CMD 창에서 서버 재실행
- `deploy_bg.bat`: `git pull` 후 백그라운드로 서버 재실행

운영에서는 보통 루트의 `deploy_bg.bat`을 사용합니다.
