# Documentação do organizador de arquivos

**Versão 3 · atualizada em 19/10/2026**

Documento de referência do programa: o que ele faz, como usar, como funciona por dentro,
como agendar a execução automática e como resolver problemas.
Para um resumo rápido, veja o [README](../README.md).

## Índice

1. [Visão geral](#1-visão-geral)
2. [O que faz e o que não faz](#2-o-que-faz-e-o-que-não-faz)
3. [Como usar](#3-como-usar)
4. [Como funciona por dentro](#4-como-funciona-por-dentro)
5. [Arquivos e pastas](#5-arquivos-e-pastas)
6. [Referência do código](#6-referência-do-código)
7. [Agendamento no Windows](#7-agendamento-no-windows)
8. [Decisões de projeto](#8-decisões-de-projeto)
9. [Como personalizar](#9-como-personalizar)
10. [Solução de problemas](#10-solução-de-problemas)
11. [Limitações conhecidas](#11-limitações-conhecidas)
12. [Histórico de versões](#12-histórico-de-versões)
13. [Ideias futuras](#13-ideias-futuras)

---

## 1. Visão geral

Programa em Python que organiza os arquivos soltos de uma pasta em subpastas por tipo:
**Videos**, **Fotos**, **PDFs**, **Instaladores** e **Games**.

Tem dois modos: com perguntas (uso manual) e sem perguntas (`--pasta`), que é o usado
pelo agendamento automático no Windows.

- **Linguagem:** Python 3, rodando no Ubuntu (WSL).
- **Pasta do projeto:** `~/organizador-de-arquivos`.
- **Repositório:** `github.com/migasparotto/organizador-de-arquivos`.
- **Uso típico:** organizar a pasta Downloads do Windows a cada 30 minutos.
- **Princípio:** nunca apaga nem sobrescreve. Só move, registra tudo e permite desfazer.

## 2. O que faz e o que não faz

**Faz:**

- Move arquivos soltos da pasta escolhida para subpastas por extensão, sem diferenciar maiúsculas.
- Separa instaladores de jogos (palavras no nome) na pasta Games.
- Simula antes de mover, trata nomes repetidos, registra cada movimento e desfaz a última organização.
- No modo sem perguntas, evita arquivos recentes e só move o que ficou estável entre duas rodadas.

**Não faz:**

- Não entra em subpastas e não mexe em arquivos sem categoria (por exemplo `.epub`, `.zip`, `.txt`).
- Não apaga arquivos e não sobrescreve: um nome repetido vira `nome (1).ext`.
- No modo sem perguntas, não move instaladores nem jogos.
- Não roda com o notebook dormindo ou com o usuário deslogado.

## 3. Como usar

Sempre dentro da pasta do projeto (`cd ~/organizador-de-arquivos`), porque `logs`,
`execucoes.txt` e `vistos.json` ficam nela.

### Modo com perguntas

```bash
python3 organizador.py
```

Pergunta a pasta (Enter usa `pasta_teste`) e se é simulação (Enter mantém a simulação,
`n` move de verdade). Organiza todas as categorias, incluindo Instaladores e Games.

### Modo sem perguntas

```bash
python3 organizador.py --pasta CAMINHO
python3 organizador.py --pasta CAMINHO --executar --aguardar 300 --quarentena 900
```

Sem `--executar`, só simula. Instaladores e Games ficam de fora.

### Opções

| Opção | O que faz |
|---|---|
| `--pasta CAMINHO` | Ativa o modo sem perguntas e define a pasta |
| `--executar` | Move de verdade. Sem ela, o modo sem perguntas apenas simula |
| `--aguardar N` | Ignora arquivos modificados nos últimos N segundos. Padrão: 0 |
| `--quarentena N` | Só move um arquivo que já estava igual (tamanho e data) numa rodada anterior, há pelo menos N segundos. Padrão: 0, que desliga |
| `--help` | Mostra a ajuda |

### Ler o resumo

- **movidos** (ou "seriam movidos", na simulação): arquivos que passaram por todas as regras.
- **ignorados:** arquivos sem categoria.
- **só no manual:** instaladores e jogos deixados de fora no modo sem perguntas.
- **recentes:** modificados há menos tempo que o valor de `--aguardar`.
- **em quarentena:** ainda não ficaram estáveis por tempo suficiente.
- **com erro:** falharam ao mover (permissão, arquivo em uso).

### Desfazer

```bash
python3 desfazer.py
```

Devolve os arquivos da última organização real ao lugar de origem.

## 4. Como funciona por dentro

1. Lê as opções da linha de comando (`argparse`). Se houver `--pasta`, o modo é automático.
2. Define a pasta: pela opção ou perguntando. Se ela não existir, avisa e termina
   (no modo automático, anota o erro no `execucoes.txt`).
3. Define se é simulação: pela ausência de `--executar` (modo automático) ou perguntando.
4. Lista os arquivos soltos da pasta e, para cada um, decide nesta ordem:
   1. Sem categoria: conta como ignorado.
   2. No modo automático e categoria em `CATEGORIAS_SO_MANUAL`: conta como só no manual.
   3. Modificado há menos de `--aguardar` segundos: conta como recente.
   4. Com `--quarentena` e ainda não liberado: conta como em quarentena e anota em `vistos.json`.
   5. Caso contrário, move. Na simulação só mostra. No modo real, cria a subpasta, move com
      `rename`, anota no log e conta. Se der `OSError`, avisa, conta o erro e segue.
5. No modo real com quarentena, grava o `vistos.json`. Mostra o resumo e, no modo automático,
   anota uma linha no `execucoes.txt`.

**Nomes repetidos:** se já existe um arquivo igual no destino, o novo vira `nome (1).ext`,
depois `nome (2).ext`, e assim por diante.

**Quarentena:** na primeira vez que um arquivo candidato é visto, o programa anota tamanho,
data de modificação e o momento. Numa rodada seguinte, se tamanho e data forem iguais e já
tiver passado o tempo da opção, o arquivo é liberado. Se algo mudou, a contagem recomeça.
Arquivos movidos ou que sumiram saem do registro. A simulação lê o registro, mas não grava.

## 5. Arquivos e pastas

- `organizador.py`: programa principal.
- `desfazer.py`: desfaz a última organização real.
- `logs/`: um arquivo `AAAA-MM-DD_HH-MM-SS.txt` por execução real que moveu algo. Cada linha
  tem a origem e o destino (caminhos completos), separados por tabulação. Depois de desfeito,
  o arquivo vira `.desfeito`.
- `execucoes.txt`: uma linha por execução automática (inclusive simulações), com data, modo,
  pasta e os seis contadores.
- `vistos.json`: estado da quarentena. Para cada arquivo em espera guarda `tamanho`,
  `mtime` (data em nanossegundos) e `visto_em` (momento da primeira vez, em segundos).
- `pasta_teste/`: arquivos para testar.
- `.gitignore`: deixa fora do GitHub `logs/`, `pasta_teste/`, `__pycache__/`,
  `execucoes.txt` e `vistos.json`.
- Subpastas criadas dentro da pasta organizada: `Videos`, `Fotos`, `PDFs`, `Instaladores` e `Games`.
- Fora do projeto, no Windows: `organizador-silencioso.vbs` (na pasta do usuário) e a
  tarefa agendada `OrganizadorDeArquivos`.

## 6. Referência do código

### Constantes (topo do `organizador.py`)

- `CATEGORIAS`: dicionário com o nome da pasta e a lista de extensões.
- `PALAVRAS_JOGOS`: palavras que, no nome de um instalador, mandam o arquivo para Games.
- `CATEGORIAS_SO_MANUAL`: categorias que o modo automático não move.
  Lista vazia faz o modo automático organizar tudo.
- `ARQUIVO_VISTOS`: nome do arquivo do estado da quarentena.

### Funções

- `caminho_livre(destino, item)`: devolve um caminho que ainda não existe no destino,
  acrescentando (1), (2)...
- `parece_jogo(nome_arquivo)`: diz se o nome tem alguma palavra de `PALAVRAS_JOGOS`.
- `descobrir_categoria(item)`: devolve a categoria pela extensão (e Games para instalador
  de jogo) ou `None`.
- `modificado_recentemente(item, segundos)`: diz se o arquivo foi modificado há menos de
  N segundos. Se o arquivo sumiu, considera recente.
- `carregar_vistos()` e `salvar_vistos(vistos)`: leem e gravam o `vistos.json`.
  Arquivo ausente ou quebrado vira um dicionário vazio.
- `liberado_da_quarentena(item, vistos, novos_vistos, hora_atual, segundos)`: diz se o
  arquivo já pode ser movido. Se não, anota em `novos_vistos`.
- `registrar_movimento(caminho_log, origem, destino)`: acrescenta uma linha ao log da execução.
- `registrar_execucao(texto)`: acrescenta uma linha ao `execucoes.txt`.

### `desfazer.py`

Procura o `.txt` mais recente em `logs`, lê as linhas de trás para frente e move cada arquivo
de volta. Se o destino não existe mais, ou já existe algo no lugar original, avisa e conta
como problema. Se não houve problemas, renomeia o log para `.desfeito`.

## 7. Agendamento no Windows

O Agendador de Tarefas do Windows chama, a cada 30 minutos, um script VBS que roda o programa
pelo `wsl.exe`, sem abrir janela. O programa roda, grava uma linha no `execucoes.txt` e termina.

### Recriar do zero

Troque `SEU_USUARIO_LINUX` e `SEU_USUARIO_WINDOWS` pelos seus nomes de usuário.

1. No Ubuntu, ter o projeto em `~/organizador-de-arquivos` e o Python 3 instalado.
2. Descobrir o caminho do Downloads: `ls /mnt/c/Users` e depois
   `ls /mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads`.
3. Testar no Ubuntu, em simulação:

   ```bash
   cd ~/organizador-de-arquivos
   python3 organizador.py --pasta /mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads --aguardar 300 --quarentena 900
   ```

4. Testar no PowerShell, também em simulação:

   ```powershell
   wsl.exe --cd /home/SEU_USUARIO_LINUX/organizador-de-arquivos -- python3 organizador.py --pasta /mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads --aguardar 300 --quarentena 900
   ```

5. Criar o script que esconde a janela (ainda sem `--executar`):

   ```powershell
   Set-Content -Path "$env:USERPROFILE\organizador-silencioso.vbs" -Value 'Set shell = CreateObject("WScript.Shell")', 'shell.Run "wsl.exe --cd /home/SEU_USUARIO_LINUX/organizador-de-arquivos -- python3 organizador.py --pasta /mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads --aguardar 300 --quarentena 900", 0, False'
   ```

6. Testar o script: `wscript.exe "$env:USERPROFILE\organizador-silencioso.vbs"` e conferir
   uma linha nova com `[simulação]` no `execucoes.txt`.
7. Criar a tarefa:

   ```powershell
   schtasks /Create /SC MINUTE /MO 30 /TN "OrganizadorDeArquivos" /TR "wscript.exe $env:USERPROFILE\organizador-silencioso.vbs"
   ```

8. Liberar a execução na bateria:

   ```powershell
   Set-ScheduledTask -TaskName "OrganizadorDeArquivos" -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries)
   ```

9. Conferir que a tarefa dispara sozinha (linhas novas de 30 em 30 minutos) e, só então,
   refazer o passo 5 acrescentando `--executar`.
10. Testar o `desfazer.py` quando houver arquivos movidos.

### Operar a tarefa (PowerShell)

```powershell
schtasks /Run /TN "OrganizadorDeArquivos"
schtasks /Query /TN "OrganizadorDeArquivos" /V /FO LIST
schtasks /Change /TN "OrganizadorDeArquivos" /DISABLE
schtasks /Change /TN "OrganizadorDeArquivos" /ENABLE
schtasks /Delete /TN "OrganizadorDeArquivos" /F
```

No `/Query`, "Último resultado" `0` significa que rodou sem erro e `267011` significa que
nunca rodou.

### Acompanhar (terminal do Ubuntu, na pasta do projeto)

```bash
grep Downloads execucoes.txt | tail -n 5
```

**Antes de editar o `organizador.py`, pause a tarefa** com `/DISABLE`, para o agendador não
rodar uma versão quebrada. Religue depois com `/ENABLE`.

## 8. Decisões de projeto

- **Rodar por horário, e não vigiar a pasta:** o `/mnt/c` não avisa o Linux de arquivos criados
  pelo Windows, e o WSL não fica rodando sozinho.
- **Quarentena de duas rodadas:** a data de modificação pode enganar (cópias mantêm a data
  original, alguns downloads usam a data do servidor). A quarentena usa o relógio do próprio programa.
- **Instaladores e jogos só no manual (no modo automático):** instalador em uso, ISO montada e
  jogo portátil não aparecem como arquivo em andamento.
- **Simulação como padrão:** quem não passa `--executar` nunca move nada.
- **Log de tudo e desfazer:** mover é difícil de reverter sem registro.
- **Estabilidade:** o programa fica como está, só com reparos pontuais.

## 9. Como personalizar

- **Nova categoria:** adicione uma linha em `CATEGORIAS`, por exemplo `"Livros": [".epub"],`.
- **Novo formato:** adicione a extensão na lista da categoria, por exemplo `".webp"` em Fotos.
- **Nova palavra de jogo:** adicione em `PALAVRAS_JOGOS`, em minúsculas.
- **Categorias que o modo automático não move:** edite `CATEGORIAS_SO_MANUAL`.
- **Outra pasta ou outro ritmo:** edite o script VBS e recrie a tarefa com outro valor em `/MO`.
- Pause a tarefa agendada antes de editar o código.

## 10. Solução de problemas

- **`unrecognized arguments`:** o arquivo que roda é uma versão antiga. Confira com
  `grep -c quarentena organizador.py` e `python3 organizador.py --help`, e salve o arquivo.
- **Nada é movido na primeira rodada:** comportamento normal da quarentena. A seguinte,
  depois do tempo configurado, move.
- **Um arquivo nunca é movido:** veja se ele tem categoria, se é instalador ou jogo no modo
  automático, se muda de tamanho ou de data a cada rodada (reinicia a quarentena) e se aparece
  em `com erro`.
- **`ERRO ao mover ... Permission denied`:** o arquivo está em uso ou a pasta de destino não
  aceita escrita. O programa segue com os outros.
- **A tarefa não roda:** rode `schtasks /Query ... /V /FO LIST` e veja a hora da última execução
  e o último resultado. Confira bateria, repouso e se o usuário está logado.
- **`vistos.json` quebrado:** apague o arquivo. A quarentena recomeça do zero.
- **`desfazer.py` avisa "Não encontrado" ou "Já existe algo no lugar original":** o arquivo
  foi movido de novo ou já há outro no destino. O log continua `.txt` e a conta fica como
  problema. Resolva à mão olhando as linhas do log.

## 11. Limitações conhecidas

- Só organiza arquivos soltos na pasta, sem entrar em subpastas.
- A quarentena reduz o risco de mover um arquivo em andamento, mas não o elimina.
- Só roda com o notebook ligado, acordado e com o usuário logado. Em repouso a rodada é pulada.
- `logs`, `execucoes.txt` e `vistos.json` ficam na pasta em que o programa é executado.
  Por isso o agendamento usa `--cd` para entrar na pasta do projeto.
- Os caminhos (usuário, pasta do projeto) ficam escritos no script VBS e precisam ser
  ajustados se mudarem.
- O log separa origem e destino por tabulação. Um nome de arquivo com tabulação, muito raro,
  quebraria o desfazer daquela linha.

## 12. Histórico de versões

- **Versão 1 (etapas 1 a 8):** classificar por extensão, mover, nomes repetidos, escolher a
  pasta, dicionário de categorias, simulação, resumo, log e desfazer.
- **Versão 2 (etapas 9 e 10):** tratamento de erros, pasta Games, comentários e docstrings, README.
- **Versão 3 (etapas 11 a 13):** modo sem perguntas, ignorar arquivos recentes, quarentena,
  instaladores e jogos só no manual, agendamento no Windows.

## 13. Ideias futuras

- Novas categorias (Livros, Audios).
- Verificar a integridade do arquivo antes de mover.
- Resumo mais legível do `execucoes.txt`.
