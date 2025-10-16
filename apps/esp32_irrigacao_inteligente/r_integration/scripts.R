# scripts.R — FIAP CAP1 - FarmTech
# Integração em R (Fase 2)
# Análises estatísticas para decisão inteligente de irrigação
# ========================================================================

# Configura mirror do CRAN
options(repos = c(CRAN = "https://cloud.r-project.org/"))

cat("\n")
cat("========================================================================\n")
cat("  FARMTECH - ANÁLISE ESTATÍSTICA PARA IRRIGAÇÃO INTELIGENTE (Fase 2)\n")
cat("========================================================================\n")
cat("\n")

# -------------------------
# 1. INSTALAÇÃO DE PACOTES
# -------------------------

# Função para instalar pacotes se necessário
install_if_missing <- function(package) {
  if (!requireNamespace(package, quietly = TRUE)) {
    cat(sprintf("Instalando pacote: %s\n", package))
    install.packages(package, dependencies = TRUE, quiet = TRUE)
  }
  suppressPackageStartupMessages(library(package, character.only = TRUE))
}

# Instala pacotes necessários
cat("Verificando pacotes R necessários...\n")
required_packages <- c("jsonlite", "dplyr")
for (pkg in required_packages) {
  install_if_missing(pkg)
}
cat("✅ Pacotes carregados com sucesso!\n\n")

# -------------------------
# 2. CONFIGURAÇÃO
# -------------------------

# Thresholds para decisão de irrigação
THRESHOLDS <- list(
  soil_moisture_min = 30,    # Irrigar se umidade < 30%
  soil_moisture_max = 80,    # Não irrigar se > 80%
  rain_threshold = 5,        # Não irrigar se chuva > 5mm
  temp_min = 15,             # Temperatura mínima
  temp_max = 35,             # Temperatura máxima
  wind_max = 20              # Vento máximo (km/h)
)

# Configuração da fazenda (ajustar conforme localização)
FARM_CONFIG <- list(
  latitude = -23.55,      # São Paulo (exemplo)
  longitude = -46.63,
  crop_type = "soja",
  soil_type = "argiloso"
)

# -------------------------
# 3. FUNÇÕES DE ANÁLISE
# -------------------------

# Função para ler/simular dados dos sensores
read_sensor_data <- function() {
  cat("📊 Carregando dados dos sensores...\n")
  
  # Simula 30 dias de dados (em produção, viria do ESP32)
  set.seed(123)
  dates <- seq(from = Sys.Date() - 30, to = Sys.Date(), by = "day")
  
  data <- data.frame(
    date = dates,
    soil_moisture = pmax(20, pmin(85, rnorm(length(dates), 50, 15))),
    temperature = pmax(10, pmin(40, rnorm(length(dates), 25, 8))),
    humidity = pmax(20, pmin(90, rnorm(length(dates), 65, 15))),
    wind_speed = pmax(0, pmin(30, rnorm(length(dates), 12, 5))),
    rainfall = pmax(0, rgamma(length(dates), shape = 2, scale = 3))
  )
  
  cat(sprintf("✅ %d dias de dados carregados\n\n", nrow(data)))
  return(data)
}

# Função para calcular média móvel
calculate_moving_average <- function(data, variable, window = 7) {
  n <- length(data[[variable]])
  ma <- rep(NA, n)
  
  for (i in window:n) {
    ma[i] <- mean(data[[variable]][(i-window+1):i], na.rm = TRUE)
  }
  
  return(ma)
}

# Função para análise de regressão simples
regression_analysis <- function(data) {
  cat("📈 Análise de Regressão (Temperatura vs Umidade)...\n")
  
  # Regressão linear: umidade ~ temperatura
  model <- lm(soil_moisture ~ temperature, data = data)
  
  # Coeficientes
  intercept <- coef(model)[1]
  slope <- coef(model)[2]
  r_squared <- summary(model)$r.squared
  
  cat(sprintf("   Equação: Umidade = %.2f + %.2f × Temperatura\n", intercept, slope))
  cat(sprintf("   R²: %.3f\n", r_squared))
  
  if (abs(r_squared) > 0.3) {
    cat("   ✅ Correlação significativa encontrada!\n\n")
  } else {
    cat("   ⚠️  Correlação fraca\n\n")
  }
  
  return(model)
}

# Função para obter previsão meteorológica
get_weather_forecast <- function(lat, lon, days = 3) {
  cat("🌤️  Obtendo previsão meteorológica...\n")
  
  tryCatch({
    url <- sprintf(
      "https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&daily=temperature_2m_mean,precipitation_sum&timezone=auto&forecast_days=%d",
      lat, lon, days
    )
    
    response <- jsonlite::fromJSON(url)
    
    if (!is.null(response$daily)) {
      forecast <- data.frame(
        date = as.Date(response$daily$time),
        temp = response$daily$temperature_2m_mean,
        rain = response$daily$precipitation_sum
      )
      
      cat(sprintf("✅ Previsão para %d dias obtida\n\n", days))
      return(forecast)
    }
  }, error = function(e) {
    cat("⚠️  Erro ao obter previsão meteorológica\n\n")
    return(NULL)
  })
}

# Função principal de decisão de irrigação
analyze_irrigation_need <- function(sensor_data, forecast_data = NULL) {
  cat("🤖 Analisando necessidade de irrigação...\n\n")
  
  # Dados mais recentes
  latest <- tail(sensor_data, 1)
  
  # Inicializa resultado
  decision <- "HOLD"
  confidence <- 0.5
  reasons <- character()
  
  # -------------------------
  # ANÁLISE 1: Umidade do Solo
  # -------------------------
  cat("1️⃣  Análise de Umidade do Solo:\n")
  cat(sprintf("   Umidade atual: %.1f%%\n", latest$soil_moisture))
  
  if (latest$soil_moisture < THRESHOLDS$soil_moisture_min) {
    decision <- "IRRIGATE"
    confidence <- 0.8
    reasons <- c(reasons, "Umidade do solo muito baixa")
    cat("   ❌ Abaixo do mínimo recomendado (30%)\n")
    cat("   ✅ DECISÃO: Irrigar necessário!\n\n")
  } else if (latest$soil_moisture > THRESHOLDS$soil_moisture_max) {
    decision <- "DO_NOT_IRRIGATE"
    confidence <- 0.8
    reasons <- c(reasons, "Solo já saturado")
    cat("   ✅ Acima do máximo (80%)\n")
    cat("   ❌ DECISÃO: Não irrigar!\n\n")
  } else {
    cat("   ✅ Dentro da faixa ideal (30-80%)\n\n")
  }
  
  # -------------------------
  # ANÁLISE 2: Média Móvel (7 dias)
  # -------------------------
  cat("2️⃣  Análise de Tendência (Média Móvel 7 dias):\n")
  
  if (nrow(sensor_data) >= 7) {
    sensor_data$soil_moisture_ma7 <- calculate_moving_average(sensor_data, "soil_moisture", 7)
    latest_ma <- tail(sensor_data$soil_moisture_ma7, 1)
    
    if (!is.na(latest_ma)) {
      cat(sprintf("   Média móvel: %.1f%%\n", latest_ma))
      
      if (latest_ma < THRESHOLDS$soil_moisture_min) {
        decision <- "IRRIGATE"
        confidence <- max(confidence, 0.7)
        reasons <- c(reasons, "Tendência de umidade baixa")
        cat("   📉 Tendência de redução\n")
        cat("   ✅ Reforça necessidade de irrigação\n\n")
      } else {
        cat("   📊 Tendência estável\n\n")
      }
    }
  } else {
    cat("   ⚠️  Dados insuficientes para média móvel\n\n")
  }
  
  # -------------------------
  # ANÁLISE 3: Condições Meteorológicas
  # -------------------------
  cat("3️⃣  Análise de Condições Meteorológicas:\n")
  cat(sprintf("   Temperatura: %.1f°C\n", latest$temperature))
  cat(sprintf("   Vento: %.1f km/h\n", latest$wind_speed))
  
  # Verifica temperatura
  if (latest$temperature < THRESHOLDS$temp_min || latest$temperature > THRESHOLDS$temp_max) {
    if (decision == "IRRIGATE") {
      decision <- "HOLD"
    }
    confidence <- max(confidence, 0.6)
    reasons <- c(reasons, "Temperatura inadequada para irrigação")
    cat("   ❌ Temperatura fora da faixa ideal (15-35°C)\n")
  } else {
    cat("   ✅ Temperatura adequada\n")
  }
  
  # Verifica vento
  if (latest$wind_speed > THRESHOLDS$wind_max) {
    decision <- "DO_NOT_IRRIGATE"
    confidence <- max(confidence, 0.7)
    reasons <- c(reasons, "Vento forte - irrigação ineficiente")
    cat("   ❌ Vento acima do limite (20 km/h)\n")
  } else {
    cat("   ✅ Vento dentro do limite\n")
  }
  cat("\n")
  
  # -------------------------
  # ANÁLISE 4: Chuva Recente
  # -------------------------
  cat("4️⃣  Análise de Precipitação:\n")
  recent_rain <- sum(tail(sensor_data$rainfall, 3))
  cat(sprintf("   Chuva (últimos 3 dias): %.1f mm\n", recent_rain))
  
  if (recent_rain > THRESHOLDS$rain_threshold) {
    decision <- "DO_NOT_IRRIGATE"
    confidence <- max(confidence, 0.8)
    reasons <- c(reasons, "Chuva recente suficiente")
    cat("   ✅ Chuva suficiente\n")
    cat("   ❌ DECISÃO: Não irrigar!\n\n")
  } else {
    cat("   ⚠️  Pouca chuva recente\n\n")
  }
  
  # -------------------------
  # ANÁLISE 5: Previsão do Tempo
  # -------------------------
  if (!is.null(forecast_data)) {
    cat("5️⃣  Análise de Previsão Meteorológica:\n")
    rain_forecast <- sum(forecast_data$rain)
    cat(sprintf("   Chuva prevista (próximos %d dias): %.1f mm\n", nrow(forecast_data), rain_forecast))
    
    if (rain_forecast > THRESHOLDS$rain_threshold) {
      decision <- "DO_NOT_IRRIGATE"
      confidence <- max(confidence, 0.7)
      reasons <- c(reasons, "Chuva prevista em breve")
      cat("   🌧️  Chuva significativa prevista\n")
      cat("   ❌ DECISÃO: Aguardar chuva!\n\n")
    } else {
      cat("   ☀️  Pouca chuva prevista\n\n")
    }
  }
  
  return(list(
    decision = decision,
    confidence = confidence,
    reasons = reasons,
    sensor_data = latest
  ))
}

# -------------------------
# 4. EXECUÇÃO PRINCIPAL
# -------------------------

cat("========================================================================\n")
cat("  INICIANDO ANÁLISE ESTATÍSTICA\n")
cat("========================================================================\n\n")

# Carrega dados dos sensores
sensor_data <- read_sensor_data()

# Executa análise de regressão
regression_model <- regression_analysis(sensor_data)

# Obtém previsão meteorológica
weather_forecast <- get_weather_forecast(
  FARM_CONFIG$latitude,
  FARM_CONFIG$longitude,
  days = 3
)

# Executa análise de irrigação
result <- analyze_irrigation_need(sensor_data, weather_forecast)

# -------------------------
# 5. RESULTADOS FINAIS
# -------------------------

cat("========================================================================\n")
cat("  RESULTADO DA ANÁLISE\n")
cat("========================================================================\n\n")

# Decisão
cat("🎯 DECISÃO FINAL:\n")
cat(sprintf("   Comando: %s\n", result$decision))
cat(sprintf("   Confiança: %.0f%%\n\n", result$confidence * 100))

# Razões
if (length(result$reasons) > 0) {
  cat("📋 RAZÕES:\n")
  for (i in seq_along(result$reasons)) {
    cat(sprintf("   %d. %s\n", i, result$reasons[i]))
  }
  cat("\n")
}

# Dados atuais
cat("📊 DADOS ATUAIS:\n")
cat(sprintf("   Umidade do solo: %.1f%%\n", result$sensor_data$soil_moisture))
cat(sprintf("   Temperatura: %.1f°C\n", result$sensor_data$temperature))
cat(sprintf("   Umidade relativa: %.1f%%\n", result$sensor_data$humidity))
cat(sprintf("   Vento: %.1f km/h\n", result$sensor_data$wind_speed))
cat(sprintf("   Chuva (último dia): %.1f mm\n\n", result$sensor_data$rainfall))

# Estatísticas dos últimos 7 dias
recent_7d <- tail(sensor_data, 7)
cat("📈 ESTATÍSTICAS (Últimos 7 dias):\n")
cat(sprintf("   Umidade média: %.1f%% (DP: %.1f)\n",
            mean(recent_7d$soil_moisture), sd(recent_7d$soil_moisture)))
cat(sprintf("   Temperatura média: %.1f°C (DP: %.1f)\n",
            mean(recent_7d$temperature), sd(recent_7d$temperature)))
cat(sprintf("   Chuva acumulada: %.1f mm\n\n", sum(recent_7d$rainfall)))

# Token para ESP32
cat("📡 TOKEN PARA ESP32:\n")
token <- sprintf(
  "FARMTECH_CMD=%s;CONFIDENCE=%.0f;SOIL_MOISTURE=%.1f;TEMP=%.1f;TIMESTAMP=%s",
  result$decision,
  result$confidence * 100,
  result$sensor_data$soil_moisture,
  result$sensor_data$temperature,
  format(Sys.time(), "%Y%m%d_%H%M%S")
)
cat(sprintf("   %s\n\n", token))

# Salva token em arquivo
writeLines(token, "esp32_irrigation_command.txt")
cat("✅ Token salvo em: esp32_irrigation_command.txt\n\n")

# Recomendações
cat("💡 RECOMENDAÇÕES:\n")
if (result$decision == "IRRIGATE") {
  cat("   → Ligar bomba de irrigação (relé azul)\n")
  cat("   → Monitorar umidade durante irrigação\n")
  cat("   → Ajustar duração conforme necessário\n")
} else if (result$decision == "DO_NOT_IRRIGATE") {
  cat("   → Não ligar irrigação no momento\n")
  cat("   → Continuar monitoramento\n")
  cat("   → Reavaliar em 2-4 horas\n")
} else {
  cat("   → Manter status atual\n")
  cat("   → Monitorar tendências\n")
  cat("   → Reavaliar em 1-2 horas\n")
}
cat("\n")

cat("========================================================================\n")
cat("  ANÁLISE CONCLUÍDA COM SUCESSO!\n")
cat("========================================================================\n")
cat("\n")
cat("🌱 FarmTech - Agricultura Inteligente com Data Science! 🌱\n")
cat("\n")

