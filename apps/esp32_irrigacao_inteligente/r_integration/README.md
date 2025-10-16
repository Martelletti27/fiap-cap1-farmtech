# 🌱 Integração em R (Fase 2)

Sistema de análise estatística para decisão inteligente de irrigação, aplicando métodos de **Data Science** sobre os dados coletados pelos sensores ESP32.

## 🎯 Objetivo

Aplicar técnicas estatísticas (médias móveis, regressão linear, análise de correlação) para decidir automaticamente quando ligar ou desligar a bomba de irrigação (relé azul), otimizando o uso de água na agricultura.

---

## 📊 Técnicas de Data Science Implementadas

### 1. **Análise de Umidade do Solo**
- Comparação com thresholds configuráveis
- Identificação de níveis críticos

### 2. **Médias Móveis (7 dias)**
- Suavização de dados para identificar tendências
- Redução de ruído nas leituras dos sensores

### 3. **Regressão Linear Simples**
- Correlação entre Temperatura e Umidade do Solo
- Equação: `Umidade = a + b × Temperatura`
- Coeficiente de determinação (R²)

### 4. **Análise de Precipitação**
- Soma de chuva nos últimos 3 dias
- Previsão meteorológica via API Open-Meteo

### 5. **Sistema de Decisão Multi-Critério**
- Avaliação de múltiplos fatores ambientais
- Níveis de confiança calculados
- Recomendações baseadas em dados

---

## 🗂️ Estrutura dos Arquivos

```
r_integration/
├── scripts.R       # Script R principal (análise completa)
└── README.md       # Este arquivo (explicações de uso)
```

---

## 🚀 Como Usar

### Pré-requisitos

1. **R instalado** (versão 4.0 ou superior)
   - Windows: https://cran.r-project.org/bin/windows/base/
   - Linux: `sudo apt-get install r-base`
   - macOS: `brew install r`

2. **Conexão com internet** (para instalar pacotes e acessar API meteorológica)

### Execução

#### Opção 1: Via RStudio (Recomendado)
```r
# 1. Abra o RStudio
# 2. Abra o arquivo scripts.R
# 3. Clique em "Source" ou pressione Ctrl+Shift+S
```

#### Opção 2: Via Terminal/Prompt
```bash
# Navegue até a pasta r_integration
cd apps/esp32_irrigacao_inteligente/r_integration

# Execute o script
Rscript scripts.R
```

#### Opção 3: Console R Interativo
```r
# No console R
setwd("caminho/para/r_integration")
source("scripts.R")
```

---

## 📈 Saída Esperada

O script executará 5 análises sequenciais:

### 1️⃣ **Análise de Umidade do Solo**
```
Umidade atual: 56.4%
✅ Dentro da faixa ideal (30-80%)
```

### 2️⃣ **Análise de Tendência (Média Móvel)**
```
Média móvel (7 dias): 48.3%
📊 Tendência estável
```

### 3️⃣ **Análise de Condições Meteorológicas**
```
Temperatura: 21.0°C ✅
Vento: 10.7 km/h ✅
```

### 4️⃣ **Análise de Precipitação**
```
Chuva (últimos 3 dias): 50.2 mm
✅ Chuva suficiente
```

### 5️⃣ **Previsão Meteorológica**
```
Chuva prevista (próximos 3 dias): 12.6 mm
🌧️ Chuva significativa prevista
```

### 🎯 **Decisão Final**
```
========================================================================
  RESULTADO DA ANÁLISE
========================================================================

🎯 DECISÃO FINAL:
   Comando: DO_NOT_IRRIGATE
   Confiança: 80%

📋 RAZÕES:
   1. Chuva recente suficiente
   2. Chuva prevista em breve

📡 TOKEN PARA ESP32:
   FARMTECH_CMD=DO_NOT_IRRIGATE;CONFIDENCE=80;SOIL_MOISTURE=56.4;TEMP=21.0;TIMESTAMP=20251015_230000

✅ Token salvo em: esp32_irrigation_command.txt
```

---

## ⚙️ Configuração

### Thresholds de Irrigação

Edite no arquivo `scripts.R` (linhas 40-47):

```r
THRESHOLDS <- list(
  soil_moisture_min = 30,    # Irrigar se < 30%
  soil_moisture_max = 80,    # Não irrigar se > 80%
  rain_threshold = 5,        # Não irrigar se chuva > 5mm
  temp_min = 15,             # Temperatura mínima (°C)
  temp_max = 35,             # Temperatura máxima (°C)
  wind_max = 20              # Vento máximo (km/h)
)
```

### Configuração da Fazenda

Ajuste conforme sua localização (linhas 50-55):

```r
FARM_CONFIG <- list(
  latitude = -23.55,      # Sua latitude
  longitude = -46.63,     # Sua longitude
  crop_type = "soja",     # Tipo de cultura
  soil_type = "argiloso"  # Tipo de solo
)
```

---

## 📡 Integração com ESP32

### Token Gerado

O script gera um token no formato:
```
FARMTECH_CMD=IRRIGATE;CONFIDENCE=85;SOIL_MOISTURE=28.5;TEMP=32.1;TIMESTAMP=20251015_230000
```

### Campos do Token

| Campo | Descrição | Valores |
|-------|-----------|---------|
| FARMTECH_CMD | Comando de decisão | IRRIGATE, DO_NOT_IRRIGATE, HOLD |
| CONFIDENCE | Confiança da decisão | 0-100% |
| SOIL_MOISTURE | Umidade atual do solo | % |
| TEMP | Temperatura atual | °C |
| TIMESTAMP | Data/hora da análise | YYYYMMDD_HHMMSS |

### Uso no ESP32

1. O token é salvo em `esp32_irrigation_command.txt`
2. O ESP32 lê o arquivo ou recebe via serial
3. ESP32 executa o comando:
   - `IRRIGATE` → Liga relé azul (bomba ON)
   - `DO_NOT_IRRIGATE` → Desliga relé (bomba OFF)
   - `HOLD` → Mantém estado atual

---

## 🔧 Pacotes R Utilizados

O script instala automaticamente os pacotes necessários:

- **jsonlite**: Leitura de dados JSON (API meteorológica)
- **dplyr**: Manipulação de dados

Instalação manual (se necessário):
```r
install.packages(c("jsonlite", "dplyr"))
```

---

## 📊 Decisões Possíveis

### ✅ IRRIGATE (Irrigar)
**Quando:** Umidade < 30% OU tendência de baixa umidade  
**Ação:** Ligar bomba de irrigação (relé azul)  
**Confiança:** 70-90%

### ❌ DO_NOT_IRRIGATE (Não Irrigar)
**Quando:** Umidade > 80% OU chuva recente OU previsão de chuva  
**Ação:** Não ligar bomba  
**Confiança:** 70-90%

### ⏸️ HOLD (Manter)
**Quando:** Umidade adequada mas condições ambientais inadequadas  
**Ação:** Manter estado atual  
**Confiança:** 50-70%

---

## 🌐 API Meteorológica

### Open-Meteo (Gratuita)
- **URL**: https://api.open-meteo.com/v1/forecast
- **Dados**: Temperatura média, precipitação
- **Previsão**: Até 7 dias à frente
- **Custo**: Gratuito (sem necessidade de API key)

---

## 📚 Conceitos de Data Science Aplicados

### 1. **Análise Exploratória de Dados (EDA)**
- Estatísticas descritivas (média, desvio padrão)
- Visualização de tendências temporais

### 2. **Feature Engineering**
- Cálculo de médias móveis
- Agregação de dados temporais (soma de 3 dias)

### 3. **Regressão Linear**
- Modelo: `Y = a + bX`
- Interpretação de coeficientes
- Avaliação com R²

### 4. **Sistema de Decisão**
- Regras baseadas em thresholds
- Ponderação de múltiplos critérios
- Níveis de confiança

### 5. **Integração de Fontes**
- Dados locais (sensores)
- Dados externos (API meteorológica)
- Fusão de informações

---

## 💡 Exemplos de Análise

### Cenário 1: Solo Seco
```
Umidade: 25% (< 30%)
Temperatura: 28°C
Chuva recente: 0 mm
Previsão: Sem chuva

DECISÃO: IRRIGATE (Confiança: 85%)
RAZÃO: Umidade muito baixa
```

### Cenário 2: Chuva Recente
```
Umidade: 55%
Temperatura: 22°C
Chuva recente: 18 mm
Previsão: Sem chuva

DECISÃO: DO_NOT_IRRIGATE (Confiança: 80%)
RAZÃO: Chuva recente suficiente
```

### Cenário 3: Vento Forte
```
Umidade: 32%
Temperatura: 25°C
Vento: 25 km/h
Chuva recente: 0 mm

DECISÃO: HOLD (Confiança: 60%)
RAZÃO: Vento forte - irrigação ineficiente
```

---

## ❓ Solução de Problemas

### Erro: "package not found"
**Solução:**
```r
install.packages(c("jsonlite", "dplyr"))
```

### Erro: "tentando usar o CRAN sem definir um mirror"
**Solução:** O script já configura automaticamente, mas você pode forçar:
```r
options(repos = c(CRAN = "https://cloud.r-project.org/"))
```

### API meteorológica não responde
**Solução:** 
- Verifique conexão com internet
- O script continua funcionando mesmo sem previsão
- API pode estar temporariamente indisponível

### Dados dos sensores
**Nota:** O script atualmente simula dados. Para usar dados reais:
1. Modifique a função `read_sensor_data()`
2. Leia de arquivo CSV ou banco de dados
3. Integre com ESP32 via serial ou arquivo

---

## 🎓 Aplicações no Mercado

Este projeto demonstra competências valorizadas em:

✅ **Data Science**: Análise estatística, regressão, médias móveis  
✅ **AgTech**: Agricultura de precisão, IoT agrícola  
✅ **Programação R**: Linguagem líder em estatística  
✅ **APIs**: Integração com serviços externos  
✅ **Automação**: Decisões automatizadas baseadas em dados  
✅ **Sustentabilidade**: Otimização de recursos hídricos  

---

## 🔮 Próximos Passos (Evolução)

1. **Integração Real**: Ler dados diretamente do ESP32
2. **Banco de Dados**: Armazenar histórico em SQLite
3. **Machine Learning**: Random Forest ou SVM para classificação
4. **Dashboard**: Visualização com Shiny
5. **Alertas**: Notificações quando decisões críticas são tomadas

---

## 📞 Suporte

### Recursos de Aprendizado
- [R for Data Science](https://r4ds.had.co.nz/) - Livro gratuito
- [CRAN Task View: Agriculture](https://cran.r-project.org/) - Pacotes para agricultura
- [Open-Meteo Docs](https://open-meteo.com/en/docs) - Documentação da API

### Documentação do Código
- Todos os comentários estão em português
- Cada função tem descrição clara
- Exemplos de uso incluídos

---

**🌱 FarmTech - Tecnologia a serviço da agricultura sustentável! 🌱**

*Fase 2: Transformando dados em decisões inteligentes com Data Science em R*
