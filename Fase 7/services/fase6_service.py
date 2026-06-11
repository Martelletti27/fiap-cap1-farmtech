# Servico da Fase 6: inferencia YOLO nas imagens de teste da lavoura.
# Usa o best.pt treinado da Fase 6 se existir; senao, cai no yolov8n pre-treinado.
# Classes do dataset: 0=maquinarios, 1=animais

import os
from pathlib import Path
from config import IMAGENS_FASE6, MODELO_YOLO

# nomes das classes do dataset da Fase 6
CLASSES = {0: "maquinarios", 1: "animais"}

# extensoes de imagem aceitas
_EXTENSOES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def listar_imagens() -> list[str]:
    pasta = Path(IMAGENS_FASE6)
    if not pasta.exists():
        return []
    return sorted(
        str(p) for p in pasta.iterdir()
        if p.suffix.lower() in _EXTENSOES
    )


def _carregar_modelo():
    from ultralytics import YOLO
    if os.path.exists(MODELO_YOLO):
        return YOLO(MODELO_YOLO)
    # sem best.pt, usa o modelo base — detecta objetos genericos
    return YOLO("yolov8n.pt")


def rodar_deteccao(caminho_imagem: str, confianca: float = 0.25) -> dict:
    modelo = _carregar_modelo()
    resultados = modelo(caminho_imagem, conf=confianca, verbose=False)
    r = resultados[0]

    deteccoes = []
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        nome = CLASSES.get(cls_id, f"classe_{cls_id}")
        deteccoes.append({"classe": nome, "confianca": round(conf, 3)})

    contagem = {nome: 0 for nome in CLASSES.values()}
    for d in deteccoes:
        if d["classe"] in contagem:
            contagem[d["classe"]] += 1

    # imagem anotada em PIL para exibir no Streamlit
    imagem_anotada = r.plot()

    return {
        "deteccoes": deteccoes,
        "contagem": contagem,
        "total": len(deteccoes),
        "imagem_anotada": imagem_anotada,
        "usando_modelo_treinado": os.path.exists(MODELO_YOLO),
    }


def acao_para_deteccao(contagem: dict) -> str:
    if contagem.get("animais", 0) > 0:
        return "Animal detectado na area monitorada. Verificar presenca e acionar equipe de campo."
    if contagem.get("maquinarios", 0) > 0:
        return "Maquinario identificado na imagem. Confirmar operacao planejada no talhao."
    return "Nenhum objeto das classes monitoradas detectado nesta imagem."
