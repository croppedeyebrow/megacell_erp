# services

업무 로직과 데이터 가공 로직을 둡니다.

- `document_service.py`: 견적서/발주서 PDF 추출, 주문서 xlsm 생성
- `battery_service.py`: 배터리 미출고 계산, 달력 표시 보조 로직
- `sync_service.py`: 엑셀 원본을 DB로 다시 적재하는 `init_db.py` 실행

Streamlit UI와 직접 연결되지 않는 계산/변환 로직은 이 폴더로 이동합니다.
