from sqlalchemy import create_engine, Column, String, Float, Boolean, LargeBinary
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

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    saneado = Column(Boolean, default=False)
    sei = Column(String, nullable=True)
    enviado = Column(Boolean, default=False)

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

# Criar a tabela no banco de dados
Base.metadata.create_all(bind=engine)