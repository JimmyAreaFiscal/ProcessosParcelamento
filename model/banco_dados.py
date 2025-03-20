from sqlalchemy import create_engine, Column, String, Float, Boolean, LargeBinary, DateTime, Integer, ForeignKey
from datetime import datetime
from sqlalchemy.orm import sessionmaker, declarative_base
import streamlit as st 
import os 
import hashlib 


# Configuração do banco de dados (substitua pela URL correta)
DATABASE_URL = st.secrets["database"]["URL"]

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Criar sessão do banco
def get_db():
    return SessionLocal()


class ProcessoDB(Base):
    __tablename__ = "processos"

    nome = Column(String, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    saneado = Column(Boolean, default=False)
    sei = Column(String, nullable=True)
    enviado = Column(Boolean, default=False)

    # Novos campos
    data_inclusao = Column(DateTime, default=datetime.utcnow)
    data_saneamento = Column(DateTime, nullable=True)
    data_sei = Column(DateTime, nullable=True)
    data_enviado = Column(DateTime, nullable=True)
    usuario_ultima_alteracao = Column(String, nullable=True)  # Nome do usuário que fez a última alteração

class ProcessoHistoricoDB(Base):
    __tablename__ = "historico_processos"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    saneado = Column(Boolean, default=False)
    sei = Column(String, nullable=True)
    enviado = Column(Boolean, default=False)

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    conta = Column(String, primary_key=True, index=True)
    senha_hash = Column(LargeBinary, nullable=False)
    salt = Column(LargeBinary, nullable=False)
    role = Column(String, default="aguardando_aprovacao")
    precisa_redefinir_senha = Column(Boolean, default=False)  # Indica se precisa redefinir senha no próximo login


class LogUsuarios(Base):
    __tablename__ = "log_usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conta_usuario = Column(String, ForeignKey("usuarios.conta"), nullable=False)
    administrador = Column(String, nullable=False)  # Quem fez a alteração
    data_modificacao = Column(DateTime, default=datetime.utcnow)
    acao = Column(String, nullable=False)  # Exemplo: "Senha resetada pelo admin"

# Criar a tabela no banco de dados
Base.metadata.create_all(bind=engine)





# Criar Admin ao iniciar o sistema
def criar_admin():
    """Cria um novo Administrador SEM verificar se já existe."""
    session = SessionLocal()

    try:
        admin_usuario = st.secrets["admin"]["usuario"]
        admin_senha = st.secrets["admin"]["senha"]

        salt = os.urandom(16)
        senha_hash = hashlib.pbkdf2_hmac('sha256', admin_senha.encode(), salt, 100000)

        admin = UsuarioDB(
            conta=admin_usuario,
            senha_hash=senha_hash,
            salt=salt,
            role="admin"
        )

        session.add(admin)
        session.commit()
        st.success("Novo Administrador criado com sucesso!")

    except Exception as e:
        st.error(f"Erro ao criar conta Admin: {e}")
    
    finally:
        session.close()


def resetar_senha(conta_usuario, admin_responsavel):
    """Reseta a senha do usuário e registra no log."""
    session = SessionLocal()

    usuario = session.query(UsuarioDB).filter_by(conta=conta_usuario).first()
    if usuario:
        # Gerar um novo salt e hash para a senha padrão temporária
        salt = os.urandom(16)
        senha_temporaria = "Reset@123"
        senha_hash = hashlib.pbkdf2_hmac('sha256', senha_temporaria.encode(), salt, 100000)

        # Atualiza os dados do usuário
        usuario.senha_hash = senha_hash
        usuario.salt = salt
        usuario.precisa_redefinir_senha = True  # O usuário será obrigado a mudar a senha no próximo login

        # Criar log da alteração
        log = LogUsuarios(
            conta_usuario=conta_usuario,
            administrador=admin_responsavel,
            acao="Senha resetada pelo admin"
        )
        session.add(log)

        session.commit()
        session.close()
        return True
    return False


# Rodar criação do Admin ao importar este módulo
criar_admin()
