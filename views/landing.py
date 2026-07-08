from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import streamlit as st

from config import ASSETS_DIR


DEPARTMENT_SUMMARIES = {
    "경영지원팀": {
        "summary": "재고, 입출고, 구매/발주, 문서와 기준 운영을 관리합니다.",
        "accent": "#1f77b4",
    },
    "기술영업팀": {
        "summary": "수주, 견적, 미출고, 고객 요청과 출고 요청의 시작점입니다.",
        "accent": "#0f9d58",
    },
    "생산팀": {
        "summary": "생산 요청, BOM 소요량, 부족 자재, 검수와 출고 준비를 확인합니다.",
        "accent": "#f4a261",
    },
    "연구소": {
        "summary": "제품/BOM 기준정보, 자재 마스터, 사양 변경과 기술 검토를 담당합니다.",
        "accent": "#7c3aed",
    },
    "전체 현황": {
        "summary": "부서별 업무 흐름을 한 번에 보는 관리자/공통 현황 화면입니다.",
        "accent": "#334155",
    },
}


def inject_landing_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
        }
        .megacell-hero {
            border-bottom: 1px solid #e5e7eb;
            padding: 1.2rem 0 1.6rem;
            margin-bottom: 1.4rem;
        }
        .megacell-hero h1 {
            margin: 0.9rem 0 0.35rem;
            color: #111827;
            font-size: 2.25rem;
            font-weight: 760;
            letter-spacing: 0;
        }
        .megacell-hero p {
            margin: 0;
            color: #64748b;
            font-size: 1.02rem;
        }
        .department-card {
            border: 1px solid #d9e2ec;
            border-top: 5px solid var(--accent);
            border-radius: 8px;
            padding: 1rem 1rem 0.85rem;
            min-height: 178px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
        }
        .department-card h3 {
            margin: 0 0 0.35rem;
            color: #0f172a;
            font-size: 1.15rem;
            font-weight: 720;
            letter-spacing: 0;
        }
        .department-card p {
            min-height: 48px;
            margin: 0 0 0.7rem;
            color: #475569;
            line-height: 1.45;
            font-size: 0.94rem;
        }
        .department-card ul {
            margin: 0;
            padding-left: 1.05rem;
            color: #334155;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .planned-page {
            border-left: 5px solid #1f77b4;
            padding: 1rem 1.2rem;
            background: #f8fafc;
            border-radius: 8px;
            margin-top: 1rem;
        }
        .planned-page strong {
            color: #0f172a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_department_landing(
    department_pages: dict[str, list[str]],
    navigate: Callable[[str, str | None], None],
) -> None:
    inject_landing_style()

    logo_path = ASSETS_DIR / "megacell_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=520)

    st.markdown(
        """
        <div class="megacell-hero">
            <h1>메가셀 ERP</h1>
            <p>부서별 업무 흐름에 맞춰 필요한 화면으로 바로 이동합니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    departments = [name for name in department_pages if name != "홈"]
    for row_start in range(0, len(departments), 3):
        cols = st.columns(3)
        for col, department in zip(cols, departments[row_start : row_start + 3]):
            info = DEPARTMENT_SUMMARIES.get(
                department,
                {"summary": "부서 업무 화면으로 이동합니다.", "accent": "#1f77b4"},
            )
            pages = department_pages[department][:4]
            items = "".join(f"<li>{page}</li>" for page in pages)
            with col:
                st.markdown(
                    f"""
                    <div class="department-card" style="--accent: {info['accent']}">
                        <h3>{department}</h3>
                        <p>{info['summary']}</p>
                        <ul>{items}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"{department} 이동", key=f"go_{department}", width="stretch"):
                    navigate(department)
                    st.rerun()


def render_planned_page(title: str, department: str, description: str) -> None:
    inject_landing_style()
    st.title(title)
    st.caption(department)
    st.markdown(
        f"""
        <div class="planned-page">
            <strong>설계 예정 화면</strong><br />
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("현재는 큰 메뉴 구조를 먼저 잡는 단계입니다. 이후 데이터 모델과 권한 구조가 정리되면 이 화면부터 순차적으로 구현합니다.")
