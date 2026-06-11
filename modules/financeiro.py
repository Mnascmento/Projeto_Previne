"""
modules/financeiro.py

CRUD de rendas, gastos e dívidas via SQLAlchemy.

Todas as funções recebem user_id explicitamente — sem globals,
sem st.session_state — para que possam ser testadas unitariamente.

Padrão de retorno:
  - Listagens   → list[dict]  (não expõe objetos ORM para as páginas)
  - Totais      → float
  - Agregações  → dict[str, float]
  - Mutações    → None  (erros propagam exceção)
"""

from __future__ import annotations
from datetime import date, datetime

from models.schemas import SessionLocal, Renda, Gasto, Divida


# ── Constantes exportadas ──────────────────────────────────────────────────

CATEGORIAS_GASTO = [
    "Alimentação", "Moradia", "Transporte", "Saúde",
    "Educação", "Lazer", "Vestuário", "Outros",
]


# ── Helpers ────────────────────────────────────────────────────────────────

def _renda_to_dict(r: Renda) -> dict:
    return {
        "id":        r.id,
        "descricao": r.descricao,
        "valor":     r.valor,
        "tipo":      r.tipo,
        "mes":       r.mes,
    }


def _gasto_to_dict(g: Gasto) -> dict:
    return {
        "id":        g.id,
        "descricao": g.descricao,
        "categoria": g.categoria,
        "valor":     g.valor,
        "data":      g.data.isoformat() if isinstance(g.data, date) else str(g.data),
    }


def _divida_to_dict(d: Divida) -> dict:
    return {
        "id":                  d.id,
        "descricao":           d.descricao,
        "valor_total":         d.valor_total,
        "valor_parcela":       d.valor_parcela,
        "parcelas_restantes":  d.parcelas_restantes,
        "taxa_juros":          d.taxa_juros,
        "vencimento":          d.vencimento,
        "ativa":               d.ativa,
        "total_restante":      d.total_restante,
        "percentual_pago":     d.percentual_pago,
    }


# ── Rendas ─────────────────────────────────────────────────────────────────

def inserir_renda(user_id: int, descricao: str, valor: float,
                  tipo: str, mes: str) -> None:
    with SessionLocal() as db:
        db.add(Renda(
            user_id=user_id,
            descricao=descricao.strip(),
            valor=valor,
            tipo=tipo,
            mes=mes,
        ))
        db.commit()


def listar_rendas(user_id: int, mes: str) -> list[dict]:
    with SessionLocal() as db:
        rows = (
            db.query(Renda)
            .filter(Renda.user_id == user_id, Renda.mes == mes)
            .order_by(Renda.tipo, Renda.descricao)
            .all()
        )
        return [_renda_to_dict(r) for r in rows]


def total_renda(user_id: int, mes: str) -> float:
    with SessionLocal() as db:
        rows = (
            db.query(Renda.valor)
            .filter(Renda.user_id == user_id, Renda.mes == mes)
            .all()
        )
        return sum(r.valor for r in rows)


def deletar_renda(renda_id: int) -> None:
    with SessionLocal() as db:
        obj = db.query(Renda).filter(Renda.id == renda_id).first()
        if obj:
            db.delete(obj)
            db.commit()


# ── Gastos ─────────────────────────────────────────────────────────────────

def inserir_gasto(user_id: int, descricao: str, categoria: str,
                  valor: float, data_gasto: date | str) -> None:
    if isinstance(data_gasto, str):
        data_gasto = date.fromisoformat(data_gasto)
    with SessionLocal() as db:
        db.add(Gasto(
            user_id=user_id,
            descricao=descricao.strip(),
            categoria=categoria,
            valor=valor,
            data=data_gasto,
        ))
        db.commit()


def listar_gastos(user_id: int, mes: str) -> list[dict]:
    """mes no formato YYYY-MM"""
    ano, m = mes.split("-")
    with SessionLocal() as db:
        rows = (
            db.query(Gasto)
            .filter(
                Gasto.user_id == user_id,
                Gasto.data >= date(int(ano), int(m), 1),
                Gasto.data <= _ultimo_dia_mes(int(ano), int(m)),
            )
            .order_by(Gasto.data.desc())
            .all()
        )
        return [_gasto_to_dict(g) for g in rows]


def total_gastos(user_id: int, mes: str) -> float:
    return sum(g["valor"] for g in listar_gastos(user_id, mes))


def gastos_por_categoria(user_id: int, mes: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for g in listar_gastos(user_id, mes):
        result[g["categoria"]] = result.get(g["categoria"], 0.0) + g["valor"]
    return result


def deletar_gasto(gasto_id: int) -> None:
    with SessionLocal() as db:
        obj = db.query(Gasto).filter(Gasto.id == gasto_id).first()
        if obj:
            db.delete(obj)
            db.commit()


# ── Dívidas ────────────────────────────────────────────────────────────────

def inserir_divida(user_id: int, descricao: str, valor_total: float,
                   valor_parcela: float, parcelas_restantes: int,
                   taxa_juros: float, vencimento: int | None) -> None:
    with SessionLocal() as db:
        db.add(Divida(
            user_id=user_id,
            descricao=descricao.strip(),
            valor_total=valor_total,
            valor_parcela=valor_parcela,
            parcelas_restantes=int(parcelas_restantes),
            taxa_juros=taxa_juros or 0.0,
            vencimento=int(vencimento) if vencimento else None,
        ))
        db.commit()


def listar_dividas(user_id: int, apenas_ativas: bool = True) -> list[dict]:
    with SessionLocal() as db:
        q = db.query(Divida).filter(Divida.user_id == user_id)
        if apenas_ativas:
            q = q.filter(Divida.ativa == True)
        rows = q.order_by(Divida.vencimento.nullslast(), Divida.descricao).all()
        return [_divida_to_dict(d) for d in rows]


def total_parcelas_mensais(user_id: int) -> float:
    with SessionLocal() as db:
        rows = (
            db.query(Divida.valor_parcela)
            .filter(Divida.user_id == user_id, Divida.ativa == True)
            .all()
        )
        return sum(r.valor_parcela for r in rows)


def maior_taxa_juros(user_id: int) -> float:
    """Retorna a maior taxa de juros entre as dívidas ativas."""
    with SessionLocal() as db:
        rows = (
            db.query(Divida.taxa_juros)
            .filter(Divida.user_id == user_id, Divida.ativa == True)
            .all()
        )
        if not rows:
            return 0.0
        return max(r.taxa_juros for r in rows)


def encerrar_divida(divida_id: int) -> None:
    with SessionLocal() as db:
        obj = db.query(Divida).filter(Divida.id == divida_id).first()
        if obj:
            obj.ativa = False
            db.commit()


def deletar_divida(divida_id: int) -> None:
    with SessionLocal() as db:
        obj = db.query(Divida).filter(Divida.id == divida_id).first()
        if obj:
            db.delete(obj)
            db.commit()


def calcular_indicadores(user_id: int, mes: str) -> dict:
    """
    Agrega todos os indicadores financeiros do mês em um único dict.
    Este é o payload que alimenta o ia_engine.py.

    Retorno:
        {
          renda_total, total_gastos, total_parcelas,
          qtd_dividas, maior_taxa, gastos_por_cat,
          saldo_bruto
        }
    """
    renda    = total_renda(user_id, mes)
    gastos   = total_gastos(user_id, mes)
    parcelas = total_parcelas_mensais(user_id)
    dividas  = listar_dividas(user_id, apenas_ativas=True)
    taxa_max = maior_taxa_juros(user_id)
    gast_cat = gastos_por_categoria(user_id, mes)

    return {
        "renda_total":     renda,
        "total_gastos":    gastos,
        "total_parcelas":  parcelas,
        "qtd_dividas":     len(dividas),
        "maior_taxa":      taxa_max,
        "gastos_por_cat":  gast_cat,
        "saldo_bruto":     renda - gastos - parcelas,
    }


# ── Utilitários internos ───────────────────────────────────────────────────

def _ultimo_dia_mes(ano: int, mes: int) -> date:
    import calendar
    ultimo = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, ultimo)
