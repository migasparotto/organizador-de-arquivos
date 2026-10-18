from datetime import datetime
from pathlib import Path

CATEGORIAS = {
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Fotos": [".png", ".jpg", ".jpeg"],
    "PDFs": [".pdf"],
    "Instaladores": [".exe", ".msi", ".iso"],
}


def caminho_livre(destino, item):
    caminho = destino / item.name
    contador = 1
    while caminho.exists():
        caminho = destino / f"{item.stem} ({contador}){item.suffix}"
        contador += 1
    return caminho


def descobrir_categoria(extensao):
    for nome, extensoes in CATEGORIAS.items():
        if extensao in extensoes:
            return nome
    return None


def registrar_movimento(caminho_log, origem, destino):
    with open(caminho_log, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{origem}\t{destino}\n")


entrada = input("Qual pasta organizar? (Enter para pasta_teste): ")

if entrada == "":
    pasta = Path("pasta_teste")
else:
    pasta = Path(entrada).expanduser()

if not pasta.is_dir():
    print("Pasta não encontrada:", pasta)
    exit()

resposta = input("Modo simulação, só mostra sem mover? (S/n): ")
simulacao = resposta.lower() != "n"

agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
caminho_log = Path("logs") / f"{agora}.txt"

if not simulacao:
    caminho_log.parent.mkdir(exist_ok=True)

movidos = 0
ignorados = 0

for item in list(pasta.iterdir()):
    if item.is_file():
        categoria = descobrir_categoria(item.suffix.lower())

        if categoria is None:
            ignorados += 1
        else:
            destino = pasta / categoria
            novo_caminho = caminho_livre(destino, item)

            if simulacao:
                print("[SIMULAÇÃO] Moveria:", item.name, "->", novo_caminho.relative_to(pasta))
            else:
                origem_absoluta = item.resolve()
                destino.mkdir(exist_ok=True)
                item.rename(novo_caminho)
                registrar_movimento(caminho_log, origem_absoluta, novo_caminho.resolve())
                print("Movido:", item.name, "->", novo_caminho.relative_to(pasta))

            movidos += 1

if simulacao:
    print(f"\nResumo (simulação): {movidos} seriam movidos, {ignorados} ignorados.")
else:
    print(f"\nResumo: {movidos} movidos, {ignorados} ignorados.")
    if movidos > 0:
        print("Log salvo em:", caminho_log)