# Organizador de arquivos

Programa em Python que organiza os arquivos soltos de uma pasta em subpastas por tipo:
**Videos**, **Fotos**, **PDFs**, **Instaladores** e **Games**.

Nunca apaga nem sobrescreve arquivos: se já existir um arquivo com o mesmo nome no destino,
o novo ganha um número, como `foto (1).png`. Tudo que é movido fica registrado e pode ser desfeito.

## Recursos

- Separa por extensão (vídeos, fotos, PDFs e instaladores), sem diferenciar maiúsculas
- Instaladores com palavras de jogo no nome (steam, epic, game...) vão para **Games**
- **Modo simulação** (padrão): mostra o que seria feito, sem mover nada
- **Log** de cada execução e programa para **desfazer** a última organização
- Se um arquivo der erro (sem permissão ou em uso), avisa e continua com os outros
- **Modo sem perguntas**, para rodar sozinho (agendado)
- **Proteção contra arquivos em andamento:** ignora arquivos modificados há pouco tempo e usa uma
  **quarentena** de duas rodadas, movendo só o que ficou igual entre elas

## Requisitos

- Python 3
- Linux ou WSL (Ubuntu no Windows)

## Como usar

Sempre dentro da pasta do projeto.

### Modo com perguntas

```bash
python3 organizador.py
```

1. Digite a pasta a organizar, ou aperte Enter para usar a `pasta_teste`.
2. Na pergunta do modo simulação, aperte Enter para só ver o que aconteceria,
   ou digite `n` para mover de verdade.

Esse modo organiza todas as categorias, incluindo Instaladores e Games.

### Modo sem perguntas

```bash
python3 organizador.py --pasta CAMINHO
python3 organizador.py --pasta CAMINHO --executar --aguardar 300 --quarentena 900
```

| Opção | O que faz |
|---|---|
| `--pasta CAMINHO` | Ativa o modo sem perguntas e define a pasta |
| `--executar` | Move de verdade. Sem ela, apenas simula |
| `--aguardar N` | Ignora arquivos modificados nos últimos N segundos |
| `--quarentena N` | Só move um arquivo que já estava igual (tamanho e data) numa rodada anterior, há pelo menos N segundos |

Nesse modo, Instaladores e Games ficam de fora (veja "Como personalizar").
Cada execução grava uma linha em `execucoes.txt`.

### Desfazer

```bash
python3 desfazer.py
```

Devolve os arquivos da última organização real ao lugar de origem.

## Como a quarentena funciona

Na primeira vez que o programa vê um arquivo, só anota o tamanho e a data em `vistos.json`.
Numa rodada seguinte, se nada mudou e já passou o tempo configurado, o arquivo é movido.
Isso evita mexer em arquivos que ainda estão sendo baixados ou copiados.
A simulação lê esse registro, mas não grava nele.

## Rodar sozinho no Windows (WSL)

O Agendador de Tarefas do Windows chama o programa de tempos em tempos pelo `wsl.exe`.
No PowerShell, troque `SEU_USUARIO_LINUX` e `SEU_USUARIO_WINDOWS` pelos seus nomes.

1. Crie um script que roda o programa sem abrir janela. Comece **sem** `--executar`:

```powershell
Set-Content -Path "$env:USERPROFILE\organizador-silencioso.vbs" -Value 'Set shell = CreateObject("WScript.Shell")', 'shell.Run "wsl.exe --cd /home/SEU_USUARIO_LINUX/organizador-de-arquivos -- python3 organizador.py --pasta /mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads --aguardar 300 --quarentena 900", 0, False'
```

2. Crie a tarefa, a cada 30 minutos:

```powershell
schtasks /Create /SC MINUTE /MO 30 /TN "OrganizadorDeArquivos" /TR "wscript.exe $env:USERPROFILE\organizador-silencioso.vbs"
```

3. Confira no `execucoes.txt` que as linhas `[simulação]` aparecem de 30 em 30 minutos.
4. Para mover de verdade, refaça o passo 1 acrescentando `--executar`.

Para operar a tarefa:

```powershell
schtasks /Run /TN "OrganizadorDeArquivos"
schtasks /Change /TN "OrganizadorDeArquivos" /DISABLE
schtasks /Change /TN "OrganizadorDeArquivos" /ENABLE
schtasks /Delete /TN "OrganizadorDeArquivos" /F
```

Pause a tarefa antes de editar o código. Ela só roda com o computador ligado, acordado e com o usuário logado.

## Como personalizar

- **Nova categoria:** adicione uma linha em `CATEGORIAS` no `organizador.py`,
  por exemplo `"Livros": [".epub"],`.
- **Novo formato:** adicione a extensão na lista da categoria, por exemplo `".webp"` em Fotos.
- **Nova palavra de jogo:** adicione o texto, em minúsculas, em `PALAVRAS_JOGOS`.
- **Categorias que o modo sem perguntas não move:** edite `CATEGORIAS_SO_MANUAL`.
  Com a lista vazia, ele organiza tudo.

## Estrutura

```
organizador.py   programa principal
desfazer.py      desfaz a última organização
logs/            registro de tudo que foi movido (não vai para o GitHub)
execucoes.txt    resumo de cada execução sem perguntas (não vai para o GitHub)
vistos.json      estado da quarentena (não vai para o GitHub)
pasta_teste/     arquivos para testar (não vai para o GitHub)
```

## Limitações

- Só organiza arquivos soltos na pasta, sem entrar em subpastas.
- A quarentena reduz o risco de mover um arquivo em andamento, mas não o elimina.
- O modo sem perguntas não move instaladores nem jogos, porque eles costumam estar em uso.