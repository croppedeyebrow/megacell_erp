# repositories

DB 테이블별 조회/저장 함수를 둘 예정인 폴더입니다.

현재는 `core.db.get_table()`로 직접 테이블을 읽고 있지만, 테이블 구조가 안정화되면 다음과 같이 분리합니다.

- `sales_repo.py`: 수주/영업 테이블 조회
- `inventory_repo.py`: 제품 재고/출납 테이블 조회
- `battery_repo.py`: 배터리 테이블 조회
- `bom_repo.py`: 자재/BOM 테이블 조회

SQL이나 테이블 스키마 의존 코드는 장기적으로 이 폴더로 모읍니다.
