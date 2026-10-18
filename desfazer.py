from pathlib import Path

pasta_logs = Path("logs")

if not pasta_logs.is_dir():
    print("Nenhum log encontrado.")
    exit()

logs = sorted(pasta_logs.glob("*.txt"))

if not logs:
    print("Nenhum log para desfazer.")
    exit()

ultimo = logs[-1]
print("Desfazendo:", ultimo.name)

linhas = ultimo.read_text(encoding="utf-8").splitlines()

revertidos = 0
problemas = 0

for linha in reversed(linhas):
    origem_texto, destino_texto = linha.split("\t")
    origem = Path(origem_texto)
    destino = Path(destino_texto)

    if not destino.exists():
        print("Não encontrado (já foi movido?):", destino.name)
        problemas += 1
    elif origem.exists():
        print("Já existe algo no lugar original:", origem.name)
        problemas += 1
    else:
        destino.rename(origem)
        print("Revertido:", origem.name)
        revertidos += 1

print(f"\nResumo: {revertidos} revertidos, {problemas} com problema.")

if problemas == 0:
    ultimo.rename(ultimo.with_suffix(".desfeito"))