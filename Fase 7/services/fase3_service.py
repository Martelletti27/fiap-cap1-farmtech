# Servico da Fase 3: leitura e analise dos dados de sensores do ESP32.
# Fonte: Fase 3/assets/fase2_sensor_readings.csv (separador ; decimal ,)

import pandas as pd
import sys
import os

# adiciona a Fase 2 ao path para reutilizar o cliente Open-Meteo
_FASE2_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "Fase 2", "apps")
sys.path.insert(0, os.path.abspath(_FASE2_PATH))

from config import CSV_SENSORES, LIMITE_UMIDADE_MIN, PH_MIN, PH_MAX


def carregar_leituras() -> pd.DataFrame:
    df = pd.read_csv(CSV_SENSORES, sep=";", decimal=",")
    # padroniza a coluna de timestamp para facilitar os graficos
    df["timestamp"] = pd.to_datetime(
        df["captured_date"].astype(str) + " " + df["captured_time"].astype(str),
        errors="coerce",
    )
    return df


def estatisticas(df: pd.DataFrame) -> dict:
    cols = ["soil_moisture_percent", "ph", "temperature_c", "humidity_percent"]
    stats = {}
    for col in cols:
        if col in df.columns:
            stats[col] = {
                "media": df[col].mean(),
                "min": df[col].min(),
                "max": df[col].max(),
            }
    return stats


def detectar_anomalias(df: pd.DataFrame) -> pd.DataFrame:
    # classifica cada leitura com a anomalia mais critica encontrada
    linhas = []
    for _, row in df.iterrows():
        alertas = []
        if row.get("soil_moisture_percent", 100) < LIMITE_UMIDADE_MIN:
            alertas.append(f"Umidade critica ({row['soil_moisture_percent']:.1f}%)")
        if not (PH_MIN <= row.get("ph", 6.0) <= PH_MAX):
            alertas.append(f"pH fora da faixa ({row['ph']:.2f})")
        if row.get("nitrogen_alert", 0) == 1:
            alertas.append("Nitrogenio baixo")
        if row.get("phosphorus_alert", 0) == 1:
            alertas.append("Fosforo baixo")
        if row.get("potassium_alert", 0) == 1:
            alertas.append("Potassio baixo")
        linhas.append({
            "timestamp": row.get("timestamp"),
            "umidade": row.get("soil_moisture_percent"),
            "ph": row.get("ph"),
            "temperatura": row.get("temperature_c"),
            "comando": row.get("irrigation_command"),
            "anomalias": "; ".join(alertas) if alertas else "OK",
            "tem_alerta": len(alertas) > 0,
        })
    return pd.DataFrame(linhas)


def resumo_alertas(df_anomalias: pd.DataFrame) -> dict:
    total = len(df_anomalias)
    com_alerta = int(df_anomalias["tem_alerta"].sum())
    return {
        "total_leituras": total,
        "leituras_com_alerta": com_alerta,
    }


# acoes corretivas associadas a cada tipo de anomalia
# usadas tanto na dashboard quanto no servico de alerta da AWS
ACOES_CORRETIVAS = {
    "Umidade critica": "Acionar irrigacao imediata no talhao.",
    "pH fora da faixa": "Aplicar correcao de acidez (calcario) ou acidificante conforme laudo.",
    "Nitrogenio baixo": "Programar adubacao nitrogenada de cobertura.",
    "Fosforo baixo": "Aplicar adubacao fosfatada conforme analise de solo.",
    "Potassio baixo": "Programar adubacao potassica de manutencao.",
}


def acoes_para_anomalias(anomalias_str: str) -> list[str]:
    if not anomalias_str or anomalias_str == "OK":
        return []
    acoes = []
    for chave, acao in ACOES_CORRETIVAS.items():
        if chave in anomalias_str:
            acoes.append(acao)
    return acoes


# ------------------------
# PREVISAO METEOROLOGICA (Fase 2 — Open-Meteo)
# O path ja foi inserido no topo deste modulo, entao o import funciona normalmente.

def previsao_chuva(lat: float, lon: float) -> dict:
    from python_integration.openmeteo_client import get_token_and_metrics
    _, m = get_token_and_metrics(lat, lon)
    rain_block = (m["rain_mm_12h"] >= 1.0) or (m["pop_max_12h"] >= 60)
    return {
        "rain_mm_12h": m["rain_mm_12h"],
        "pop_max_12h": m["pop_max_12h"],
        "rain_block": rain_block,
    }
