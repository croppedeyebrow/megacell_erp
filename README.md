# 메가셀 ERP Streamlit MVP

기존 엑셀 원장을 SQLite DB로 모아 조회하는 로컬 테스트용 ERP입니다.

## 실행

```powershell
cd C:\Users\megaPC\Documents\Codex\2026-06-17\files-mentioned-by-the-user-megacell\outputs\megacell_erp_streamlit
python -m streamlit run app.py
```

## DB 다시 만들기

원본 엑셀을 수정한 뒤 DB를 다시 만들 때 실행합니다.

```powershell
python init_db.py
```

## 포함 메뉴

- 대시보드
- 영업/수주
- 재고 관리
- 자재/BOM
- 자재 발주
- 배터리 관리
- AS 관리
- 견적/주문서 준비 화면

배터리 `.xlsb` 파일은 `pyxlsb`가 설치되어 있을 때만 자동 적재됩니다. 설치하지 않아도 나머지 메뉴는 동작합니다.
