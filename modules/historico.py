"""
modules/historico.py

Módulo de persistência e consulta do histórico de risco.

Responsabilidades:
  - Salvar o resultado do ia_engine após cada cálculo (chamado pelo dashboard)
  - Consultar evolução do índice ao longo dos meses
  - Alimentar o gráfico de linha da página de Relatório

Decisão: apenas um registro por mês por usuário. Se o dashboard
for acessado múltiplas vezes no mesmo mês, o registro é atualizado
(não duplicado) — isso reflete sempre o estado atual do mês.
"""

from __future__ import annotations
from datetime import datetime

from models.schemas import SessionLocal, HistoricoRisco
from modules.ia_engine import ResultadoRisco


def salvar_historico(user_id: int, mes: str, resultado: ResultadoRisco) -> None:
    """
    Persiste (ou atualiza) o resultado do cálculo de risco para o mês.
    mes: formato YYYY-MM
    """
    with SessionLocal() as db:
        existente = (
            db.query(HistoricoRisco)
            .filter(HistoricoRisco.user_id == user_id, HistoricoRisco.mes == mes)
            .first()
        )
        if existente:
            existente.indice          = resultado.indice
            existente.nivel           = resultado.nivel
            existente.comprometimento = resultado.comprometimento
            existente.saldo_livre     = resultado.saldo_livre
            existente.calculado_em    = datetime.utcnow()
        else:
            db.add(HistoricoRisco(
                user_id=user_id,
                mes=mes,
                indice=resultado.indice,
                nivel=resultado.nivel,
                comprometimento=resultado.comprometimento,
                saldo_livre=resultado.saldo_livre,
            ))
        db.commit()


def listar_historico(user_id: int, ultimos_n: int = 12) -> list[dict]:
    """
    Retorna os últimos N meses de histórico de risco em ordem crescente.
    Usado para o gráfico de evolução no relatório.
    """
    with SessionLocal() as db:
        rows = (
            db.query(HistoricoRisco)
            .filter(HistoricoRisco.user_id == user_id)
            .order_by(HistoricoRisco.mes.desc())
            .limit(ultimos_n)
            .all()
        )
        # Inverter para ordem cronológica
        rows = list(reversed(rows))
        return [
            {
                "mes":             r.mes,
                "indice":          r.indice,
                "nivel":           r.nivel,
                "comprometimento": r.comprometimento,
                "saldo_livre":     r.saldo_livre,
                "calculado_em":    r.calculado_em.isoformat() if r.calculado_em else None,
            }
            for r in rows
        ]


def obter_historico_mes(user_id: int, mes: str) -> dict | None:
    """Retorna o registro de um mês específico ou None."""
    with SessionLocal() as db:
        row = (
            db.query(HistoricoRisco)
            .filter(HistoricoRisco.user_id == user_id, HistoricoRisco.mes == mes)
            .first()
        )
        if not row:
            return None
        return {
            "mes":             row.mes,
            "indice":          row.indice,
            "nivel":           row.nivel,
            "comprometimento": row.comprometimento,
            "saldo_livre":     row.saldo_livre,
        }
