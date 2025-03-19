from model.banco_dados import UsuarioDB, SessionLocal
import hashlib
import os 
import streamlit as st 


class Usuario:
    def __init__(self, conta: str, senha: str):
        self._conta = conta
        self._senha_hash, self._salt = self._gerar_hash_senha(senha)


    def _gerar_hash_senha(self, senha: str):
        """Gera um hash seguro para a senha usando SHA-256 e um salt aleatório."""
        salt = os.urandom(16)  # Gera um salt aleatório de 16 bytes
        hash_senha = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, 100000)
        return hash_senha, salt


    def criarConta(self):
        """Cria uma nova conta no banco de dados."""
        session = SessionLocal()
        
        # Verifica se o usuário já existe
        usuario_existente = session.query(UsuarioDB).filter_by(conta=self._conta).first()
        if usuario_existente:
            session.close()
            raise ValueError("Usuário já existe no banco de dados.")

        novo_usuario = UsuarioDB(
            conta=self._conta,
            senha_hash=self._senha_hash,
            salt=self._salt
        )
        session.add(novo_usuario)
        session.commit()
        session.close()


    def mudarSenha(self, nova_senha: str):
        """Altera a senha do usuário no banco de dados e mantém um novo hash e salt."""
        session = SessionLocal()
        usuario = session.query(UsuarioDB).filter_by(conta=self._conta).first()

        if not usuario:
            session.close()
            raise ValueError("Usuário não encontrado.")

        # Gerar novo hash e salt para a nova senha
        novo_hash, novo_salt = self._gerar_hash_senha(nova_senha)

        # Atualizar os dados no banco de dados
        usuario.senha_hash = novo_hash
        usuario.salt = novo_salt

        session.commit()
        session.close()


    def validarSenha(self, senha: str) -> bool:
        """Valida se a senha fornecida corresponde à senha armazenada no banco de dados."""
        session = SessionLocal()
        usuario = session.query(UsuarioDB).filter_by(conta=self._conta).first()
        session.close()

        if not usuario:
            return False
        
        hash_senha_verificacao = hashlib.pbkdf2_hmac('sha256', senha.encode(), usuario.salt, 100000)
        return hash_senha_verificacao == usuario.senha_hash