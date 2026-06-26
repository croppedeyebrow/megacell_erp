# Megacell ERP Git 운영 가이드

## Git 아이디가 필요한 경우

로컬 PC에서 변경 이력만 남길 때는 GitHub 아이디가 꼭 필요하지 않습니다.

GitHub 또는 GitLab에 백업 저장소를 만들고 업로드할 때는 해당 서비스 계정 로그인이 필요합니다.

비밀번호, 토큰, 복구코드는 Codex나 다른 사람에게 전달하지 않습니다. 로그인은 브라우저 또는 Git Credential Manager에서 직접 진행합니다.

## Git에 포함할 파일

- `app.py`
- `init_db.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `README.md`
- `RUN_GUIDE.md`
- `GIT_WORKFLOW.md`
- 개발 기획서
- 샘플 템플릿 파일

## Git에서 제외할 파일

- 실제 DB 파일: `*.db`
- 실제 엑셀 원본: `*.xls`, `*.xlsx`, `*.xlsm`, `*.xlsb`
- 고객 PDF
- 생성된 문서
- 로그 파일
- 백업 폴더
- Cloudflare 인증 정보
- `.env`, `.streamlit/secrets.toml`

## 실행 기준

배치 파일은 사용하지 않습니다.

개발 중 실행:

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
C:\Users\megaPC\AppData\Local\Python\bin\python.exe -m streamlit run app.py
```

서버 설정은 `.streamlit/config.toml`에서 관리합니다.

## 권장 브랜치

초기에는 단순하게 운영합니다.

```text
master
  - 실제 운영 가능한 안정 버전

feature/*
  - 기능별 작업
```

## 커밋 메시지 예시

```text
feat: 사용자 권한 그룹 추가
fix: 재고 데이터 적재 오류 수정
docs: 개발 기획서 추가
chore: 실행 방식 정리
```

## 원격 저장소

```text
https://github.com/croppedeyebrow/megacell_erp.git
```

실제 고객 문서, 엑셀 원본, DB 파일은 원격 저장소에 올리지 않습니다.
