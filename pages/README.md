# pages

Streamlit 화면 단위 렌더링 함수를 둡니다.

- `dashboard.py`: 대시보드
- `sales.py`: 영업/수주 화면
- `management.py`: 경영 요약
- `inventory.py`: 제품 재고, 재고 출납기록
- `materials.py`: 자재, BOM, 자재 발주
- `battery.py`: 배터리 관리
- `as_management.py`: AS 관리
- `document_converter.py`: 견적/발주서 PDF 변환 및 주문서 생성

각 파일은 화면을 그리는 역할만 담당하고, DB 조회/업무 계산은 `core`와 `services`를 호출합니다.
