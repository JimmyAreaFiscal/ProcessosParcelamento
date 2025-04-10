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

            if usuario.role == "admin":
                opcoes_roles = ["Usuario", "Auditor", "admin"]
                index_atual = opcoes_roles.index(u.role) if u.role in opcoes_roles else 0

                nova_role = st.selectbox(
                    f"Alterar role de {u.conta}",
                    opcoes_roles,
                    index=index_atual,
                    key=f"role_{u.conta}"
                )

                if st.button(f"🔄 Atualizar Role {u.conta}", key=f"atualizar_{u.conta}"):
                    u.role = nova_role
                    session.commit()
                    st.success(f"Permissão de {u.conta} alterada para {nova_role}.")
                    st.rerun()

                if st.button(f"🔐 Resetar senha de {u.conta}", key=f"reset_senha_{u.conta}"):
                    sucesso = resetar_senha(u.conta, usuario.conta)
                    if sucesso:
                        st.success("Senha resetada. O usuário deverá redefinir no próximo login.")
                        st.rerun()
                    else:
                        st.error("Erro ao resetar a senha do usuário.")

    session.close()
