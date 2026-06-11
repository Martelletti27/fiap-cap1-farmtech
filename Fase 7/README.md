# Fase 7 – Consolidação do Sistema FarmTech Solutions

Dashboard integrada que reúne em um único projeto Python todos os serviços desenvolvidos nas Fases 1 a 6, com alertas automáticos via AWS SNS.

## Vídeo demonstrativo

<!-- Após gravar, substitua o link abaixo -->
> Link do YouTube (não listado): _a preencher_

## Como executar o código

Na raiz do repositório:

```bash
cd "Fase 7"
pip install -r requirements.txt
python run.py
```

O navegador abre automaticamente com a dashboard na porta padrão do Streamlit (8501).

## Pré-requisitos

- Python 3.10 ou superior
- Dependências listadas em `requirements.txt` (instaladas pelo comando acima)
- Para os alertas AWS SNS: conta AWS com tópico SNS criado (ver seção abaixo)
- Para inferência com o modelo treinado da Fase 6: arquivo `best.pt` copiado para esta pasta

Sem as configurações opcionais o sistema funciona normalmente — os alertas entram em modo simulação e o YOLO usa o modelo pré-treinado `yolov8n`.

## Estrutura

```
Fase 7/
├── app.py                  # dashboard Streamlit com todas as abas
├── run.py                  # atalho para python run.py
├── config.py               # caminhos, culturas, limites de alerta e config AWS
├── .env.example            # modelo de variáveis de ambiente (não commitar o .env)
├── requirements.txt
├── README.md
└── services/
    ├── fase1_service.py    # cálculo de área e volume de insumos (Fase 1)
    ├── fase3_service.py    # leitura de sensores, anomalias e Open-Meteo (Fases 2 e 3)
    ├── fase6_service.py    # inferência YOLO nas imagens da lavoura (Fase 6)
    └── aws_alert_service.py# disparo de alertas via AWS SNS (Fase 5)
```

## Funcionalidades por aba

### Visão Geral
Métricas rápidas dos dados de sensor carregados do CSV da Fase 3 e tabela com o status de cada fase integrada.

### Fase 1 – Manejo e Insumos
Formulário para calcular a área do talhão (retangular ou circular) e o volume total de insumo para um manejo. Os produtos sugeridos por cultura e tipo de manejo seguem a mesma base da Fase 1.

### Fase 2/3 – Sensores e IoT
- Gráficos de série temporal de umidade do solo e pH com linhas de referência (valores críticos / faixa ideal)
- Tabela de anomalias detectadas (umidade crítica, pH fora da faixa, N/P/K baixos)
- Previsão de precipitação para as próximas 12h via API Open-Meteo (mesma integração da Fase 2) com indicação de bloqueio de irrigação

### Fase 4 – Machine Learning
Referência à dashboard da Fase 4 (`Fase 4/dashboard.py`) com acesso direto aos gráficos de regressão e recomendações de irrigação por município.

### Fase 6 – Visão Computacional
Seletor de imagem na pasta de teste da Fase 6, botão para rodar a detecção YOLO, exibição da imagem anotada e contagem por classe (maquinários / animais) com a ação corretiva sugerida.

### AWS Alertas
Envio de alerta para o tópico SNS configurado com a anomalia detectada e as ações corretivas. Sem credencial configurada, o sistema exibe a mensagem que seria enviada (modo simulação).

---

## Configuração do serviço de alertas na AWS (SNS)

O serviço de mensageria usa o **Amazon SNS** para enviar e-mail ou SMS aos funcionários da fazenda quando uma anomalia é detectada pelos sensores ou pela visão computacional.

### Passo 1 – Criar o tópico SNS

Acesse o console da AWS → **Amazon SNS** → **Topics** → **Create topic**.

- Type: **Standard**
- Name: `farmtech-alertas`
- Clique em **Create topic**

> Salve o **ARN** exibido após a criação (formato `arn:aws:sns:us-east-1:XXXXXXXXXXXX:farmtech-alertas`).

<!-- Insira aqui o print da tela de criação do tópico -->
![Criação do tópico SNS](assets/prints_aws/sns_01_create_topic.png)

### Passo 2 – Criar a assinatura (e-mail ou SMS)

Na página do tópico criado, clique em **Create subscription**.

- Protocol: **Email** (ou **SMS**)
- Endpoint: endereço de e-mail ou número de celular (formato `+5511999999999`)
- Clique em **Create subscription**

Confirme o e-mail recebido clicando no link de confirmação da AWS.

<!-- Insira aqui o print da tela de assinatura confirmada -->
![Assinatura confirmada](assets/prints_aws/sns_02_subscription.png)

### Passo 3 – Criar o usuário IAM com permissão de publicação

Acesse **IAM** → **Users** → **Create user**.

- Username: `farmtech-sns-publisher`
- Permissions: **Attach policies directly** → busque `AmazonSNSFullAccess` (ou crie uma policy personalizada com apenas `sns:Publish`)
- Clique em **Create user**

Na página do usuário criado, acesse **Security credentials** → **Create access key** → escolha **Application running outside AWS** → salve o `Access key ID` e o `Secret access key`.

<!-- Insira aqui o print das credenciais geradas -->
![Credenciais IAM](assets/prints_aws/sns_03_iam_keys.png)

### Passo 4 – Configurar as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e preencha:

```env
AWS_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:XXXXXXXXXXXX:farmtech-alertas
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

> O arquivo `.env` já está no `.gitignore` — as credenciais não vão para o repositório.

### Passo 5 – Testar o envio

Com o servidor rodando, acesse a aba **AWS Alertas** na dashboard e clique em **Enviar alerta**. Se a configuração estiver correta, o e-mail ou SMS chegará em alguns segundos.

<!-- Insira aqui o print do alerta recebido no e-mail -->
![E-mail de alerta recebido](assets/prints_aws/sns_04_email_received.png)

---

## Exemplos de alertas gerados

| Origem | Anomalia | Ação sugerida |
|--------|----------|---------------|
| Sensor (Fase 3) | Umidade crítica (< 20%) | Acionar irrigação imediata no talhão |
| Sensor (Fase 3) | pH fora da faixa (< 5.5 ou > 6.5) | Aplicar correção de acidez (calcário) ou acidificante |
| Sensor (Fase 3) | Nitrogênio baixo | Programar adubação nitrogenada de cobertura |
| Sensor (Fase 3) | Fósforo baixo | Aplicar adubação fosfatada conforme análise de solo |
| Sensor (Fase 3) | Potássio baixo | Programar adubação potássica de manutenção |
| Visão computacional (Fase 6) | Animal detectado na área | Verificar presença e acionar equipe de campo |

---

## Dependências principais

| Pacote | Uso |
|--------|-----|
| streamlit | Interface web da dashboard |
| plotly | Gráficos interativos |
| pandas | Leitura e manipulação do CSV de sensores |
| ultralytics | Inferência YOLO (Fase 6) |
| boto3 | Integração com AWS SNS |
| requests | Chamadas à API Open-Meteo (Fase 2) |
