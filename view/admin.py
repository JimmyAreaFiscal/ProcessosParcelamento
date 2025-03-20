import streamlit as st
from model.banco_dados import SessionLocal, resetar_senha
from model.usuario import UsuarioDB

def painelAdmin():
    """ Painel para Auditores e Administradores gerenciarem usuários """
    if "usuario" not in st.session_state:
        st.error("Você precisa estar logado para acessar esta página.")
        return

    session = SessionLocal()
    usuario = session.query(UsuarioDB).filter_by(conta=st.session_state["usuario"]).first()

    if not usuario or usuario.role not in ["Auditor", "admin"]:
        st.error("Acesso negado. Apenas Auditores e Administradores podem acessar esta página.")
        session.close()
        return

    st.title("Painel de Administração 👤")

    usuarios = session.query(UsuarioDB).all()

    if not usuarios:
        st.info("Nenhum usuário encontrado.")
        session.close()
        return

    for u in usuarios:
        with st.expander(f"👤 {u.conta} - Role: {u.role}"):
            if u.role == "aguardando_aprovacao":
                if st.button(f"✅ Aprovar {u.conta}", key=f"aprovar_{u.conta}"):
                    u.role = "Usuario"
                    session.commit()
                    st.success(f"Usuário {u.conta} aprovado.")
                    st.rerun()

            if usuario.role == "admin":  # Apenas admin pode promover usuários
                nova_role = st.selectbox(
                    f"Alterar role de {u.conta}",
                    ["Usuario", "Auditor", "admin"],
                    index=["Usuario", "Auditor", "admin"].index(u.role),
                    key=f"role_{u.conta}"
                )

                if st.button(f"🔄 Atualizar Role {u.conta}", key=f"atualizar_{u.conta}"):
                    u.role = nova_role
                    session.commit()
                    st.success(f"Permissão de {u.conta} alterada para {nova_role}.")
                    st.rerun()

                # Opção de resetar senha
                if st.button(f"🔑 Resetar Senha {u.conta}", key=f"resetar_{u.conta}"):
                    if resetar_senha(u.conta, usuario.conta):
                        st.success(f"Senha de {u.conta} foi resetada para 'Reset@123'. O usuário deverá alterá-la no próximo login.")
                        st.rerun()
                    else:
                        st.error("Erro ao resetar senha.")

    session.close()