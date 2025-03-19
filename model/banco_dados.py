from sqlalchemy import create_engine, Column, String, Float, Boolean, LargeBinary, DateTime 
from datetime import datetime
from sqlalchemy.orm import sessionmaker, declarative_base
import streamlit as st 


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