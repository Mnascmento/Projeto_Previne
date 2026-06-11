"""
models/schemas.py
Definição das tabelas via SQLAlchemy ORM.

Decisão de arquitetura (Sprint 1 / T-03):
Este é o arquivo zero do projeto — nenhum outro módulo pode ser escrito
sem ele. Toda alteração de estrutura de dados deve passar por aqui.

Tabelas:
  - usuarios       → autenticação e perfil
  - rendas         → fontes de renda mensais (fixas ou variáveis)
  - gastos         → lançamentos de despesas por categoria
  - dividas        → dívidas ativas com parcelas, juros e vencimento
  - historico_risco→ log do índice de risco calculado por mês
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, Float, String,
    Boolean, DateTime, Date, Text, ForeignKey, Index,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from pathlib import Path

# ── Engine e sessão ────────────────────────────────────────────────────────
DB_PATH = Path("data/database.db")
DB_PATH.parent.mkdir(exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,                    # Altere para True para ver SQL no terminal
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ── Modelos ────────────────────────────────────────────────────────────────

class Usuario(Base):
    """Conta de usuário. Autenticação por e-mail + senha (hash SHA-256)."""
    __tablename__ = "usuarios"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    username    = Column(String(80),  unique=True,  nullable=False)
    email       = Column(String(120), unique=True,  nullable=False)
    senha_hash  = Column(String(64),  nullable=False)           # SHA-256 hex
    criado_em   = Column(DateTime, default=datetime.utcnow)
    ativo       = Column(Boolean, default=True)

    # Relacionamentos (lazy="dynamic" evita carregar tudo de uma vez)
    rendas          = relationship("Renda",         back_populates="usuario", cascade="all, delete-orphan")
    gastos          = relationship("Gasto",         back_populates="usuario", cascade="all, delete-orphan")
    dividas         = relationship("Divida",        back_populates="usuario", cascade="all, delete-orphan")
    historico_risco = relationship("HistoricoRisco",back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario id={self.id} username={self.username!r}>"


class Renda(Base):
    """Fonte de renda mensal — fixa (salário) ou variável (freela, comissão)."""
    __tablename__ = "rendas"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    descricao   = Column(String(120), nullable=False)
    valor       = Column(Float,       nullable=False)
    tipo        = Column(String(20),  nullable=False, default="fixa")  # fixa | variavel
    mes         = Column(String(7),   nullable=False)                  # YYYY-MM
    criado_em   = Column(DateTime,    default=datetime.utcnow)

    usuario     = relationship("Usuario", back_populates="rendas")

    __table_args__ = (
        Index("ix_rendas_user_mes", "user_id", "mes"),
    )

    def __repr__(self):
        return f"<Renda id={self.id} desc={self.descricao!r} valor={self.valor}>"


class Gasto(Base):
    """Lançamento de despesa por categoria e data."""
    __tablename__ = "gastos"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    descricao   = Column(String(120), nullable=False)
    categoria   = Column(String(50),  nullable=False)
    valor       = Column(Float,       nullable=False)
    data        = Column(Date,        nullable=False)
    criado_em   = Column(DateTime,    default=datetime.utcnow)

    usuario     = relationship("Usuario", back_populates="gastos")

    __table_args__ = (
        Index("ix_gastos_user_data", "user_id", "data"),
    )

    def __repr__(self):
        return f"<Gasto id={self.id} cat={self.categoria!r} valor={self.valor}>"


class Divida(Base):
    """
    Dívida ativa com controle de parcelas.
    taxa_juros em % ao mês (0.0 = sem juros declarados).
    vencimento = dia do mês (1-31).
    """
    __tablename__ = "dividas"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    user_id             = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    descricao           = Column(String(120), nullable=False)
    valor_total         = Column(Float,       nullable=False)
    valor_parcela       = Column(Float,       nullable=False)
    parcelas_restantes  = Column(Integer,     nullable=False)
    taxa_juros          = Column(Float,       default=0.0)          # % a.m.
    vencimento          = Column(Integer,     nullable=True)        # dia 1-31
    ativa               = Column(Boolean,     default=True)
    criado_em           = Column(DateTime,    default=datetime.utcnow)

    usuario             = relationship("Usuario", back_populates="dividas")

    __table_args__ = (
        Index("ix_dividas_user_ativa", "user_id", "ativa"),
    )

    @property
    def total_restante(self) -> float:
        return self.valor_parcela * self.parcelas_restantes

    @property
    def percentual_pago(self) -> float:
        if self.valor_total <= 0:
            return 0.0
        pago = self.valor_total - self.total_restante
        return max(0.0, min(1.0, pago / self.valor_total))

    def __repr__(self):
        return f"<Divida id={self.id} desc={self.descricao!r} parcela={self.valor_parcela}>"


class HistoricoRisco(Base):
    """
    Log mensal do índice de risco calculado pelo motor de IA.
    Permite rastrear a evolução financeira do usuário ao longo do tempo
    e alimentar futuros modelos de ML com dados reais.
    """
    __tablename__ = "historico_risco"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    mes             = Column(String(7),  nullable=False)    # YYYY-MM
    indice          = Column(Float,      nullable=False)    # 0-100
    nivel           = Column(String(20), nullable=False)    # baixo|medio|alto|critico
    comprometimento = Column(Float,      nullable=False)    # % da renda comprometida
    saldo_livre     = Column(Float,      nullable=False)
    calculado_em    = Column(DateTime,   default=datetime.utcnow)

    usuario         = relationship("Usuario", back_populates="historico_risco")

    __table_args__ = (
        Index("ix_historico_user_mes", "user_id", "mes"),
    )

    def __repr__(self):
        return f"<HistoricoRisco user={self.user_id} mes={self.mes} indice={self.indice}>"


# ── Criação das tabelas ────────────────────────────────────────────────────

def criar_tabelas():
    """
    Cria todas as tabelas no banco se ainda não existirem.
    Deve ser chamado uma vez na inicialização do app (app.py).
    """
    Base.metadata.create_all(bind=engine)


def get_session():
    """
    Context manager para uso em módulos:

        from models.schemas import get_session
        with get_session() as db:
            db.add(obj)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
