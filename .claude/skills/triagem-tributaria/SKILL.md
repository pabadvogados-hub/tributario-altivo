---
name: triagem-tributaria
description: Transforma a conversa ou a reuniao com uma empresa devedora em triagem util - debitos e sua origem, fase, execucao fiscal, parcelamentos, CAPAG, teses candidatas com a prova de cada uma, gatilhos de prazo e o que ainda falta perguntar.
---

# Triagem de caso tributario

Use quando chegar uma conversa de WhatsApp, a transcricao de uma reuniao ou um relato solto sobre uma empresa
com debitos fiscais. Se tiver o CNPJ, rode antes `python consulta/consultar_cnpj.py <cnpj>` e use o raio-x.

## Ordem
- **Quem**: empresa (regime, atividade, porte, situacao no CNPJ, socios) e quem decide (socio, conjuge, contador).
- **Debitos**: cada um separado. CDA ou inscricao, tributo, ente (PGFN, Receita, Estado, Municipio), periodo,
  valor, fase (lancamento, defesa administrativa, divida ativa, execucao fiscal, parcelado) e COMO NASCEU
  (declaracao do proprio contribuinte, auto de infracao, lancamento de oficio).
- **Execucao fiscal**: numero, vara, citacao, penhora ou bloqueio, garantia.
- **Parcelamentos e transacoes**: modalidade, situacao, atraso, rescisao (rescisao de transacao gera 2 anos de
  impedimento).
- **CAPAG**: faixa e valor que aparecem no Regularize, e quando apareceram (prazo de 30 dias, art. 29).
  Se houver chance de revisao, chamar o agente `avaliador-capag`.
- **Teses candidatas**: so o que os FATOS sustentam, cada uma com a prova que existe hoje e a forca
  (FORTE / MEDIA / FRACA), puxadas de `teses/`. Tese sem fato e sem prova vira pergunta, nao vira pedido.
- **Gatilhos**: prazo de embargos ou recurso correndo, bloqueio, certidao travando negocio, parcelamento a
  rescindir, edital com prazo de adesao, prescricao ou decadencia perto de consumar.
- **Gaps**: o que falta perguntar, em perguntas curtas e simples.

## Regras
- Nunca inventar tributo, valor, data, numero de CDA ou de processo. Faltou: `[CONFERIR: o que falta]`.
- Nao concluir prescricao ou decadencia sem as datas-chave (fato gerador, constituicao do credito, citacao).
- Nao prometer desconto nem estimar economia.
- A triagem organiza, nao recusa: quem decide se o escritorio pega o caso e o advogado.
