# MegaCell ERP Git 운영 가이드

## 목적

GitHub에는 ERP 코드와 운영 문서만 관리합니다. 실제 업무 원장, DB, 로그, PDF, 엑셀 파일은 GitHub에 올리지 않습니다.

## Git에 올리는 것

- `app.py`, `config.py`, `init_db.py`
- `core/`, `services/`, `views/`, `utils/`
- `templates/`
- `infra/`
- `docs/`
- `README.md`
- `requirements.txt`
- `.streamlit/config.toml`

## Git에 올리지 않는 것

- 업무 원장 파일: `*.xls`, `*.xlsx`, `*.xlsm`, `*.xlsb`
- SQLite DB: `*.db`
- PDF 산출물
- `data/` 내부 실제 데이터
- `instance/` 내부 DB와 산출물
- `logs/` 내부 로그
- 백업 폴더
- `.env`, `.streamlit/secrets.toml`
- Cloudflare 토큰, 비밀번호, 인증 정보

## 기본 작업 흐름

개발 PC에서 작업 후 커밋/푸시합니다.

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
git status
git add 파일명
git commit -m "작업 내용"
git push
```

운영 PC에 최신 코드를 반영할 때는 반자동 배포 파일을 실행합니다.

```bat
cd /d C:\Users\megaPC\Desktop\megacell_erp
deploy.bat
```

`deploy.bat`은 `infra/scripts/deploy.bat`을 호출합니다.

## 브랜치 운영

초기에는 단순하게 운영합니다.

```text
master
  - 현재 운영 기준 코드

feature/*
  - 기능 단위 작업이 커질 때 사용
```

## 커밋 메시지 예시

```text
feat: 수요량 분석 화면 추가
fix: 재고 현재고 표시 오류 수정
docs: 배포 문서 정리
chore: 배포 스크립트 구조 정리
refactor: 재고 화면 모듈 분리
```

## 저장소

```text
https://github.com/croppedeyebrow/megacell_erp.git
```
