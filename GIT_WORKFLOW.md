# Megacell ERP Git 운영 가이드

## Git 아이디가 필요한 경우

로컬 PC에서 변경 이력만 남길 때는 GitHub 아이디가 꼭 필요하지 않습니다.

다만 커밋 작성자 정보는 필요합니다.

```powershell
git config --global user.name "Megacell ERP"
git config --global user.email "your-email@example.com"
```

GitHub 또는 GitLab에 백업 저장소를 만들고 업로드할 때는 해당 서비스 계정 로그인이 필요합니다.

비밀번호, 토큰, 복구코드는 Codex나 다른 사람에게 전달하지 않습니다. 로그인은 브라우저 또는 Git Credential Manager에서 직접 진행합니다.

## Git에 포함할 파일

- `app.py`
- `init_db.py`
- `requirements.txt`
- `start_erp.bat`
- `stop_erp.bat`
- `erp_status.bat`
- `RUN_GUIDE.md`
- `README.md`
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

## 초기 설정 순서

Git 설치 후 아래 순서로 진행합니다.

```powershell
cd C:\Users\megaPC\Desktop\megacell_erp
git init
git status
git add .gitignore README.md RUN_GUIDE.md requirements.txt app.py init_db.py start_erp.bat stop_erp.bat erp_status.bat firewall_allow_8501_admin.bat megacell_erp_development_plan.md GIT_WORKFLOW.md
git commit -m "chore: initialize megacell erp project"
```

## 권장 브랜치

초기에는 단순하게 운영합니다.

```text
main
  - 실제 운영 가능한 안정 버전

dev
  - 개발 통합 버전

feature/*
  - 기능별 작업
```

## 커밋 메시지 예시

```text
feat: 사용자 권한 그룹 추가
fix: 재고 데이터 적재 오류 수정
docs: 개발 기획서 추가
chore: 실행 스크립트 정리
```

## 원격 저장소 추천

1. GitHub Private 저장소
2. GitLab Private 저장소
3. NAS 내부 Git 저장소

추천은 `GitHub Private 또는 GitLab Private + NAS 백업`입니다.

실제 고객 문서, 엑셀 원본, DB 파일은 원격 저장소에 올리지 않습니다.
