# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# PROJETO FARMTECH SOLUTIONS

## 👥 Integrantes: 
- <a href="https://github.com/Emarinhos">Everton</a>
- <a href="https://github.com/Juliagutierres29">Julia</a>
- <a href="https://github.com/rm567718">Nayara</a> 
- <a href="https://github.com/Xaramandas">Felipe Lourenco</a> 
- <a href="https://github.com/Martelletti27">Matheus</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/sabrina-otoni-22525519b/">Sabrina Otoni</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Andre Godoy, PhD</a>

## 📜 Descrição:

O **FarmTech Solutions** é um projeto acadêmico do curso de **Inteligência Artificial (FIAP)** com foco em **Agricultura Digital**. O repositório reúne o trabalho do grupo em **seis fases** sequenciais, da modelagem e do manejo no campo (insumos, área, tratamentos) à automação com **IoT (ESP32)**, passagem de dados de sensores para **banco de dados (Oracle)**, modelos de **aprendizado de máquina** (previsão de umidade, análise de rendimento) e apoio em **nuvem** (custo e arquitetura). A **Fase 6** trata de **visão computacional** e **detecção de objetos** no contexto do campo: dataset no formato YOLO (classes *maquinário* e *animais*), com documentação, vídeo e material de apoio no [README da Fase 6](Fase%206/README.md) e na [Parte 1](Fase%206/Parte%201/README.md).

Em termos técnicos, o material integra **Python**, **R** e, conforme a fase, **SQL**, **Streamlit**, serviços de nuvem e, na Fase 6, **treinamento/validação** com fluxo típico YOLO (ex.: **Ultralytics**).

## 🗂 ESTRUTURA GERAL

```
fiap_cursotiao_pbl/
│
├── Fase 1/                          # Manejo e cálculo de insumos
│   ├── apps/
│   │   ├── python_app/              # CLI para cálculo de manejo
│   │   └── r_app/                   # Análise de tratamentos (R)
│   ├── docs/                        # Recursos (ex.: YouTube)
│   └── README.md
│
├── Fase 2/                          # Irrigação inteligente (IoT + API)
│   ├── apps/
│   │   ├── esp32_app/               # ESP32 / Wokwi
│   │   ├── python_integration/      # Open-Meteo
│   │   └── r_integration/           # Análise e decisão de irrigação
│   └── README.md
│
├── Fase 3/                          # Banco de dados (Oracle) e sensores
│   ├── scripts/                     # Consultas SQL
│   ├── assets/                      # CSV e prints do manual Oracle
│   └── README.md
│
├── Fase 4/                          # ML – previsão de umidade (Streamlit)
│   ├── dashboard.py
│   ├── phase1_regression.py
│   ├── weather_api.py
│   ├── recommendations.py
│   └── requirements.txt
│
├── Fase 5/                          # ML – rendimento de safra + cloud (AWS)
│   ├── Parte 1/                     # Notebook, dados + README
│   ├── Parte 2/                     # comparacao_aws.md + README
│   └── README.md                    # Visão geral e links às partes
│
├── Fase 6/                          # Visão computacional – detecção (YOLO)
│   ├── Parte 1/                     # Dataset: images, labels, dataset.yaml + README
│   ├── Parte 2/
│   └── README.md
│
├── Fase 7/                          # Consolidação: dashboard integrada + AWS SNS
│   ├── app.py                       # Dashboard Streamlit unificada (abas por fase)
│   ├── run.py                       # Atalho de execução
│   ├── config.py                    # Configurações e caminhos
│   ├── services/                    # Serviços de cada fase (1, 3, 6, AWS)
│   └── README.md
│
└── README.md                        # Este arquivo
```

## Fases do projeto

Cada fase tem **README próprio** com resumo, estrutura e a seção **Como executar o código** (ou equivalente, conforme a tecnologia). As **Fases 5 e 6** têm ainda **README em cada `Parte 1` e `Parte 2`**; o README da fase aponta para eles.

| Fase | Tema (resumo) | README |
|------|----------------|--------|
| **1** | Manejo agrícola: cálculo de insumos e áreas (Python CLI) e análise em R | [Fase 1/README.md](Fase%201/README.md) |
| **2** | IoT: ESP32 (Wokwi), integração Python (Open-Meteo) e R | [Fase 2/README.md](Fase%202/README.md) |
| **3** | Importação e consultas de sensores no Oracle (SQL Developer) | [Fase 3/README.md](Fase%203/README.md) |
| **4** | Machine Learning: previsão de umidade e dashboard Streamlit | [Fase 4/README.md](Fase%204/README.md) |
| **5** | Previsão de rendimento (notebook) e notas de cloud (AWS) | [Fase 5 (visão geral)](Fase%205/README.md) · [P1](Fase%205/Parte%201/README.md) · [P2](Fase%205/Parte%202/README.md) |
| **6** | Visão computacional: detecção de objetos (YOLO), dataset *maquinário* / *animais* | [Fase 6 (visão geral)](Fase%206/README.md) · [P1](Fase%206/Parte%201/README.md) · [P2](Fase%206/Parte%202/README.md) |
| **7** | Dashboard integrada (Fases 1–6) com alertas via AWS SNS | [Fase 7/README.md](Fase%207/README.md) |

___________________________________________________________________________
🧾 Licença

 <img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
