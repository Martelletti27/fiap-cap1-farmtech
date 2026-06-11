# Servico da Fase 4: carrega os modulos de ML da Fase 4 e expoe as funcoes
# necessarias para a dashboard integrada da Fase 7.

import sys
import os

_FASE4_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "Fase 4")
sys.path.insert(0, os.path.abspath(_FASE4_PATH))


def carregar_e_treinar(df_ou_bytes, cultura: str) -> dict:
    import pandas as pd
    import io
    from data_loader import DataLoader
    from phase1_regression import Phase1Regression

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
        "df_completo": df,
    }


def prever_umidade(regression, loader, df, cultura: str,
                   temperatura: float, chuva: float,
                   umidade_ar: float, hora: int) -> dict:
    import pandas as pd
    import sys
    import os

    _FASE4_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "Fase 4")
    if _FASE4_PATH not in sys.path:
        sys.path.insert(0, os.path.abspath(_FASE4_PATH))

    import config as cfg4

    feature_names = regression.feature_names
    features = {f: 0 for f in feature_names}

    if "Temperatura" in feature_names:
        features["Temperatura"] = temperatura
    if "Chuva Real (mm)" in feature_names:
        features["Chuva Real (mm)"] = chuva
    if "Umidade do Ar" in feature_names:
        features["Umidade do Ar"] = umidade_ar
    if "Hora" in feature_names:
        features["Hora"] = hora

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

    X_input = __import__("pandas").DataFrame([{k: features[k] for k in feature_names}])
    umidade = regression.predict(X_input)[0]

    irrigar = umidade < 30 and chuva == 0 and umidade_ar < 60
    if umidade < 20:
        irrigar = True

    return {"umidade_prevista": umidade, "irrigar": irrigar}


def comparar_modelos(regression) -> "pd.DataFrame":
    import pandas as pd
    if not regression or not regression.results:
        return pd.DataFrame()
    df_res = pd.DataFrame(regression.results).T
    df_res = df_res[["MAE_test", "MSE_test", "RMSE_test", "R2_test"]]
    df_res.columns = ["MAE", "MSE", "RMSE", "R²"]
    return df_res.round(4)
