# Configuracao central da Fase 7
# Reune caminhos das fases anteriores, parametros de cultura/manejo e limites de alerta.

import os

# ------------------------
# CAMINHOS

# pasta da Fase 7 e raiz do projeto (uma pasta acima)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.dirname(BASE_DIR)

# arquivos/pastas reaproveitados das outras fases
CSV_SENSORES = os.path.join(RAIZ_PROJETO, "Fase 3", "assets", "fase2_sensor_readings.csv")
IMAGENS_FASE6 = os.path.join(RAIZ_PROJETO, "Fase 6", "Parte 1", "images", "test")

# modelo YOLO treinado da Fase 6 (se existir best.pt nesta pasta usamos ele; senao cai no pre-treinado)
MODELO_YOLO = os.path.join(BASE_DIR, "best.pt")

# ------------------------
# CULTURAS E MANEJO (mesma base da Fase 1)

config_culturas = ["Milho", "Soja", "Cafe"]

classes_manejo = ["Herbicida", "Fungicida", "Inseticida", "Biologico"]

ativo_cultura_manejo = {
    "Milho": {
        "Herbicida":  ["glyphosate", "atrazine", "nicosulfuron"],
        "Fungicida":  ["azoxystrobin", "propiconazole"],
        "Inseticida": ["lambda-cyhalothrin", "chlorantraniliprole"],
        "Biologico":  ["Bacillus thuringiensis", "Beauveria bassiana", "Metarhizium anisopliae"],
    },
    "Soja": {
        "Herbicida":  ["glyphosate", "chlorimuron-ethyl", "diclosulam"],
        "Fungicida":  ["azoxystrobin", "tebuconazole"],
        "Inseticida": ["imidacloprid", "thiamethoxam"],
        "Biologico":  ["Bacillus thuringiensis", "Trichoderma harzianum"],
    },
    "Cafe": {
        "Herbicida":  ["glyphosate"],
        "Fungicida":  ["tebuconazole", "copper oxychloride"],
        "Inseticida": ["imidacloprid"],
        "Biologico":  ["Beauveria bassiana", "Metarhizium anisopliae", "Trichoderma harzianum"],
    },
}

# ------------------------
# LIMITES DE ALERTA
# Usados pela Fase 3 (sensores) e pelo servico de mensageria da AWS.

LIMITE_UMIDADE_MIN = 20.0   # abaixo disso, risco de estresse hidrico
PH_MIN = 5.5                # faixa ideal de pH do solo
PH_MAX = 6.5

# ------------------------
# AWS / SNS
# O ARN fica em variavel de ambiente para nao expor credencial no codigo.
# Sem ARN configurado, o servico de alerta roda em modo simulacao.

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
