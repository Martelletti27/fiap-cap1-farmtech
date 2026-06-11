# Servico da Fase 4: carrega os modulos de ML da Fase 4 sem colidir com o config.py da Fase 7.
# O problema: data_loader.py da Fase 4 faz "import config" e o Python encontra o config
# da Fase 7 (ja em cache). A solucao e substituir temporariamente sys.modules['config']
# pelo config correto da Fase 4 durante o import, depois restaurar.

import importlib.util
import sys
import os

_FASE4_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Fase 4"))


def _carregar_config_fase4():
    spec = importlib.util.spec_from_file_location(
        "fase4_config", os.path.join(_FASE4_PATH, "config.py")
    )
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    return cfg


def _importar_modulos_fase4():
    cfg4 = _carregar_config_fase4()

    # substitui temporariamente 'config' no cache para que data_loader e phase1_regression
    # encontrem o config correto (Fase 4) ao importar
    config_original = sys.modules.get("config")
    sys.modules["config"] = cfg4

    # remove do cache para forccar reimport com o config correto agora no lugar
    for nome in ["data_loader", "phase1_regression"]:
        sys.modules.pop(nome, None)

    if _FASE4_PATH not in sys.path:
        sys.path.insert(0, _FASE4_PATH)

    try:
        from data_loader import DataLoader
        from phase1_regression import Phase1Regression
    finally:
        # restaura o config da Fase 7
        if config_original is not None:
            sys.modules["config"] = config_original
        else:
            sys.modules.pop("config", None)

    return DataLoader, Phase1Regression, cfg4


def carregar_e_treinar(df_ou_bytes, cultura: str) -> dict:
    import pandas as pd
    import io

    DataLoader, Phase1Regression, _ = _importar_modulos_fase4()

    loader = DataLoader()

    if isinstance(df_ou_bytes, bytes):
        df = pd.read_csv(io.BytesIO(df_ou_bytes))
    else:
        df = df_ou_bytes

    loader.df = df.copy()

    df_filtrado = df.copy()
    if "Cultura" in df.columns:
        candidatos = df[df["Cultura"] == cultura]
        if len(candidatos) >= 50:
            df_filtrado = candidatos.copy()

    X, y, _ = loader.preprocess_for_regression()

    regression = Phase1Regression()
    regression.initialize_models()
    regression.train_models(X, y)
    regression.get_best_model()

    return {
        "regression": regression,
        "loader": loader,
        "df": df_filtrado,
    }


def prever_umidade(regression, df, cultura: str,
                   temperatura: float, chuva: float,
                   umidade_ar: float, hora: int) -> dict:
    import pandas as pd

    _, _, cfg4 = _importar_modulos_fase4()

    feature_names = regression.feature_names
    features = {f: 0 for f in feature_names}

    mapa = {
        "Temperatura": temperatura,
        "Chuva Real (mm)": chuva,
        "Umidade do Ar": umidade_ar,
        "Hora": hora,
    }
    for chave, valor in mapa.items():
        if chave in feature_names:
            features[chave] = valor

    for col in ["PH", "Nível de Nitrogênio", "Nível de Fósforo", "Nível de Potássio", "Probabilidade de Chuva"]:
        if col in feature_names and col in df.columns:
            features[col] = df[col].mean()

    for f in feature_names:
        if f.startswith("Cultura_"):
            features[f] = 1 if f == f"Cultura_{cultura}" else 0
        if f.startswith("Estagio_"):
            estagios = cfg4.ESTAGIOS_POR_CULTURA.get(cultura, ["Vegetativo"])
            padrao = estagios[len(estagios) // 2]
            features[f] = 1 if f == f"Estagio_{padrao}" else 0

    X_input = pd.DataFrame([{k: features[k] for k in feature_names}])
    umidade = regression.predict(X_input)[0]

    irrigar = (umidade < 20) or (umidade < 30 and chuva == 0 and umidade_ar < 60)

    return {"umidade_prevista": umidade, "irrigar": irrigar}


def comparar_modelos(regression) -> "pd.DataFrame":
    import pandas as pd
    if not regression or not regression.results:
        return pd.DataFrame()
    df_res = pd.DataFrame(regression.results).T
    df_res = df_res[["MAE_test", "MSE_test", "RMSE_test", "R2_test"]]
    df_res.columns = ["MAE", "MSE", "RMSE", "R²"]
    return df_res.round(4)
