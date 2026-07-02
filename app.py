from __future__ import annotations

import streamlit as st

from config import BASE_DIR, DB_PATH
from core.db import db_mtime, list_tables
from views.as_management import render_as_management
from views.battery import render_battery_management
from views.dashboard import render_dashboard
from views.document_converter import render_document_converter
from views.inventory import render_current_inventory, render_inventory_demand_analysis, render_inventory_history
from views.management import render_management_summary
from views.materials import render_material_purchases, render_materials_bom
from views.sales import render_sales_orders
from services.sync_service import run_db_sync


st.set_page_config(
    page_title="메가셀 ERP",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGE_GROUPS = {
    "재고관리": ["제품 재고", "배터리 재고", "재고 출납기록", "수요량 분석"],
    "영업관리": ["수주/미출고 현황", "견적/발주서 변환"],
    "구매-자재관리": ["자재/BOM", "자재 발주"],
    "AS관리": ["AS 이력"],
    "대시보드": ["대시보드"],
    "경영관리": ["경영 요약"],
}


def render_db_controls() -> None:
    with st.sidebar.expander("원장/DB 관리", expanded=False):
        st.caption(str(BASE_DIR))
        if st.button("원장 동기화", width="stretch"):
            with st.spinner("엑셀 원장을 DB로 다시 읽는 중입니다..."):
                try:
                    result = run_db_sync()
                except Exception as exc:
                    st.error(f"동기화 실행 오류: {exc}")
                else:
                    if result.returncode == 0:
                        st.cache_data.clear()
                        st.success("원장 동기화 완료")
                        with st.expander("동기화 로그"):
                            st.code(result.stdout[-4000:] or "완료")
                        st.rerun()
                    else:
                        st.error("원장 동기화 실패")
                        st.code((result.stdout + "\n" + result.stderr)[-5000:])
        if st.button("화면 새로고침", width="stretch"):
            st.cache_data.clear()
            st.rerun()


def route(menu: str, available_tables: list[str]) -> None:
    if menu == "대시보드":
        render_dashboard()
    elif menu in {"수주 현황", "수주/미출고 현황", "영업내역"}:
        render_sales_orders()
    elif menu == "경영 요약":
        render_management_summary()
    elif menu in {"재고 관리", "제품 재고"}:
        render_current_inventory()
    elif menu == "재고 출납기록":
        render_inventory_history(available_tables)
    elif menu == "수요량 분석":
        render_inventory_demand_analysis()
    elif menu in {"자재/BOM", "자재 현황", "BOM 조회"}:
        render_materials_bom()
    elif menu in {"자재 발주", "발주 필요 품목"}:
        render_material_purchases()
    elif menu in {"배터리 관리", "배터리 재고", "배터리 입출고", "미출고 달력"}:
        render_battery_management()
    elif menu in {"AS 관리", "AS 이력"}:
        render_as_management()
    elif menu in {"견적/주문서", "견적/발주서 변환"}:
        render_document_converter()
    else:
        st.error(f"알 수 없는 메뉴입니다: {menu}")


def main() -> None:
    if not DB_PATH.exists():
        st.error(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
        st.info("먼저 같은 폴더에서 `python init_db.py`를 실행해 주세요.")
        st.stop()

    st.sidebar.title("메가셀 ERP")
    st.sidebar.caption("엑셀 원장 기반 로컬 통합 조회")
    st.sidebar.divider()

    render_db_controls()

    st.sidebar.divider()
    section = st.sidebar.radio("업무영역", list(PAGE_GROUPS.keys()))
    pages = PAGE_GROUPS[section]
    menu = pages[0] if len(pages) == 1 else st.sidebar.radio("화면", pages)

    available_tables = list_tables(db_mtime())
    required_tables = ["수주", "재고", "재고출납", "AS관리", "부품리스트", "자재재고", "BOM", "발주현황"]
    missing_tables = [name for name in required_tables if name not in available_tables]
    if missing_tables:
        st.warning("DB에 아직 없는 테이블: " + ", ".join(missing_tables))

    route(menu, available_tables)


if __name__ == "__main__":
    main()
