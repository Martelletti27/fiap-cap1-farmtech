import os
import streamlit as st
import plotly.graph_objects as go

import config
from services import fase1_service as f1
from services import fase3_service as f3
from services import fase4_service as f4
from services import fase6_service as f6
from services import aws_alert_service as aws

st.set_page_config(
    page_title="FarmTech Solutions - Fase 7",
    layout="wide"
)

st.title("FarmTech Solutions - Dashboard Integrada")
st.write("Integração das Fases 1 a 6 em uma única aplicação.")

abas = st.tabs([
    "Visão Geral",
    "Fase 1 - Manejo",
    "Fase 2/3 - Sensores e IoT",
    "Fase 4 - Machine Learning",
    "Fase 6 - Visão Computacional",
    "AWS Alertas",
    "Ir Além"
])

with abas[0]:
    st.header("Visão Geral")
    st.write("FarmTech Solutions — sistema integrado de gestão agrícola desenvolvido ao longo das Fases 1 a 6.")

    # metricas rapidas do dataset de sensores
    try:
        _df_vis = f3.carregar_leituras()
        _anom_vis = f3.detectar_anomalias(_df_vis)
        _res_vis = f3.resumo_alertas(_anom_vis)
        _stats_vis = f3.estatisticas(_df_vis)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Leituras de sensor", _res_vis["total_leituras"])
        c2.metric("Umidade média", f"{_stats_vis['soil_moisture_percent']['media']:.1f}%")
        c3.metric("pH médio", f"{_stats_vis['ph']['media']:.2f}")
        c4.metric("Alertas detectados", _res_vis["leituras_com_alerta"])
    except Exception:
        pass

    st.markdown("---")
    st.markdown("""
| Fase | Conteúdo | Status |
|------|----------|--------|
| 1 | Cálculo de área e manejo de insumos (Python + R) | Integrada |
| 2 | Previsão meteorológica Open-Meteo para o ESP32 | Integrada |
| 3 | Sensores ESP32, Oracle, irrigação automatizada | Integrada |
| 4 | Dashboard ML — previsão de umidade com Scikit-Learn | Referenciada |
| 5 | Cloud AWS — infraestrutura, segurança e mensageria SNS | Integrada (SNS) |
| 6 | Visão computacional YOLO — maquinários e animais | Integrada |
""")

    st.markdown("---")
    st.subheader("Como rodar")
    st.code("cd \"Fase 7\"\npip install -r requirements.txt\npython run.py", language="bash")

with abas[1]:
    st.header("Fase 1 - Manejo e Insumos")
    st.write("Calcule a área do talhão e o volume total de insumo para um manejo.")

    col_esq, col_dir = st.columns(2)

    with col_esq:
        cultura = st.selectbox("Cultura", config.config_culturas)
        geometria = st.radio("Geometria do talhão", ["Retangular", "Circular (pivô)"])

        if geometria == "Retangular":
            largura = st.number_input("Largura do talhão (m)", min_value=0.0, value=100.0, step=1.0)
            comprimento = st.number_input("Comprimento do talhão (m)", min_value=0.0, value=200.0, step=1.0)
        else:
            raio = st.number_input("Raio do pivô (m)", min_value=0.0, value=50.0, step=1.0)

    with col_dir:
        manejo = st.selectbox("Manejo", config.classes_manejo)
        # ativos sugeridos para a cultura e o manejo escolhidos
        sugeridos = config.ativo_cultura_manejo.get(cultura, {}).get(manejo, [])
        ativo = st.selectbox("Produto (ativo)", sugeridos) if sugeridos else st.text_input("Produto (ativo)")
        dose_ha = st.number_input("Dose por hectare", min_value=0.0, value=1.2, step=0.1)
        unidade = st.text_input("Unidade", value="L/ha")
        aplicacoes = st.number_input("Número de aplicações", min_value=1, value=1, step=1)

    if st.button("Calcular manejo", type="primary"):
        try:
            # calcula a area conforme a geometria selecionada
            if geometria == "Retangular":
                area = f1.calc_area_retangulo(largura, comprimento)
            else:
                area = f1.calc_area_circulo(raio)

            resumo = f1.calcular_manejo(
                cultura, area, manejo, ativo, dose_ha, unidade, int(aplicacoes)
            )

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Área do talhão", f"{resumo['area_ha']:.4f} ha")
            c2.metric("Área", f"{resumo['area_m2']:.2f} m²")
            c3.metric("Volume total de insumo", f"{resumo['total_insumo']:.2f} {resumo['unidade']}")

            st.success(
                f"{resumo['manejo']} de {resumo['ativo']} na cultura {resumo['cultura']}: "
                f"{resumo['aplicacoes']} aplicação(ões) de {resumo['dose_ha']:.2f} {resumo['unidade']}."
            )
        except ValueError as e:
            st.error(f"Erro: {e}")

with abas[2]:
    st.header("Fase 2/3 - Sensores e IoT")
    st.write("Leituras do ESP32 (Fase 3) e previsão meteorológica via Open-Meteo (Fase 2).")

    # ---- carrega os dados de sensor uma vez por sessão ----
    if "df_sensores" not in st.session_state:
        try:
            st.session_state.df_sensores = f3.carregar_leituras()
            st.session_state.df_anomalias = f3.detectar_anomalias(st.session_state.df_sensores)
        except FileNotFoundError:
            st.session_state.df_sensores = None
            st.session_state.df_anomalias = None

    df_s = st.session_state.df_sensores
    df_a = st.session_state.df_anomalias

    if df_s is None:
        st.error("CSV de sensores não encontrado. Verifique o caminho em config.py.")
    else:
        # ---- metricas gerais ----
        stats = f3.estatisticas(df_s)
        res = f3.resumo_alertas(df_a)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de leituras", res["total_leituras"])
        c2.metric("Umidade média", f"{stats['soil_moisture_percent']['media']:.1f}%")
        c3.metric("pH médio", f"{stats['ph']['media']:.2f}")
        c4.metric("Leituras com alerta", res["leituras_com_alerta"])

        st.markdown("---")

        # ---- graficos de serie temporal ----
        st.subheader("Evolução das leituras")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig_umid = go.Figure()
            fig_umid.add_trace(go.Scatter(
                x=df_s["timestamp"], y=df_s["soil_moisture_percent"],
                mode="lines+markers", name="Umidade solo (%)",
                line=dict(color="steelblue", width=2)
            ))
            fig_umid.add_hline(y=config.LIMITE_UMIDADE_MIN, line_dash="dash",
                               line_color="red", annotation_text="Mínimo crítico")
            fig_umid.update_layout(title="Umidade do Solo (%)", height=320,
                                   xaxis_title="Data/Hora", showlegend=False)
            st.plotly_chart(fig_umid, use_container_width=True)

        with col_g2:
            fig_ph = go.Figure()
            fig_ph.add_trace(go.Scatter(
                x=df_s["timestamp"], y=df_s["ph"],
                mode="lines+markers", name="pH",
                line=dict(color="darkorange", width=2)
            ))
            fig_ph.add_hrect(y0=config.PH_MIN, y1=config.PH_MAX,
                             fillcolor="green", opacity=0.08,
                             annotation_text="Faixa ideal",
                             annotation_position="top left")
            fig_ph.update_layout(title="pH do Solo", height=320,
                                 xaxis_title="Data/Hora", showlegend=False)
            st.plotly_chart(fig_ph, use_container_width=True)

        st.markdown("---")

        # ---- tabela de anomalias ----
        st.subheader("Anomalias detectadas")

        apenas_alertas = st.checkbox("Mostrar apenas leituras com alerta", value=True)
        df_exibir = df_a[df_a["tem_alerta"]] if apenas_alertas else df_a

        st.dataframe(
            df_exibir[["timestamp", "umidade", "ph", "temperatura", "comando", "anomalias"]],
            use_container_width=True, hide_index=True
        )

        # ---- previsao Open-Meteo (Fase 2) ----
        st.markdown("---")
        st.subheader("Previsão meteorológica — Open-Meteo (Fase 2)")

        col_lat, col_lon, col_btn = st.columns([2, 2, 1])
        with col_lat:
            lat_input = st.number_input("Latitude", value=-22.07, format="%.4f")
        with col_lon:
            lon_input = st.number_input("Longitude", value=-45.56, format="%.4f")
        with col_btn:
            st.write("")  # alinha verticalmente
            st.write("")
            buscar = st.button("Buscar previsão")

        if buscar:
            try:
                m = f3.previsao_chuva(lat_input, lon_input)
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("Chuva prevista (12h)", f"{m['rain_mm_12h']} mm")
                cc2.metric("Prob. máx. chuva", f"{m['pop_max_12h']}%")
                cc3.metric("Bloquear irrigação?", "Sim" if m["rain_block"] else "Não",
                           delta="Aguardar chuva" if m["rain_block"] else "Irrigar se necessário")
            except Exception as e:
                st.warning(f"Não foi possível consultar a API meteorológica: {e}")

with abas[3]:
    st.header("Fase 4 - Machine Learning")
    st.write("Previsão de umidade do solo e recomendação de irrigação com Scikit-Learn.")

    # ---- upload e treinamento ----
    arquivo = st.file_uploader(
        "Carregue o CSV de dados (base_sintetica_pivo_2025.csv)",
        type=["csv"],
        help="Arquivo gerado na Fase 4 — pasta Fase 4/data/"
    )
    cultura_ml = st.selectbox("Cultura", ["SOJA", "MILHO", "CAFÉ"], key="cultura_ml")

    if st.button("Carregar e treinar modelos", type="primary"):
        if arquivo is None:
            st.warning("Selecione um arquivo CSV antes de continuar.")
        else:
            with st.spinner("Treinando modelos..."):
                try:
                    resultado = f4.carregar_e_treinar(arquivo.read(), cultura_ml)
                    st.session_state.f4_regression = resultado["regression"]
                    st.session_state.f4_loader = resultado["loader"]
                    st.session_state.f4_df = resultado["df"]
                    st.session_state.f4_cultura = cultura_ml
                    st.success("Modelos treinados com sucesso.")
                except Exception as e:
                    st.error(f"Erro ao treinar: {e}")

    if "f4_regression" in st.session_state:
        reg = st.session_state.f4_regression
        df_ml = st.session_state.f4_df

        st.markdown("---")
        st.subheader("Comparação de modelos")
        df_modelos = f4.comparar_modelos(reg)
        if not df_modelos.empty:
            st.dataframe(df_modelos, use_container_width=True)
            melhor, _ = reg.get_best_model()
            st.success(f"Melhor modelo: **{melhor}** (R² = {df_modelos.loc[melhor, 'R²']:.4f})")

        st.markdown("---")
        st.subheader("Previsão de umidade do solo")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            temp_in = st.number_input("Temperatura (°C)", value=25.0, min_value=0.0, max_value=50.0, step=0.1, key="f4_temp")
            chuva_in = st.number_input("Chuva Real (mm)", value=0.0, min_value=0.0, max_value=100.0, step=0.1, key="f4_chuva")
        with col_p2:
            umid_ar_in = st.number_input("Umidade do Ar (%)", value=60.0, min_value=0.0, max_value=100.0, step=0.1, key="f4_umid")
            hora_in = st.number_input("Hora do dia", value=12, min_value=0, max_value=23, step=1, key="f4_hora")

        if st.button("Prever umidade", key="btn_prever_f4"):
            try:
                prev = f4.prever_umidade(
                    reg, df_ml,
                    st.session_state.f4_cultura,
                    temp_in, chuva_in, umid_ar_in, int(hora_in)
                )
                cp1, cp2 = st.columns(2)
                cp1.metric("Umidade prevista", f"{prev['umidade_prevista']:.2f}%")
                cp2.metric(
                    "Recomendação",
                    "IRRIGAR" if prev["irrigar"] else "NÃO IRRIGAR",
                    delta="Necessário" if prev["irrigar"] else "Adequado"
                )
            except Exception as e:
                st.error(f"Erro na previsão: {e}")

with abas[4]:
    st.header("Fase 6 - Visão Computacional")
    st.write("Detecção de objetos com YOLO nas imagens de teste da lavoura (classes: maquinários / animais).")

    imagens = f6.listar_imagens()

    if not imagens:
        st.warning("Nenhuma imagem encontrada em Fase 6/Parte 1/images/test. Verifique o caminho em config.py.")
    else:
        nomes = [os.path.basename(p) for p in imagens]
        escolhida_nome = st.selectbox("Selecione uma imagem", nomes)
        caminho = imagens[nomes.index(escolhida_nome)]

        confianca = st.slider("Confiança mínima", min_value=0.10, max_value=0.90, value=0.25, step=0.05)

        col_img, col_res = st.columns(2)
        with col_img:
            st.image(caminho, caption="Imagem original", use_container_width=True)

        if st.button("Rodar detecção", type="primary"):
            with st.spinner("Rodando YOLO..."):
                try:
                    resultado = f6.rodar_deteccao(caminho, confianca)

                    with col_res:
                        st.image(resultado["imagem_anotada"], caption="Resultado da detecção",
                                 use_container_width=True)

                    st.markdown("---")

                    if not resultado["usando_modelo_treinado"]:
                        st.caption("Usando YOLOv8n pré-treinado (best.pt da Fase 6 não encontrado).")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total de detecções", resultado["total"])
                    c2.metric("Maquinários", resultado["contagem"].get("maquinarios", 0))
                    c3.metric("Animais", resultado["contagem"].get("animais", 0))

                    acao = f6.acao_para_deteccao(resultado["contagem"])
                    if resultado["total"] > 0:
                        st.warning(f"Ação sugerida: {acao}")
                    else:
                        st.info(acao)

                    if resultado["deteccoes"]:
                        import pandas as pd
                        st.dataframe(
                            pd.DataFrame(resultado["deteccoes"]),
                            use_container_width=True, hide_index=True
                        )
                except Exception as e:
                    st.error(f"Erro na detecção: {e}")

with abas[5]:
    st.header("AWS Alertas")
    st.write("Dispara alertas via AWS SNS para os funcionários da fazenda com as ações corretivas.")

    # avisa se esta em modo simulacao
    if aws._modo_simulacao():
        st.info(
            "Modo simulação ativo: a variável SNS_TOPIC_ARN não está configurada. "
            "O alerta será exibido aqui, mas não será enviado por e-mail/SMS. "
            "Consulte o README para configurar o tópico SNS na AWS."
        )
    else:
        st.success("AWS SNS configurado. Os alertas serão enviados de verdade.")

    st.markdown("---")
    st.subheader("Gerar alerta manualmente")

    # seleciona a origem do alerta
    origem_opts = {
        "Sensor (Fase 3) — última leitura com alerta": "sensores",
        "Visão Computacional (Fase 6) — detecção de animal": "fase6",
        "Personalizado": "custom",
    }
    origem_escolhida = st.selectbox("Origem do alerta", list(origem_opts.keys()))
    modo = origem_opts[origem_escolhida]

    if modo == "sensores":
        # pega a ultima leitura com alerta do CSV
        if "df_anomalias" in st.session_state and st.session_state.df_anomalias is not None:
            df_a = st.session_state.df_anomalias
            alertas_df = df_a[df_a["tem_alerta"]]
            if alertas_df.empty:
                st.warning("Nenhuma anomalia encontrada nas leituras. Vá à aba Sensores para carregar os dados.")
                anomalia_txt = ""
                acoes_txt = []
            else:
                ultima = alertas_df.iloc[-1]
                anomalia_txt = ultima["anomalias"]
                acoes_txt = f3.acoes_para_anomalias(anomalia_txt)
                st.write(f"**Última anomalia:** {anomalia_txt}")
        else:
            st.warning("Dados de sensores não carregados ainda. Acesse a aba Sensores primeiro.")
            anomalia_txt = ""
            acoes_txt = []

    elif modo == "fase6":
        anomalia_txt = "Animal detectado na area monitorada pela camera da lavoura."
        acoes_txt = ["Acionar equipe de campo para verificar presenca de animais na area."]
        st.write(f"**Anomalia simulada:** {anomalia_txt}")

    else:
        anomalia_txt = st.text_area("Descreva a anomalia", value="Umidade critica detectada no talhao 3.")
        acoes_input = st.text_area(
            "Ações corretivas (uma por linha)",
            value="Acionar irrigacao imediata.\nVerificar bomba hidraulica."
        )
        acoes_txt = [a.strip() for a in acoes_input.splitlines() if a.strip()]

    if anomalia_txt and st.button("Enviar alerta", type="primary"):
        resultado = aws.enviar_alerta(origem_escolhida, anomalia_txt, acoes_txt)

        st.markdown("---")
        st.subheader("Mensagem gerada")
        st.code(resultado["mensagem"], language=None)

        if resultado["simulacao"]:
            st.warning(f"Status: {resultado['status']}")
        elif "Erro" in resultado["status"]:
            st.error(f"Status: {resultado['status']}")
        else:
            st.success(f"Alerta enviado! Message ID: {resultado.get('message_id', '')}")

with abas[6]:
    st.header("Ir Além")
    st.info("Aqui será documentada a proposta extra com AWS Rekognition.")
