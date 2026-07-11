from __future__ import annotations

import streamlit as st

from services.auth_service import DEPARTMENTS, ROLES, CurrentUser, get_user, get_user_options, list_users, upsert_user


def render_user_management(current_user: CurrentUser) -> None:
    st.title("사용자 관리")
    st.caption("ERP 자체 로그인 계정, 부서, 역할, 문서 생성 권한을 관리합니다.")

    if not current_user.is_admin:
        st.error("관리자만 접근할 수 있습니다.")
        st.stop()

    users = list_users()
    st.subheader("사용자 목록")
    st.dataframe(users, width="stretch", hide_index=True)

    st.divider()
    st.subheader("사용자 추가/수정")

    existing_options = ["새 사용자"] + get_user_options()
    selected = st.selectbox("수정할 사용자", existing_options)
    selected_user = None if selected == "새 사용자" else get_user(selected)

    with st.form("user_form"):
        email = st.text_input("이메일", value=selected_user.email if selected_user else "")
        name = st.text_input("이름", value=selected_user.name if selected_user else "")
        department_default = selected_user.department if selected_user and selected_user.department in DEPARTMENTS else DEPARTMENTS[0]
        role_default = selected_user.role if selected_user and selected_user.role in ROLES else "일반사용자"

        c1, c2 = st.columns(2)
        department = c1.selectbox("부서", DEPARTMENTS, index=DEPARTMENTS.index(department_default))
        role = c2.selectbox("역할", ROLES, index=ROLES.index(role_default))

        c3, c4 = st.columns(2)
        can_create_documents = c3.checkbox(
            "문서 생성 권한",
            value=bool(selected_user.can_create_documents) if selected_user else False,
        )
        is_active = c4.checkbox("사용 허용", value=bool(selected_user.is_active) if selected_user else True)

        st.caption("비밀번호를 입력하면 신규 사용자의 초기 비밀번호 또는 기존 사용자의 재설정 비밀번호로 저장됩니다.")
        new_password = st.text_input("초기/재설정 비밀번호", type="password")
        force_password_change = st.checkbox("다음 로그인 시 비밀번호 변경 요구", value=selected_user is None)

        submitted = st.form_submit_button("저장", width="stretch")

    if submitted:
        try:
            upsert_user(
                email=email,
                name=name,
                department=department,
                role=role,
                can_create_documents=can_create_documents,
                is_active=is_active,
                new_password=new_password,
                force_password_change=force_password_change,
            )
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success("사용자 정보가 저장되었습니다.")
            st.rerun()

    st.info("로그인/로그아웃/회원관리는 이제 ERP 내부에서 처리합니다. 비밀번호는 해시로 저장되며 평문은 저장하지 않습니다.")
