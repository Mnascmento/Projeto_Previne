"""
modules/conteudo.py

Sistema de recomendação de conteúdo educativo contextualizado (HU-10).

Arquitetura: regras + filtragem por perfil (sem ML).
Fonte: assets/conteudos.json — base estática editável sem tocar em código.

Pipeline de recomendação:
  1. Carregar todos os conteúdos do JSON
  2. Filtrar por nível de risco (ou "todos")
  3. Opcionalmente filtrar por categoria de gasto dominante
  4. Embaralhar e retornar `quantidade` itens
  5. Fallback para conteúdos embutidos se JSON não existir
"""

from __future__ import annotations
import json
import random
from pathlib import Path

CONTEUDOS_PATH = Path("assets/conteudos.json")


def obter_dicas(
    nivel_risco: str,
    quantidade: int = 3,
    categoria_dominante: str | None = None,
) -> list[dict]:
    """
    Retorna dicas filtradas pelo nível de risco e opcionalmente
    pela categoria de gasto mais alta do usuário.

    nivel_risco: 'baixo' | 'medio' | 'alto' | 'critico'
    """
    conteudos = _carregar_conteudos()

    # Filtro primário: nível de risco
    filtrados = [
        c for c in conteudos
        if nivel_risco in c.get("niveis", []) or "todos" in c.get("niveis", [])
    ]

    # Filtro secundário: categoria dominante (se informada)
    if categoria_dominante and filtrados:
        por_cat = [
            c for c in filtrados
            if categoria_dominante.lower() in (c.get("categoria", "")).lower()
        ]
        # Só aplicar filtro de categoria se sobrar conteúdo suficiente
        if len(por_cat) >= quantidade:
            filtrados = por_cat

    # Fallback: se ficou vazio, usa tudo
    if not filtrados:
        filtrados = conteudos

    random.shuffle(filtrados)
    return filtrados[:quantidade]


def obter_todos_por_nivel(nivel_risco: str) -> list[dict]:
    """Retorna todos os conteúdos para um dado nível, sem limite."""
    conteudos = _carregar_conteudos()
    return [
        c for c in conteudos
        if nivel_risco in c.get("niveis", []) or "todos" in c.get("niveis", [])
    ]


# ── I/O ────────────────────────────────────────────────────────────────────

def _carregar_conteudos() -> list[dict]:
    if CONTEUDOS_PATH.exists():
        try:
            with open(CONTEUDOS_PATH, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return _conteudos_embutidos()


def _conteudos_embutidos() -> list[dict]:
    """
    Conteúdo fallback — usado se assets/conteudos.json não existir ou
    estiver corrompido. Cobre todos os níveis de risco.
    """
    return [
        {
            "titulo": "Regra 50-30-20",
            "corpo": (
                "Divida sua renda em: 50% para necessidades, 30% para desejos "
                "e 20% para poupança e dívidas. É um ponto de partida simples e eficaz."
            ),
            "niveis": ["todos"],
            "emoji": "📊",
            "categoria": "",
        },
        {
            "titulo": "Método avalanche de dívidas",
            "corpo": (
                "Pague o mínimo em todas as dívidas e direcione o valor extra "
                "para a dívida com MAIOR juros. Você pagará menos no total."
            ),
            "niveis": ["medio", "alto", "critico"],
            "emoji": "🏔️",
            "categoria": "",
        },
        {
            "titulo": "Fundo de emergência",
            "corpo": (
                "Ter de 3 a 6 meses de despesas guardadas evita que imprevistos "
                "virem dívidas. Comece com R$ 50/mês e aumente gradualmente."
            ),
            "niveis": ["baixo", "medio"],
            "emoji": "🛡️",
            "categoria": "",
        },
        {
            "titulo": "Juros do cartão de crédito",
            "corpo": (
                "O rotativo do cartão pode passar de 400% ao ano. "
                "Pague sempre o valor total da fatura — nunca o mínimo."
            ),
            "niveis": ["medio", "alto", "critico"],
            "emoji": "💳",
            "categoria": "",
        },
        {
            "titulo": "Lei do Superendividamento",
            "corpo": (
                "A Lei 14.181/2021 garante direito à renegociação com proteção "
                "ao mínimo existencial. Procure o Procon da sua cidade."
            ),
            "niveis": ["alto", "critico"],
            "emoji": "⚖️",
            "categoria": "",
        },
        {
            "titulo": "Compras por impulso",
            "corpo": (
                "Antes de comprar algo não planejado, espere 48 horas. "
                "Se ainda quiser, avalie se cabe no orçamento. Esse hábito economiza muito."
            ),
            "niveis": ["todos"],
            "emoji": "🛍️",
            "categoria": "Lazer",
        },
        {
            "titulo": "Orçamento base zero",
            "corpo": (
                "Planeje cada real da sua renda antes de receber: atribua destino a tudo. "
                "Ao final: renda - despesas - poupança = 0."
            ),
            "niveis": ["baixo", "medio"],
            "emoji": "🎯",
            "categoria": "",
        },
        {
            "titulo": "Negociação de dívidas",
            "corpo": (
                "Credores preferem receber menos a não receber nada. "
                "Proponha pagar à vista com desconto — muitos aceitam 40% de redução."
            ),
            "niveis": ["alto", "critico"],
            "emoji": "🤝",
            "categoria": "",
        },
        {
            "titulo": "Custo do parcelamento",
            "corpo": (
                "Parcelar 'sem juros' tem custo embutido no preço. "
                "Compare o preço à vista com o total parcelado antes de decidir."
            ),
            "niveis": ["todos"],
            "emoji": "🧮",
            "categoria": "",
        },
        {
            "titulo": "Método bola de neve",
            "corpo": (
                "Pague a menor dívida primeiro para ganhar motivação, "
                "depois aplique o valor liberado na próxima. Psicologicamente mais fácil."
            ),
            "niveis": ["medio", "alto"],
            "emoji": "⛄",
            "categoria": "",
        },
        {
            "titulo": "Gasto com alimentação",
            "corpo": (
                "Planejar o cardápio semanal e fazer uma lista antes do mercado "
                "reduz o gasto com alimentação em até 30%."
            ),
            "niveis": ["todos"],
            "emoji": "🛒",
            "categoria": "Alimentação",
        },
        {
            "titulo": "Transporte inteligente",
            "corpo": (
                "Combinar transporte público com aplicativo nos dias de pico "
                "pode reduzir o custo de transporte em até 40% comparado ao carro próprio."
            ),
            "niveis": ["todos"],
            "emoji": "🚌",
            "categoria": "Transporte",
        },
    ]
