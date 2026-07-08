from __future__ import annotations

import streamlit as st

from config import ADMIN_EMAILS, ASSETS_DIR, BASE_DIR, DB_PATH
from core.db import db_mtime, list_tables
from services.sync_service import run_db_sync
from views.as_management import render_as_management
from views.battery import render_battery_management
from views.dashboard import render_dashboard
from views.document_converter import render_document_converter
from views.inventory import render_current_inventory, render_inventory_demand_analysis, render_inventory_history
from views.landing import render_department_landing, render_planned_page
from views.management import render_management_summary
from views.materials import render_material_purchases, render_materials_bom
from views.sales import render_sales_orders


st.set_page_config(
    page_title="메가셀 ERP",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)


DEPARTMENT_PAGES = {
    "홈": ["랜딩페이지"],
    "경영지원팀": [
        "재고 현황",
        "입출고 기록",
        "구매/발주 관리",
        "문서 출력",
        "거래처/정산 자료",
        "시스템 관리",
    ],
    "기술영업팀": [
        "수주/견적 현황",
        "미출고 현황",
        "견적서/주문서 변환",
        "고객/거래처 조회",
        "출고 요청",
        "AS 이력",
    ],
    "생산팀": [
        "생산 요청 현황",
        "생산 예정/진행",
        "BOM 소요량 확인",
        "부족 자재 확인",
        "검수/출고 준비",
    ],
    "연구소": [
        "제품/BOM 관리",
        "자재/배터리 마스터",
        "제품 사양 변경 이력",
        "기술 검토 자료",
    ],
    "전체 현황": [
        "업무 대시보드",
        "경영 요약",
        "수요량 분석",
    ],
}


PLANNED_PAGE_DESCRIPTIONS = {
    "거래처/정산 자료": "거래처별 문서, 주문, 정산 기준 자료를 한 곳에서 조회하는 화면입니다.",
    "시스템 관리": "데이터 적재, 권한, 실행 상태를 관리하는 운영자용 화면입니다.",
    "고객/거래처 조회": "고객사, 담당자, 거래 이력, 관련 문서를 연결해 조회하는 화면입니다.",
    "출고 요청": "영업에서 출고가 필요한 건을 생산/경영지원팀으로 넘기는 요청 화면입니다.",
    "생산 요청 현황": "영업/경영지원에서 넘어온 생산 요청을 접수 상태별로 보는 화면입니다.",
    "생산 예정/진행": "생산 예정, 조립 진행, 검수 대기 상태를 관리하는 화면입니다.",
    "검수/출고 준비": "검수 결과와 출고 준비 여부를 확인하는 생산 마감 화면입니다.",
    "자재/배터리 마스터": "자재, 배터리, 제품 기준정보를 표준화해 관리하는 화면입니다.",
    "제품 사양 변경 이력": "제품 사양과 BOM 변경 이력을 추적하는 화면입니다.",
    "기술 검토 자료": "수주 전/후 기술 검토와 특이사항을 기록하는 화면입니다.",
}


def get_login_email() -> str:
    """Read the authenticated email forwarded by Cloudflare Access."""
    headers: dict[str, str] = {}
    try:
        headers = dict(st.context.headers)
    except Exception:
        headers = {}

    normalized_headers = {str(key).lower(): str(value).strip() for key, value in headers.items()}
    for key in [
        "cf-access-authenticated-user-email",
        "x-forwarded-email",
        "x-authenticated-user-email",
    ]:
        value = normalized_headers.get(key, "")
        if value:
            return value.lower()
    return ""


def is_admin_user(email: str) -> bool:
    return bool(email and email.lower() in ADMIN_EMAILS)


def get_visible_department_pages(is_admin: bool) -> dict[str, list[str]]:
    pages = dict(DEPARTMENT_PAGES)
    if not is_admin:
        pages.pop("전체 현황", None)
    return pages


def set_navigation(department: str, page: str | None = None) -> None:
    st.session_state["selected_department"] = department
    st.session_state["selected_page"] = page or DEPARTMENT_PAGES[department][0]


def render_db_controls() -> None:
    with st.sidebar.expander("원장/DB 관리", expanded=False):
        st.caption(str(BASE_DIR))
        if st.button("원장 동기화", width="stretch"):
            with st.spinner("원장 파일을 DB로 다시 읽는 중입니다..."):
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


def route(department: str, menu: str, available_tables: list[str], visible_pages: dict[str, list[str]]) -> None:
    if department == "홈" or menu == "랜딩페이지":
        render_department_landing(visible_pages, set_navigation)
    elif menu in {"업무 대시보드"}:
        render_dashboard()
    elif menu in {"수주/견적 현황", "미출고 현황"}:
        render_sales_orders()
    elif menu == "경영 요약":
        render_management_summary()
    elif menu == "재고 현황":
        render_current_inventory()
    elif menu == "입출고 기록":
        render_inventory_history(available_tables)
    elif menu == "수요량 분석":
        render_inventory_demand_analysis()
    elif menu in {"제품/BOM 관리", "BOM 소요량 확인"}:
        render_materials_bom()
    elif menu in {"구매/발주 관리", "부족 자재 확인"}:
        render_material_purchases()
    elif menu == "자재/배터리 마스터":
        render_battery_management()
    elif menu == "AS 이력":
        render_as_management()
    elif menu in {"문서 출력", "견적서/주문서 변환"}:
        render_document_converter()
    elif menu == "시스템 관리":
        st.title("시스템 관리")
        render_db_controls()
        render_planned_page(menu, department, PLANNED_PAGE_DESCRIPTIONS[menu])
    else:
        render_planned_page(
            menu,
            department,
            PLANNED_PAGE_DESCRIPTIONS.get(menu, "부서 업무 흐름에 맞춰 추가 설계할 예정인 화면입니다."),
        )


def main() -> None:
    if not DB_PATH.exists():
        st.error(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
        st.info("먼저 같은 폴더에서 `python init_db.py`를 실행해 주세요.")
        st.stop()

    login_email = get_login_email()
    is_admin = is_admin_user(login_email)
    visible_pages = get_visible_department_pages(is_admin)

    logo_path = ASSETS_DIR / "megacell_logo.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)
    else:
        st.sidebar.title("메가셀 ERP")

    st.sidebar.caption("부서별 업무 포털")
    if login_email:
        st.sidebar.caption(f"로그인: {login_email}")
    if is_admin:
        st.sidebar.caption("권한: 관리자")
    st.sidebar.divider()

    if "selected_department" not in st.session_state:
        set_navigation("홈")

    department_names = list(visible_pages.keys())
    current_department = st.session_state.get("selected_department", "홈")
    if current_department not in department_names:
        current_department = "홈"
        st.session_state["selected_department"] = current_department

    department = st.sidebar.radio(
        "이동",
        department_names,
        index=department_names.index(current_department),
        key="selected_department",
    )

    pages = visible_pages[department]
    current_page = st.session_state.get("selected_page", pages[0])
    if current_page not in pages:
        current_page = pages[0]
        st.session_state["selected_page"] = current_page

    menu = pages[0]
    if len(pages) > 1:
        menu = st.sidebar.radio(
            "업무 화면",
            pages,
            index=pages.index(current_page),
            key="selected_page",
        )
    else:
        st.session_state["selected_page"] = menu

    if department != "홈":
        st.sidebar.divider()
        render_db_controls()

    available_tables = list_tables(db_mtime())
    required_tables = ["수주", "재고", "재고출납", "AS관리", "부품리스트", "자재재고", "BOM", "발주현황"]
    missing_tables = [name for name in required_tables if name not in available_tables]
    if missing_tables and department != "홈":
        st.warning("DB에 아직 없는 테이블: " + ", ".join(missing_tables))

    route(department, menu, available_tables, visible_pages)


if __name__ == "__main__":
    main()
