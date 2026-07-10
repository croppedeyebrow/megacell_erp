from __future__ import annotations

import streamlit as st

from config import ASSETS_DIR, BASE_DIR, DB_PATH
from core.db import db_mtime, list_tables
from services.auth_service import CurrentUser, change_password, get_current_user, login, logout
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
from views.user_management import render_user_management


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
        "전기공사 입찰/관리",
        "정산/청구 관리",
        "매입/매출 집계",
        "거래처/계약 자료",
        "문서 발행",
        "사내 자료/양식",
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
        "사용자 관리",
        "시스템 관리",
    ],
}


PLANNED_PAGE_DESCRIPTIONS = {
    "정산/청구 관리": "청구 예정, 입금 확인, 계산서 발행 상태를 관리하는 화면입니다.",
    "매입/매출 집계": "매입/매출 실적과 정산 기준 금액을 기간별로 확인하는 화면입니다.",
    "거래처/계약 자료": "거래처별 계약, 주문, 정산 기준 자료를 한 곳에서 조회하는 화면입니다.",
    "사내 자료/양식": "사내 공통 양식과 업무 문서를 관리하는 화면입니다.",
    "시스템 관리": "데이터 적재, 권한, 실행 상태를 관리하는 운영자용 화면입니다.",
    "고객/거래처 조회": "고객사, 담당자, 거래 이력, 관련 문서를 연결해 조회하는 화면입니다.",
    "전기공사 입찰/관리": "전기 공사 입찰 공고, 현장 설명, 견적, 투찰, 낙찰 후 진행 상태를 관리하는 화면입니다.",
    "출고 요청": "영업에서 출고가 필요한 건을 생산/경영지원팀으로 넘기는 요청 화면입니다.",
    "생산 요청 현황": "영업/경영지원에서 넘어온 생산 요청을 접수 상태별로 보는 화면입니다.",
    "생산 예정/진행": "생산 예정, 조립 진행, 검수 대기 상태를 관리하는 화면입니다.",
    "검수/출고 준비": "검수 결과와 출고 준비 여부를 확인하는 생산 마감 화면입니다.",
    "자재/배터리 마스터": "자재, 배터리, 제품 기준정보를 표준화해 관리하는 화면입니다.",
    "제품 사양 변경 이력": "제품 사양과 BOM 변경 이력을 추적하는 화면입니다.",
    "기술 검토 자료": "수주 전/후 기술 검토와 특이사항을 기록하는 화면입니다.",
}


def get_visible_department_pages(user: CurrentUser) -> dict[str, list[str]]:
    if user.is_admin:
        return DEPARTMENT_PAGES

    visible = {"홈": DEPARTMENT_PAGES["홈"]}
    if user.department in DEPARTMENT_PAGES:
        pages = list(DEPARTMENT_PAGES[user.department])
        pages = [page for page in pages if page != "시스템 관리"]
        if not user.can_create_documents:
            pages = [page for page in pages if page not in {"문서 발행", "문서 출력", "견적서/주문서 변환"}]
        visible[user.department] = pages
    return visible


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


def render_login() -> None:
    left, center, right = st.columns([1, 1.35, 1])
    with center:
        logo_path = ASSETS_DIR / "megacell_logo.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        st.title("ERP 로그인")
        st.caption("등록된 ERP 계정으로 로그인합니다.")
        with st.form("login_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", width="stretch")
        if submitted:
            ok, error = login(email, password)
            if ok:
                st.rerun()
            else:
                st.error(error or "로그인에 실패했습니다.")


def render_password_change(user: CurrentUser) -> None:
    left, center, right = st.columns([1, 1.35, 1])
    with center:
        st.title("비밀번호 변경")
        st.caption("초기 비밀번호 또는 재설정 비밀번호로 로그인했습니다.")
        with st.form("password_change_form"):
            new_password = st.text_input("새 비밀번호", type="password")
            confirm_password = st.text_input("새 비밀번호 확인", type="password")
            submitted = st.form_submit_button("변경", width="stretch")
        if submitted:
            if new_password != confirm_password:
                st.error("새 비밀번호가 일치하지 않습니다.")
            else:
                try:
                    change_password(user.email, new_password, must_change_password=False)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.success("비밀번호를 변경했습니다. 다시 로그인해 주세요.")
                    logout()
                    st.rerun()


def route(department: str, menu: str, available_tables: list[str], visible_pages: dict[str, list[str]], user: CurrentUser) -> None:
    if department == "홈" or menu == "랜딩페이지":
        render_department_landing(visible_pages, set_navigation)
    elif menu == "업무 대시보드":
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
    elif menu in {"문서 발행", "문서 출력", "견적서/주문서 변환"}:
        if not (user.is_admin or user.can_create_documents):
            st.error("문서 생성 권한이 필요합니다.")
            st.stop()
        render_document_converter()
    elif menu == "사용자 관리":
        render_user_management(user)
    elif menu == "시스템 관리":
        if not user.is_admin:
            st.error("관리자만 접근할 수 있습니다.")
            st.stop()
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

    user = get_current_user()
    if user is None:
        render_login()
        st.stop()
    if user.must_change_password:
        render_password_change(user)
        st.stop()

    visible_pages = get_visible_department_pages(user)

    logo_path = ASSETS_DIR / "megacell_logo.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)
    else:
        st.sidebar.title("메가셀 ERP")

    st.sidebar.caption("부서별 업무 포털")
    st.sidebar.caption(f"로그인: {user.email}")
    st.sidebar.caption(f"권한: {user.role}")
    if st.sidebar.button("로그아웃", width="stretch"):
        logout()
        st.rerun()
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

    if department != "홈" and user.is_admin:
        st.sidebar.divider()
        render_db_controls()

    available_tables = list_tables(db_mtime())
    required_tables = ["수주", "재고", "재고출납", "AS관리", "부품리스트", "자재재고", "BOM", "발주현황"]
    missing_tables = [name for name in required_tables if name not in available_tables]
    if missing_tables and department != "홈":
        st.warning("DB에 아직 없는 테이블: " + ", ".join(missing_tables))

    route(department, menu, available_tables, visible_pages, user)


if __name__ == "__main__":
    main()
