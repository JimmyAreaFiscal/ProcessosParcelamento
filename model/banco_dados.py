from sqlalchemy import create_engine, Column, String, Float, Boolean, LargeBinary, DateTime 
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


# Modelo do banco de dados
class ProcessoDB(Base):
    __tablename__ = "processos"

    nome = Column(String, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    saneado = Column(Boolean, default=False)
    sei = Column(String, nullable=True)
    enviado = Column(Boolean, default=False)
    
    # Novas colunas para armazenar datas
    data_inclusao = Column(DateTime, default=datetime.utcnow)
    data_saneamento = Column(DateTime, nullable=True)
    data_sei = Column(DateTime, nullable=True)
    data_enviado = Column(DateTime, nullable=True)

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

# Rodar criação do Admin ao importar este módulo
criar_admin()
