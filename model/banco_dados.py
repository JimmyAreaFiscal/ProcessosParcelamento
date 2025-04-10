from sqlalchemy import create_engine, Column, String, Float, Boolean, LargeBinary, DateTime, Integer, ForeignKey
from datetime import datetime, timezone
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
    nome_empresa = Column(String)
    cnpj_empresa = Column(String)
    valor = Column(Float, nullable=False)
    saneado = Column(Boolean, default=False)
    sei = Column(String, nullable=True)
    enviado = Column(Boolean, default=False)

    data_inclusao = Column(DateTime, default=datetime.utcnow)
    data_saneamento = Column(DateTime, nullable=True)
    data_sei = Column(DateTime, nullable=True)
    data_enviado = Column(DateTime, nullable=True)
    usuario_ultima_alteracao = Column(String, nullable=True)

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
    role = Column(String, default="aguardando_aprovacao")
    precisa_redefinir_senha = Column(Boolean, default=False)  # Válido apenas para admin

class LogUsuarios(Base):
    __tablename__ = "log_usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conta_usuario = Column(String, ForeignKey("usuarios.conta"), nullable=False)
    administrador = Column(String, nullable=False)
    data_modificacao = Column(DateTime, default=timezone.utc)
    acao = Column(String, nullable=False)

class DecisoesJudiciais(Base):
    __tablename__ = "decisoes_judiciais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cpf_contribuinte = Column(String, nullable=False)
    data_decisao = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    numero_processo = Column(String, nullable=False)
    efeitos_fk = Column(Integer, ForeignKey("efeitos_decisoes_judiciais.id"), nullable=False)
    situacao = Column(String, nullable=False)

class EfeitosDecisoesJudiciais(Base):
    __tablename__ = "efeitos_decisoes_judiciais"
    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao_efeitos = Column(String, nullable=False)

# Criar a tabela no banco de dados
Base.metadata.create_all(bind=engine)

# Criar Admin ao iniciar o sistema
def criar_admin():
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
    session = SessionLocal()
    usuario = session.query(UsuarioDB).filter_by(conta=conta_usuario).first()
    if usuario and usuario.role == "admin":
        salt = os.urandom(16)
        senha_temporaria = "Reset@123"
        senha_hash = hashlib.pbkdf2_hmac('sha256', senha_temporaria.encode(), salt, 100000)

        usuario.senha_hash = senha_hash
        usuario.salt = salt
        usuario.precisa_redefinir_senha = True

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
