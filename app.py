from __future__ import annotations

import streamlit as st

from config import BASE_DIR, DB_PATH
from core.db import db_mtime, list_tables
from pages.as_management import render_as_management
from pages.battery import render_battery_management
from pages.dashboard import render_dashboard
from pages.document_converter import render_document_converter
from pages.inventory import render_current_inventory, render_inventory_history
from pages.management import render_management_summary
from pages.materials import render_material_purchases, render_materials_bom
from pages.sales import render_sales_orders
from services.sync_service import run_db_sync


st.set_page_config(
    page_title="메가셀 ERP",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGE_GROUPS = {
    "대시보드": ["대시보드"],
    "영업관리": ["수주 현황"],
    "경영관리": ["경영 요약"],
    "구매재고관리": ["재고 관리", "재고 출납기록", "자재/BOM", "자재 발주"],
    "배터리관리": ["배터리 관리"],
    "AS관리": ["AS 관리"],
    "문서출력": ["견적/주문서"],
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
    elif menu == "수주 현황":
        render_sales_orders()
    elif menu == "경영 요약":
        render_management_summary()
    elif menu == "재고 관리":
        render_current_inventory()
    elif menu == "재고 출납기록":
        render_inventory_history(available_tables)
    elif menu == "자재/BOM":
        render_materials_bom()
    elif menu == "자재 발주":
        render_material_purchases()
    elif menu == "배터리 관리":
        render_battery_management()
    elif menu == "AS 관리":
        render_as_management()
    elif menu == "견적/주문서":
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
