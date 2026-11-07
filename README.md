# Transação Tributária — kit do PAB

Estrutura que o PAB Advogados montou para vender e executar transação tributária na PGFN: os POPs, o banco
de teses, o banco de leis, o motor que acha empresas devedoras e o painel que junta tudo.
Versão de 06/11/2026.

## O que tem aqui

| Pasta | O que é | Como usar |
| --- | --- | --- |
| [`painel/`](painel/index.html) | Painel com o fluxo, o organograma, o comercial, os POPs, as teses e as leis | Abrir `painel/index.html` no navegador |
| [`pops/`](pops/README.md) | 10 POPs, um arquivo cada: 4 comerciais (COM) e 6 operacionais (OP) | Ler e adaptar os nomes e cargos ao seu escritório |
| [`teses/`](teses/00_INDICE.md) | 21 teses (remessa à DAU, CAPAG, parcelamento, prescrição, CDA, execução, sócios, Simples, transação) | `teses/TEMAS/00_BANCO_DE_TESES_POR_TEMA.md`; `teses.json` para ferramentas |
| [`leis/`](leis/00_INDICE.md) | 19 normas em texto vigente, cortadas por artigo, com busca | `python leis/buscar_lei.py CTN 174` |
| [`motor/`](motor/README.md) | Motor de prospecção: dados abertos da PGFN + BrasilAPI, com nota por empresa | `python motor/motor_autonomo.py` |

## O fluxo em uma linha

Lead → robô/SDR → **R1** (diagnóstico grátis, 20 min) → **parecer pago** (24 a 48h) → **R2** (proposta) →
contrato → remessa à PGFN e/ou revisão da CAPAG quando o parecer indicar → **adesão** → acompanhamento mensal
das parcelas → êxito sobre o desconto efetivo.

## Regras que valem para tudo

- Edital (PGDAU), data de corte, teto e entrada são conferidos no Regularize **no dia de cada caso**. Nunca de memória.
- Faixas A e B da CAPAG não têm desconto, só entrada facilitada. O desconto está em C e D.
- Revisão da CAPAG só com ganho de faixa confirmado. Julgado o pedido, um novo pedido só cabe com fato
  superveniente ou mudança substancial da CAPAG presumida (art. 34-B da Portaria PGFN 6.757/2022, incluído
  pela Portaria 1.241/2023). A ideia de "CAPAG efetiva irreversível pelo art. 30", que circula por aí, está errada.
- Teses marcadas `conferir` precisam do inteiro teor antes de ir para peça. Nenhum número de processo foi inventado.
- Nunca prometer porcentagem de desconto ao lead.

## O que NÃO está aqui, e por quê

- **As aulas e os modelos originais da Mentoria CRT** (Santos & Soares): é curso pago de terceiros. As teses
  apontam o nome do modelo de origem, mas o arquivo não vem junto.
- **A lista de leads do PAB**: tem nome de sócios. O motor gera a sua própria lista na sua máquina.
- Preços: cada escritório define os seus; o painel mostra só a estrutura (parecer, fixo, êxito, acompanhamento).

## Requisitos

Python 3.10 ou mais novo, só a biblioteca padrão. O banco de leis já vem pronto (`leis/banco_leis.db`);
para atualizar, rode `python leis/montar_banco_leis.py`.
