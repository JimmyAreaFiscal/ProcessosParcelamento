import streamlit as st
from datetime import datetime
from model.banco_dados import SessionLocal
from model.usuario import UsuarioDB
from model.banco_dados import DecisoesJudiciais, EfeitosDecisoesJudiciais

def decisoes_judiciais_view():
    st.subheader("⚖️ Decisões Judiciais")

    session = SessionLocal()
    usuario = session.query(UsuarioDB).filter_by(conta=st.session_state["usuario"]).first()

    if not usuario:
        st.error("Usuário não autenticado.")
        session.close()
        return

    role = usuario.role

    # Se Auditor → CRUD de Efeitos
    if role == "Auditor":
        st.markdown("### ✏️ Efeitos de Decisões Judiciais")
        efeitos = session.query(EfeitosDecisoesJudiciais).all()

        for efeito in efeitos:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.write(f"🔸 {efeito.descricao_efeitos}")
            with col2:
                if st.button("🗑️", key=f"del_efeito_{efeito.id}"):
                    session.delete(efeito)
                    session.commit()
                    st.success("Efeito removido.")
                    st.rerun()

        with st.form("form_efeito"):
            nova_desc = st.text_input("Novo Efeito")
            if st.form_submit_button("Adicionar Efeito"):
                if nova_desc.strip():
                    novo = EfeitosDecisoesJudiciais(descricao_efeitos=nova_desc.strip())
                    session.add(novo)
                    session.commit()
                    st.success("Efeito adicionado com sucesso.")
                    st.rerun()

    # Se Auditor ou Usuario → CRUD de Decisões
    if role in ["Usuario", "Auditor"]:
        st.markdown("### 📑 Decisões Judiciais")

        decisoes = session.query(DecisoesJudiciais).all()
        efeitos_dict = {e.id: e.descricao_efeitos for e in session.query(EfeitosDecisoesJudiciais).all()}

        for d in decisoes:
            col1, col2 = st.columns([7, 1])
            with col1:
                st.write(f"🧾 CPF: {d.cpf_contribuinte} | Processo: {d.numero_processo} | Efeito: {efeitos_dict.get(d.efeitos_fk)} | Situação: {d.situacao} | Data: {d.data_decisao.strftime('%d/%m/%Y')}")
            with col2:
                if st.button("❌", key=f"del_decisao_{d.id}"):
                    session.delete(d)
                    session.commit()
                    st.success("Decisão removida.")
                    st.rerun()

        with st.form("form_decisao"):
            cpf = st.text_input("CPF do Contribuinte")
            processo = st.text_input("Número do Processo")
            efeito_id = st.selectbox("Efeito Aplicado", list(efeitos_dict.keys()), format_func=lambda x: efeitos_dict[x])
            situacao = st.text_input("Situação Atual")

            if st.form_submit_button("Adicionar Decisão Judicial"):
                nova_decisao = DecisoesJudiciais(
                    cpf_contribuinte=cpf.strip(),
                    numero_processo=processo.strip(),
                    efeitos_fk=efeito_id,
                    situacao=situacao.strip(),
                    data_decisao=datetime.utcnow()
                )
                session.add(nova_decisao)
                session.commit()
                st.success("Decisão judicial adicionada.")
                st.rerun()

    session.close()
