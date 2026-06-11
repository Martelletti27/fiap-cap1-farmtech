# Servico da Fase 1: calculo de area de plantio e volume de insumos.
# Mantem as mesmas formulas da Fase 1, agora retornando dados prontos para a dashboard.

pi = 3.141592653589793


# converte metros quadrados para hectares
def m2_to_ha(area_m2: float) -> float:
    return float(area_m2) / 10000


# valida se um valor numerico e positivo, senao avisa o campo
def validar_positivo(valor: float, nome: str) -> None:
    try:
        v = float(valor)
    except Exception as e:
        raise ValueError(f"{nome} invalido: {valor!r}") from e
    if v <= 0:
        raise ValueError(f"{nome} deve ser > 0. Recebido: {v}")


# ------------------------
# AREA DO TALHAO

# area de talhao retangular
def calc_area_retangulo(largura_m: float, comprimento_m: float) -> dict:
    validar_positivo(largura_m, "largura (m)")
    validar_positivo(comprimento_m, "comprimento (m)")
    area_m2 = float(largura_m) * float(comprimento_m)
    return {
        "geometria": "retangulo",
        "area_m2": area_m2,
        "area_ha": m2_to_ha(area_m2),
    }


# area de talhao circular (pivo central)
def calc_area_circulo(raio_pivo_m: float) -> dict:
    validar_positivo(raio_pivo_m, "raio pivo (m)")
    area_m2 = pi * (float(raio_pivo_m) ** 2)
    return {
        "geometria": "circulo",
        "area_m2": area_m2,
        "area_ha": m2_to_ha(area_m2),
    }


# ------------------------
# MANEJO / INSUMOS

# volume total do produto considerando dose por hectare e numero de aplicacoes
def total_produto(area_ha: float, dose_por_ha: float, aplicacoes: int) -> float:
    validar_positivo(area_ha, "area (ha)")
    validar_positivo(dose_por_ha, "dose/ha")
    if int(aplicacoes) <= 0:
        raise ValueError("Numero de aplicacoes deve ser maior que 0.")
    return float(area_ha) * float(dose_por_ha) * float(aplicacoes)


# monta o resumo do manejo combinando area do talhao e produto escolhido.
# Recebe os dados ja validados pela dashboard e devolve um dicionario unico.
def calcular_manejo(cultura: str, area: dict, manejo: str, ativo: str,
                    dose_ha: float, unidade: str, aplicacoes: int) -> dict:
    area_ha = area["area_ha"]
    total = total_produto(area_ha, dose_ha, aplicacoes)
    return {
        "cultura": cultura,
        "geometria": area["geometria"],
        "area_m2": area["area_m2"],
        "area_ha": area_ha,
        "manejo": manejo,
        "ativo": ativo,
        "dose_ha": float(dose_ha),
        "unidade": unidade,
        "aplicacoes": int(aplicacoes),
        "total_insumo": total,
    }
