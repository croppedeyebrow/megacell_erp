from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from config import BASE_DIR, DATA_DIR, TEMPLATES_DIR
from core.db import get_table
from core.ui import (
    clean_display,
    download_csv,
    metric_sum,
    normalize_numeric,
    prepare_numeric,
    safe_unique,
    searchable_table,
    table_view,
    text_filter,
)
from services.battery_service import build_pending_battery, render_pending_calendar
from services.document_service import (
    build_order_workbook_bytes,
    extract_document_pdf,
    safe_filename,
)


def render_document_converter() -> None:
    st.title("견적/주문서")
    tab_pdf, tab_orders, tab_templates = st.tabs(["문서 PDF 변환", "수주 원장 조회", "양식 파일"])

    with tab_pdf:
        st.subheader("견적서/발주서 PDF -> 주문서")
        uploaded_pdf = st.file_uploader("견적서 또는 발주서 PDF 업로드", type=["pdf"], key="quote_pdf_upload")

        if uploaded_pdf is None:
            st.info("텍스트형 견적서 또는 발주서 PDF를 업로드하면 주문서 양식에 들어갈 값을 추출합니다.")
        else:
            try:
                extracted = extract_document_pdf(uploaded_pdf.getvalue())
            except Exception as exc:
                st.error(f"PDF 추출 실패: {exc}")
            else:
                st.caption(
                    f"문서유형: {extracted.get('문서유형') or '-'} / "
                    f"문서번호: {extracted.get('견적번호') or '-'} / "
                    f"문서일자: {extracted.get('견적일자') or '-'}"
                )

                c1, c2, c3 = st.columns([1.4, 1.2, 1.2])
                extracted["발주처"] = c1.text_input("발주처", value=str(extracted.get("발주처", "")))
                extracted["담당자"] = c2.text_input("담당자", value=str(extracted.get("담당자", "")))
                extracted["현장명"] = c3.text_input("P/O No. 또는 현장명", value=str(extracted.get("현장명", "")))

                c4, c5, c6 = st.columns([1.2, 1.8, 1.2])
                extracted["발행일자"] = c4.text_input("주문서 발행일자", value=str(extracted.get("발행일자", "")))
                extracted["납품일자"] = c5.text_input("납품일자/시간", value=str(extracted.get("납품일자", "")))
                extracted["주문번호"] = c6.text_input("S/O No.", value=str(extracted.get("주문번호", "")))

                extracted["납품장소"] = st.text_input("납품 또는 설치 장소", value=str(extracted.get("납품장소", "")))
                extracted["현지인수자"] = st.text_input("현지 인수자", value=str(extracted.get("현지인수자", "")))
                extracted["제품정보"] = st.text_area("제품정보 및 첨부품", value=str(extracted.get("제품정보", "")), height=90)

                st.subheader("품목 확인")
                items_df = pd.DataFrame(extracted.get("품목") or [])
                if items_df.empty:
                    items_df = pd.DataFrame(columns=["품명규격", "수량", "단가", "금액"])
                edited_items = st.data_editor(
                    items_df,
                    width="stretch",
                    hide_index=True,
                    num_rows="dynamic",
                    column_order=["품명규격", "수량", "단가", "금액"],
                    key="quote_items_editor",
                )
                edited_items = prepare_numeric(edited_items, ["수량", "단가", "금액"])

                m1, m2 = st.columns(2)
                m1.metric("품목 수", f"{len(edited_items.dropna(how='all')):,}개")
                m2.metric("품목 합계", metric_sum(edited_items, "금액", "원"))

                try:
                    order_bytes = build_order_workbook_bytes(extracted, edited_items)
                except Exception as exc:
                    st.error(f"주문서 생성 실패: {exc}")
                else:
                    file_base = safe_filename(
                        f"{extracted.get('주문번호', '')} {extracted.get('발주처', '')} "
                        f"{extracted.get('담당자', '')} {extracted.get('현장명', '')}"
                    )
                    st.download_button(
                        "주문서 xlsm 내려받기",
                        data=order_bytes,
                        file_name=f"{file_base}.xlsm",
                        mime="application/vnd.ms-excel.sheet.macroEnabled.12",
                        width="stretch",
                    )

    with tab_orders:
        orders = prepare_numeric(get_table("수주"), ["수량", "수주금액", "vat포함"])
        keyword = st.text_input("문서 생성 대상 검색")
        filtered = text_filter(orders, keyword, ["납품처", "품명규격", "제조지시서", "발주처"])
        table_view(
            filtered.head(100),
            ["수주일자", "제조지시서", "납품처", "품명규격", "수량", "수주금액", "vat포함", "발주처", "비고"],
            height=500,
        )

    with tab_templates:
        st.subheader("포함된 양식 파일")
        template_dirs = [TEMPLATES_DIR, DATA_DIR, BASE_DIR]
        template_names = []
        for directory in template_dirs:
            if directory.exists():
                template_names.extend(
                    path.name for path in directory.iterdir() if path.suffix.lower() in {".pdf", ".xlsm"} and "양식" in path.name
                )
        templates = sorted(set(template_names))
        template_df = pd.DataFrame({"파일명": templates})
        table_view(template_df, ["파일명"], height=220)
