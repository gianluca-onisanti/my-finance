"""Módulo de gerenciamento de dados - leitura/escrita de CSV e lógica de frequências."""

import os
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

RECEITAS_FILE = os.path.join(DATA_DIR, "receitas.csv")
DESPESAS_FILE = os.path.join(DATA_DIR, "despesas.csv")
METAS_FILE = os.path.join(DATA_DIR, "metas.csv")
CATEGORIAS_RECEITA_FILE = os.path.join(DATA_DIR, "categorias_receita.csv")
CATEGORIAS_DESPESA_FILE = os.path.join(DATA_DIR, "categorias_despesa.csv")

FREQUENCIAS = {
    "Mensal": 1,
    "Semanal": 4.33,
    "Quinzenal": 2,
    "Bimestral": 1 / 2,
    "Trimestral": 1 / 3,
    "Semestral": 1 / 6,
    "Anual": 1 / 12,
    "Pontual": 0,
}

_CATEGORIAS_RECEITA_DEFAULT = [
    "Salário",
    "Freelance",
    "Investimentos",
    "Aluguel",
    "Pensão",
    "Bônus",
    "Outros",
]

_CATEGORIAS_DESPESA_DEFAULT = [
    "Moradia",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Educação",
    "Lazer",
    "Vestuário",
    "Assinaturas",
    "Seguros",
    "Impostos",
    "Dívidas",
    "Pets",
    "Presentes",
    "Investimentos",
    "Outros",
]


# --- Categorias ---

def _load_categorias(filepath: str, defaults: list[str]) -> list[str]:
    _ensure_data_dir()
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return df["categoria"].tolist()
    # Criar arquivo com defaults na primeira vez
    df = pd.DataFrame({"categoria": defaults})
    df.to_csv(filepath, index=False)
    return defaults


def _save_categorias(filepath: str, categorias: list[str]):
    _ensure_data_dir()
    pd.DataFrame({"categoria": categorias}).to_csv(filepath, index=False)


def load_categorias_receita() -> list[str]:
    return _load_categorias(CATEGORIAS_RECEITA_FILE, _CATEGORIAS_RECEITA_DEFAULT)


def load_categorias_despesa() -> list[str]:
    return _load_categorias(CATEGORIAS_DESPESA_FILE, _CATEGORIAS_DESPESA_DEFAULT)


def add_categoria_receita(nome: str) -> list[str]:
    cats = load_categorias_receita()
    if nome not in cats:
        cats.append(nome)
        _save_categorias(CATEGORIAS_RECEITA_FILE, cats)
    return cats


def add_categoria_despesa(nome: str) -> list[str]:
    cats = load_categorias_despesa()
    if nome not in cats:
        cats.append(nome)
        _save_categorias(CATEGORIAS_DESPESA_FILE, cats)
    return cats


def delete_categoria_receita(nome: str) -> list[str]:
    cats = load_categorias_receita()
    cats = [c for c in cats if c != nome]
    _save_categorias(CATEGORIAS_RECEITA_FILE, cats)
    return cats


def delete_categoria_despesa(nome: str) -> list[str]:
    cats = load_categorias_despesa()
    cats = [c for c in cats if c != nome]
    _save_categorias(CATEGORIAS_DESPESA_FILE, cats)
    return cats

RECEITAS_COLUMNS = {
    "id": "int64",
    "descricao": "str",
    "valor": "float64",
    "frequencia": "str",
    "categoria": "str",
    "data_inicio": "str",
    "ativo": "bool",
}

DESPESAS_COLUMNS = {
    "id": "int64",
    "descricao": "str",
    "valor": "float64",
    "frequencia": "str",
    "categoria": "str",
    "destinatario": "str",
    "data_inicio": "str",
    "dia_vencimento": "Int64",
    "parcelas_total": "Int64",
    "parcelas_pagas": "Int64",
    "ativo": "bool",
}

METAS_COLUMNS = {
    "id": "int64",
    "descricao": "str",
    "valor_alvo": "float64",
    "valor_atual": "float64",
    "data_limite": "str",
    "categoria": "str",
    "ativo": "bool",
}


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_csv(filepath: str, columns: dict) -> pd.DataFrame:
    _ensure_data_dir()
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, dtype={"dia_vencimento": "Int64", "parcelas_total": "Int64", "parcelas_pagas": "Int64"})
        for col, dtype in columns.items():
            if col not in df.columns:
                if dtype == "bool":
                    df[col] = True
                elif dtype in ("Int64", "int64"):
                    df[col] = pd.NA
                elif dtype == "float64":
                    df[col] = 0.0
                else:
                    df[col] = ""
        return df
    dtypes = {}
    for col, dtype in columns.items():
        if dtype == "bool":
            dtypes[col] = "bool"
        elif dtype == "float64":
            dtypes[col] = "float64"
        elif dtype in ("int64", "Int64"):
            dtypes[col] = "Int64"
        else:
            dtypes[col] = "object"
    return pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in dtypes.items()})


def _save_csv(df: pd.DataFrame, filepath: str):
    _ensure_data_dir()
    df.to_csv(filepath, index=False)


def _next_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


# --- Receitas ---

def load_receitas() -> pd.DataFrame:
    return _load_csv(RECEITAS_FILE, RECEITAS_COLUMNS)


def add_receita(descricao: str, valor: float, frequencia: str, categoria: str, data_inicio: str) -> pd.DataFrame:
    df = load_receitas()
    new_row = pd.DataFrame([{
        "id": _next_id(df),
        "descricao": descricao,
        "valor": valor,
        "frequencia": frequencia,
        "categoria": categoria,
        "data_inicio": data_inicio,
        "ativo": True,
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    _save_csv(df, RECEITAS_FILE)
    return df


def update_receita(id: int, **kwargs) -> pd.DataFrame:
    df = load_receitas()
    for key, value in kwargs.items():
        df.loc[df["id"] == id, key] = value
    _save_csv(df, RECEITAS_FILE)
    return df


def toggle_receita(id: int) -> pd.DataFrame:
    df = load_receitas()
    current = df.loc[df["id"] == id, "ativo"].values[0]
    df.loc[df["id"] == id, "ativo"] = not current
    _save_csv(df, RECEITAS_FILE)
    return df


def delete_receita(id: int) -> pd.DataFrame:
    df = load_receitas()
    df = df[df["id"] != id].reset_index(drop=True)
    _save_csv(df, RECEITAS_FILE)
    return df


# --- Despesas ---

def load_despesas() -> pd.DataFrame:
    return _load_csv(DESPESAS_FILE, DESPESAS_COLUMNS)


def add_despesa(descricao: str, valor: float, frequencia: str, categoria: str,
                data_inicio: str, dia_vencimento: int = None,
                parcelas_total: int = None, parcelas_pagas: int = None,
                destinatario: str = "") -> pd.DataFrame:
    df = load_despesas()
    new_row = pd.DataFrame([{
        "id": _next_id(df),
        "descricao": descricao,
        "valor": valor,
        "frequencia": frequencia,
        "categoria": categoria,
        "destinatario": destinatario,
        "data_inicio": data_inicio,
        "dia_vencimento": dia_vencimento,
        "parcelas_total": parcelas_total,
        "parcelas_pagas": parcelas_pagas,
        "ativo": True,
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    _save_csv(df, DESPESAS_FILE)
    return df


def update_despesa(id: int, **kwargs) -> pd.DataFrame:
    df = load_despesas()
    for key, value in kwargs.items():
        df.loc[df["id"] == id, key] = value
    _save_csv(df, DESPESAS_FILE)
    return df


def toggle_despesa(id: int) -> pd.DataFrame:
    df = load_despesas()
    current = df.loc[df["id"] == id, "ativo"].values[0]
    df.loc[df["id"] == id, "ativo"] = not current
    _save_csv(df, DESPESAS_FILE)
    return df


def delete_despesa(id: int) -> pd.DataFrame:
    df = load_despesas()
    df = df[df["id"] != id].reset_index(drop=True)
    _save_csv(df, DESPESAS_FILE)
    return df


# --- Metas ---

def load_metas() -> pd.DataFrame:
    return _load_csv(METAS_FILE, METAS_COLUMNS)


def add_meta(descricao: str, valor_alvo: float, valor_atual: float,
             data_limite: str, categoria: str) -> pd.DataFrame:
    df = load_metas()
    new_row = pd.DataFrame([{
        "id": _next_id(df),
        "descricao": descricao,
        "valor_alvo": valor_alvo,
        "valor_atual": valor_atual,
        "data_limite": data_limite,
        "categoria": categoria,
        "ativo": True,
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    _save_csv(df, METAS_FILE)
    return df


def update_meta(id: int, **kwargs) -> pd.DataFrame:
    df = load_metas()
    for key, value in kwargs.items():
        df.loc[df["id"] == id, key] = value
    _save_csv(df, METAS_FILE)
    return df


def delete_meta(id: int) -> pd.DataFrame:
    df = load_metas()
    df = df[df["id"] != id].reset_index(drop=True)
    _save_csv(df, METAS_FILE)
    return df


# --- Cálculos ---

def valor_mensal(valor: float, frequencia: str) -> float:
    """Converte qualquer valor com frequência para equivalente mensal."""
    fator = FREQUENCIAS.get(frequencia, 0)
    return valor * fator


def valor_anual(valor: float, frequencia: str) -> float:
    """Converte qualquer valor com frequência para equivalente anual."""
    return valor_mensal(valor, frequencia) * 12


def total_receitas_mensal(df: pd.DataFrame = None) -> float:
    if df is None:
        df = load_receitas()
    ativos = df[df["ativo"] == True]
    return sum(valor_mensal(row["valor"], row["frequencia"]) for _, row in ativos.iterrows())


def total_despesas_mensal(df: pd.DataFrame = None) -> float:
    if df is None:
        df = load_despesas()
    ativos = df[df["ativo"] == True]
    total = 0.0
    for _, row in ativos.iterrows():
        freq = row["frequencia"]
        if freq == "Parcelado":
            parcelas_total = row.get("parcelas_total", 0)
            parcelas_pagas = row.get("parcelas_pagas", 0)
            if pd.notna(parcelas_total) and pd.notna(parcelas_pagas) and parcelas_pagas < parcelas_total:
                total += row["valor"] / parcelas_total
        else:
            total += valor_mensal(row["valor"], freq)
    return total


def saldo_mensal() -> float:
    return total_receitas_mensal() - total_despesas_mensal()


def taxa_poupanca() -> float:
    """Retorna a taxa de poupança (% da renda que sobra)."""
    receitas = total_receitas_mensal()
    if receitas == 0:
        return 0.0
    return (saldo_mensal() / receitas) * 100


def despesas_por_categoria(df: pd.DataFrame = None) -> pd.DataFrame:
    if df is None:
        df = load_despesas()
    ativos = df[df["ativo"] == True].copy()
    if ativos.empty:
        return pd.DataFrame(columns=["categoria", "valor_mensal"])
    ativos["valor_mensal"] = ativos.apply(
        lambda row: row["valor"] / row["parcelas_total"] if row["frequencia"] == "Parcelado" and pd.notna(row.get("parcelas_total")) and pd.notna(row.get("parcelas_pagas")) and row["parcelas_pagas"] < row["parcelas_total"]
        else valor_mensal(row["valor"], row["frequencia"]),
        axis=1,
    )
    return ativos.groupby("categoria")["valor_mensal"].sum().reset_index().sort_values("valor_mensal", ascending=False)


def receitas_por_categoria(df: pd.DataFrame = None) -> pd.DataFrame:
    if df is None:
        df = load_receitas()
    ativos = df[df["ativo"] == True].copy()
    if ativos.empty:
        return pd.DataFrame(columns=["categoria", "valor_mensal"])
    ativos["valor_mensal"] = ativos.apply(
        lambda row: valor_mensal(row["valor"], row["frequencia"]), axis=1
    )
    return ativos.groupby("categoria")["valor_mensal"].sum().reset_index().sort_values("valor_mensal", ascending=False)


def despesas_por_destinatario(df: pd.DataFrame = None) -> pd.DataFrame:
    if df is None:
        df = load_despesas()
    ativos = df[df["ativo"] == True].copy()
    # Filtrar apenas quem tem destinatário preenchido
    ativos = ativos[ativos["destinatario"].fillna("").str.strip() != ""]
    if ativos.empty:
        return pd.DataFrame(columns=["destinatario", "valor_mensal"])
    ativos["valor_mensal"] = ativos.apply(
        lambda row: row["valor"] / row["parcelas_total"] if row["frequencia"] == "Parcelado" and pd.notna(row.get("parcelas_total")) and pd.notna(row.get("parcelas_pagas")) and row["parcelas_pagas"] < row["parcelas_total"]
        else valor_mensal(row["valor"], row["frequencia"]),
        axis=1,
    )
    return ativos.groupby("destinatario")["valor_mensal"].sum().reset_index().sort_values("valor_mensal", ascending=False)


def exportar_xlsx(filepath: str):
    """Exporta todos os dados para um arquivo .xlsx com abas separadas."""
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        load_receitas().to_excel(writer, sheet_name="Receitas", index=False)
        load_despesas().to_excel(writer, sheet_name="Despesas", index=False)
        load_metas().to_excel(writer, sheet_name="Metas", index=False)
