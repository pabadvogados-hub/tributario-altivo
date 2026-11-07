# Ecossistema de transação tributária

Tudo o que o PAB Advogados montou para vender e executar transação tributária na PGFN, num lugar só: produto,
comercial, método, POPs, banco de teses, banco de leis, motor de prospecção, raio-x por CNPJ, IA tributarista
e o agente que avalia a CAPAG. Versão de 07/11/2026.

## O que tem aqui

| Pasta | O que é | Como usar |
| --- | --- | --- |
| [`produto/`](produto/PRODUTO_E_COMERCIAL.md) | Produto, estrutura de preço, organograma por papéis, funil, qualificação, metas e implantação em 90 dias | Ler primeiro |
| [`metodo/`](metodo/METODO.md) | Método em 6 etapas, regras da CAPAG, vetores contestáveis, documentos e prazos | Consulta do dia a dia |
| [`pops/`](pops/README.md) | 10 POPs, um arquivo cada: 4 comerciais (COM) e 6 operacionais (OP) | Adaptar nomes e cargos |
| [`teses/`](teses/00_INDICE.md) | 21 teses (remessa à DAU, CAPAG, parcelamento, prescrição, CDA, execução, sócios, Simples, transação) | `teses/TEMAS/00_BANCO_DE_TESES_POR_TEMA.md` |
| [`leis/`](leis/00_INDICE.md) | 19 normas em texto vigente, cortadas por artigo, com busca | `python leis/buscar_lei.py PORT6757 34-B` |
| [`motor/`](motor/README.md) | Prospecção: dados abertos da PGFN + BrasilAPI, nota de 0 a 100 por empresa | `python motor/motor_autonomo.py` |
| [`consulta/`](consulta/consultar_cnpj.py) | Raio-x de uma empresa (cadastro, sócios, todas as inscrições) em HTML para a R1 | `python consulta/consultar_cnpj.py <cnpj> --escritorio "Seu Escritório"` |
| [`capag/`](capag/avaliar_capag.py) | Avaliador da CAPAG: diz se vale pedir a revisão (arts. 21 a 34-B da Portaria 6.757) | `python capag/avaliar_capag.py capag/exemplo_caso.json` |
| [`ia/`](ia/system_prompt_tributarista.md) | Prompt do relatório de passivo fiscal (e-CAC, Regularize, CDAs, execução) | Colar como instrução no Claude e anexar os PDFs |
| [`.claude/`](.claude/agents) | Agentes `avaliador-capag` e `peca-tributaria` e a skill `triagem-tributaria`, para o Claude Code | Abrir a pasta no Claude Code |
| [`painel/`](painel/index.html) | Painel com o fluxo, o organograma, o comercial, os POPs, as teses e as leis do PAB | Abrir no navegador |

## Como as peças se encaixam

```
motor/ acha a empresa  ->  consulta/ faz o raio-x para a R1  ->  triagem-tributaria organiza a conversa
  ->  ia/ gera o relatório de passivo com os PDFs do cliente  ->  avaliador-capag decide se pede revisão
  ->  peca-tributaria redige (teses/ + leis/)  ->  pops/ dizem quem faz o quê até o acompanhamento
```

## O agente da CAPAG

`capag/avaliar_capag.py` confere o que é objetivo:

- o prazo de 30 dias (art. 29);
- a trava do novo pedido (art. 34-B);
- a comparação entre a CAPAG presumida, a capacidade estimada pelo fluxo de caixa e o passivo total (art. 21);
- os créditos que já são irrecuperáveis pelo art. 25, como os inscritos há mais de 15 anos sem garantia ou com execução arquivada pelo art. 40 da LEF há mais de 3 anos;
- os documentos do art. 30 que faltam;
- o DFC feito pelo método indireto.

O agente `avaliador-capag` (no Claude Code) lê os documentos do cliente e monta o `caso.json`. Depois roda o
script e completa o parecer com os vetores contestáveis, a via escolhida e o cronograma.

Ele **não calcula a faixa A/B/C/D**, porque a fórmula da PGFN não é pública. A faixa sai do Regularize.

## Para adaptar ao seu escritório

- `ia/system_prompt_tributarista.md`: troque `{{ESCRITORIO}}`, `{{ADVOGADOS_RESPONSAVEIS}}` e `{{CIDADE_UF}}`.
- `motor/motor_autonomo.py`: em `CONFIG`, ajuste `uf_preferida` para a sua UF e a faixa de valor.
- `pops/` e `painel/` mostram a estrutura do PAB, com os nomes de lá. Troque pelos seus.

## Regras que valem para tudo

- Edital, data de corte, teto e entrada são conferidos no Regularize **no dia de cada caso**. Nunca de memória.
- Faixas A e B não têm desconto, só entrada facilitada. O desconto está em C e D.
- Revisão da CAPAG só com ganho de faixa confirmado. Julgado o pedido, um novo só cabe com fato superveniente
  ou mudança substancial da CAPAG presumida (art. 34-B). A ideia de "CAPAG efetiva irreversível pelo art. 30"
  está errada.
- Transação rescindida veda nova transação por 2 anos (art. 18 da Portaria 6.757).
- Teses marcadas `conferir` precisam do inteiro teor antes de ir para a peça. Nenhum número de processo foi inventado.
- Nunca prometer porcentagem de desconto ao lead.

## O que não está aqui

- As aulas e os modelos originais da Mentoria CRT (Santos & Soares), que são curso pago de terceiros.
- Listas de leads e relatórios de empresas reais. O motor gera a sua lista na sua máquina.
- Preços. Cada escritório define os seus.

## Requisitos

Python 3.10 ou mais novo, só a biblioteca padrão. O banco de leis já vem pronto (`leis/banco_leis.db`).
O raio-x por CNPJ lê o trimestre inteiro da PGFN (cerca de 8 GB de CSV). Cada consulta leva de 20 a 25 minutos,
então rode antes da reunião.
Para os agentes: [Claude Code](https://claude.com/claude-code) aberto na pasta do repositório.
