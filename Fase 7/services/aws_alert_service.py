# Servico de alerta via AWS SNS (Fase 5).
# Sem credenciais configuradas, roda em modo simulacao e exibe a mensagem que seria enviada.

from datetime import datetime
from config import AWS_REGION, SNS_TOPIC_ARN


def _modo_simulacao() -> bool:
    return not SNS_TOPIC_ARN


def montar_mensagem(origem: str, anomalias: str, acoes: list[str]) -> str:
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    linhas_acoes = "\n".join(f"  - {a}" for a in acoes) if acoes else "  - Nenhuma acao imediata necessaria."
    return (
        f"[FarmTech Solutions] Alerta de Monitoramento\n"
        f"Data/Hora: {data_hora}\n"
        f"Origem: {origem}\n\n"
        f"Anomalias detectadas:\n  {anomalias}\n\n"
        f"Acoes corretivas sugeridas:\n{linhas_acoes}\n\n"
        f"Este alerta foi gerado automaticamente pelo sistema de monitoramento da fazenda."
    )


def enviar_alerta(origem: str, anomalias: str, acoes: list[str]) -> dict:
    mensagem = montar_mensagem(origem, anomalias, acoes)

    if _modo_simulacao():
        return {
            "simulacao": True,
            "mensagem": mensagem,
            "status": "Simulado (SNS_TOPIC_ARN nao configurado)",
        }

    try:
        import boto3
        cliente = boto3.client("sns", region_name=AWS_REGION)
        resposta = cliente.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=mensagem,
            Subject="FarmTech Solutions - Alerta de Monitoramento",
        )
        return {
            "simulacao": False,
            "mensagem": mensagem,
            "status": "Enviado",
            "message_id": resposta.get("MessageId", ""),
        }
    except Exception as e:
        return {
            "simulacao": False,
            "mensagem": mensagem,
            "status": f"Erro ao enviar: {e}",
        }
