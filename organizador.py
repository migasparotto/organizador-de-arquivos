import argparse
from datetime import datetime
from pathlib import Path

# Categorias: nome da pasta -> extensões que vão para ela.
# Para criar uma categoria nova, basta adicionar uma linha aqui.
CATEGORIAS = {
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Fotos": [".png", ".jpg", ".jpeg"],
    "PDFs": [".pdf"],
    "Instaladores": [".exe", ".msi", ".iso"],
}

# Instaladores com alguma dessas palavras no nome vão para a pasta Games.
PALAVRAS_JOGOS = ["steam", "epic", "game", "jogo", "battle.net", "launcher"]


def caminho_livre(destino, item):
    """Devolve um caminho que ainda não existe no destino (foto (1).png, foto (2).png...)."""
    caminho = destino / item.name
    contador = 1
    while caminho.exists():
        caminho = destino / f"{item.stem} ({contador}){item.suffix}"
        contador += 1
    return caminho


def parece_jogo(nome_arquivo):
    """Diz se o nome do arquivo tem alguma palavra de PALAVRAS_JOGOS."""
    for palavra in PALAVRAS_JOGOS:
        if palavra in nome_arquivo:
            return True
    return False


def descobrir_categoria(item):
    """Devolve o nome da categoria do arquivo, ou None se ele não tiver uma."""
    extensao = item.suffix.lower()
    nome_arquivo = item.name.lower()

    for categoria, extensoes in CATEGORIAS.items():
        if extensao in extensoes:
            if categoria == "Instaladores" and parece_jogo(nome_arquivo):
                return "Games"
            return categoria
    return None


def registrar_movimento(caminho_log, origem, destino):
    """Anota no log uma linha com a origem e o destino de um arquivo movido."""
    with open(caminho_log, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{origem}\t{destino}\n")


def registrar_execucao(texto):
    """Anota no arquivo execucoes.txt uma linha com a data e o resumo de uma execução automática."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("execucoes.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{agora}  {texto}\n")


parser = argparse.ArgumentParser(description="Organiza os arquivos de uma pasta por tipo.")
parser.add_argument("--pasta", help="Pasta a organizar. Sem isso, o programa pergunta.")
parser.add_argument("--executar", action="store_true", help="Move de verdade. Sem isso, só simula.")
args = parser.parse_args()

automatico = args.pasta is not None

if automatico:
    pasta = Path(args.pasta).expanduser()
else:
    entrada = input("Qual pasta organizar? (Enter para pasta_teste): ")
    if entrada == "":
        pasta = Path("pasta_teste")
    else:
        pasta = Path(entrada).expanduser()

if not pasta.is_dir():
    print("Pasta não encontrada:", pasta)
    if automatico:
        registrar_execucao(f"ERRO: pasta não encontrada: {pasta}")
    exit()

if automatico:
    simulacao = not args.executar
else:
    resposta = input("Modo simulação, só mostra sem mover? (S/n): ")
    simulacao = resposta.lower() != "n"

agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
caminho_log = Path("logs") / f"{agora}.txt"

if not simulacao:
    caminho_log.parent.mkdir(exist_ok=True)

movidos = 0
ignorados = 0
erros = 0

for item in list(pasta.iterdir()):
    if item.is_file():
        categoria = descobrir_categoria(item)

        if categoria is None:
            ignorados += 1
        else:
            destino = pasta / categoria
            novo_caminho = caminho_livre(destino, item)

            if simulacao:
                print("[SIMULAÇÃO] Moveria:", item.name, "->", novo_caminho.relative_to(pasta))
                movidos += 1
            else:
                try:
                    origem_absoluta = item.resolve()
                    destino.mkdir(exist_ok=True)
                    item.rename(novo_caminho)
                    registrar_movimento(caminho_log, origem_absoluta, novo_caminho.resolve())
                    print("Movido:", item.name, "->", novo_caminho.relative_to(pasta))
                    movidos += 1
                except OSError as erro:
                    print("ERRO ao mover", item.name, "->", erro)
                    erros += 1

if simulacao:
    print(f"\nResumo (simulação): {movidos} seriam movidos, {ignorados} ignorados.")
else:
    print(f"\nResumo: {movidos} movidos, {ignorados} ignorados, {erros} com erro.")
    if movidos > 0:
        print("Log salvo em:", caminho_log)

if automatico:
    modo = "real"
    if simulacao:
        modo = "simulação"
    registrar_execucao(f"[{modo}] {pasta} | {movidos} movidos, {ignorados} ignorados, {erros} com erro")