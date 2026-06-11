"""
modules/auth.py

Autenticação e gerenciamento de sessão do usuário.

Decisões de escopo acadêmico:
  - Senha armazenada como SHA-256 hex (sem salt) — suficiente para protótipo,
    não adequado para produção (produção usaria bcrypt/argon2).
  - Sessão gerenciada por st.session_state (sem JWT, sem cookies persistentes).
  - Sem e-mail de recuperação de senha — fluxo simplificado.
"""

import hashlib
import streamlit as st
from contextlib import contextmanager

from models.schemas import SessionLocal, Usuario, criar_tabelas
from modules.validacoes import validar_usuario_cadastro, separar_erros_e_avisos


# ── Inicialização ──────────────────────────────────────────────────────────

def init_db():
    """Cria as tabelas no banco na primeira execução."""
    criar_tabelas()


def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


# ── CRUD de usuário ────────────────────────────────────────────────────────

def cadastrar_usuario(username: str, email: str, senha: str) -> tuple[bool, str]:
    """
    Cadastra novo usuário. Retorna (sucesso, mensagem).
    Validações de negócio já foram aplicadas antes de chamar esta função.
    """
    with SessionLocal() as db:
        # Verificar duplicidade
        existente = (
            db.query(Usuario)
            .filter(
                (Usuario.email == email.lower().strip()) |
                (Usuario.username == username.strip())
            )
            .first()
        )
        if existente:
            if existente.email == email.lower().strip():
                return False, "Este e-mail já está cadastrado."
            return False, "Este nome de usuário já está em uso."

        novo = Usuario(
            username=username.strip(),
            email=email.lower().strip(),
            senha_hash=_hash_senha(senha),
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
    return True, "Conta criada com sucesso!"


def autenticar_usuario(email: str, senha: str) -> dict | None:
    """
    Verifica credenciais. Retorna dict com id e username ou None.
    """
    with SessionLocal() as db:
        user = (
            db.query(Usuario)
            .filter(
                Usuario.email == email.lower().strip(),
                Usuario.senha_hash == _hash_senha(senha),
                Usuario.ativo == True,
            )
            .first()
        )
        if user:
            return {"id": user.id, "username": user.username}
    return None


def buscar_usuario_por_id(user_id: int) -> dict | None:
    with SessionLocal() as db:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user:
            return {"id": user.id, "username": user.username, "email": user.email}
    return None


# ── Telas Streamlit ────────────────────────────────────────────────────────

def login_page():
    with st.form("form_login", clear_on_submit=False):
        email = st.text_input("E-mail", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")

    if submitted:
        if not email or not senha:
            st.error("Preencha e-mail e senha.")
            return

        user = autenticar_usuario(email, senha)
        if user:
            st.session_state.user_id  = user["id"]
            st.session_state.username = user["username"]
            st.rerun()
        else:
            st.error("E-mail ou senha incorretos.")


def register_page():
    with st.form("form_register", clear_on_submit=True):
        username = st.text_input("Nome de usuário", placeholder="Como quer ser chamado?")
        email    = st.text_input("E-mail", placeholder="seu@email.com")
        senha    = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres")
        senha2   = st.text_input("Confirme a senha", type="password")
        submitted = st.form_submit_button("Criar conta", use_container_width=True, type="primary")

    if submitted:
        dados = {
            "username": username,
            "email": email,
            "senha": senha,
            "senha_confirmacao": senha2,
        }
        erros, _ = separar_erros_e_avisos(validar_usuario_cadastro(dados))
        if erros:
            for e in erros:
                st.error(e)
            return

        ok, msg = cadastrar_usuario(username, email, senha)
        if ok:
            st.success(msg + " Acesse a aba **Entrar**.")
        else:
            st.error(msg)
