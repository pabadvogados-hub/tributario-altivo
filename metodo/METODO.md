# Método da transação tributária em 6 etapas

A ordem é fixa. Cada etapa responde a uma pergunta e alimenta a seguinte.

| # | Etapa | Pergunta | Onde |
| --- | --- | --- | --- |
| 1 | **Monitorar os editais** | Qual edital está aberto e até quando? O prazo de adesão comanda a urgência do caso inteiro. | Regularize, página de editais da PGFN |
| 2 | **Consulta pública** | Qual é a situação cadastral, o porte, o Simples, a dívida ativa e a execução fiscal? | `consulta/consultar_cnpj.py`, Lista de Devedores, tribunal |
| 3 | **Simular no Regularize** | O que a PGFN oferece de fato, e em qual faixa de CAPAG classificou a empresa? | Regularize, com a procuração do cliente |
| 4 | **Analisar a viabilidade** | **Por que** a transação é possível ou não? É aqui que o escritório agrega valor. | Parecer (POP-OP-02) |
| 5 | **Verificar o SPAR** | Se a etapa 4 não explica o impedimento, qual é a causa real? | e-CAC, SISPAR |
| 6 | **Definir a tese ou a medida** | A medida decorre do impedimento encontrado. Ela não é escolha livre. | `teses/`, agente `peca-tributaria` |

## Regras duras

- **Os editais mudam os percentuais.** Entrada, prazo, desconto, teto e data de adesão são conferidos no
  Regularize no dia de cada caso. Nunca de memória, nunca de material antigo.
- **As faixas A e B não têm desconto**, só entrada facilitada. O desconto e o prazo alongado estão em C e D.
  Por isso a revisão da CAPAG é o que destrava o desconto.
- **A faixa não se calcula.** A fórmula da PGFN não é pública e considera o passivo total do contribuinte
  (PGFN, Receita e FGTS). Ela sai do Regularize.
- **Revisão da CAPAG só com ganho de faixa confirmado.** Julgado o pedido, um novo pedido só cabe com fato
  superveniente ou com mudança substancial da CAPAG presumida (art. 34-B da Portaria PGFN 6.757/2022). Se a
  capacidade recalculada for maior que a presumida, a revisão piora o caso. Use o agente `avaliador-capag`.
- Rescisão de transação gera 2 anos de impedimento para nova transação (art. 18 da Portaria 6.757).

## Vetores contestáveis da CAPAG presumida

| Vetor | Por que contestar |
| --- | --- |
| Receita bruta | Não é capacidade de pagamento: ignora a margem. |
| DARF pago | Efeito perverso: pune quem paga em dia. |
| Notas fiscais de saída | São custo e duplicam o dado contábil. |
| Endividamento bancário e despesas operacionais | A PGFN não enxerga. Entram pelo art. 30, III e V. |
| Patrimônio | É da PJ ou do sócio? É bem usado na operação (art. 30, parágrafo único)? |

## Documentos da revisão (art. 30 da Portaria 6.757)

1. Laudo técnico de viabilidade econômico-financeira, com metodologia explícita, firmado por profissional habilitado.
2. Balanço, DRE e DFC dos 2 últimos exercícios e do exercício em curso. **DFC pelo método direto**: o indireto
   costuma gerar despacho de exigência.
3. Relação de bens e direitos, com matrícula, IPTU/ITR, CRLV/IPVA e o uso de cada bem na operação.
4. Relação nominal completa dos credores, com natureza, valor e vencimentos.
5. Extratos bancários e de aplicações atualizados (pedir por último, para chegarem atuais).
6. Descrição das operações de crédito e das garantias.

Sem os documentos, a PGFN dá 10 dias para sanar. Se não vierem, o pedido não é conhecido (art. 31, § 1º).

## Prazos da CAPAG

| Ato | Prazo | Base |
| --- | --- | --- |
| Pedir a revisão | 30 dias da ciência da CAPAG no Regularize ou no e-CAC | art. 29 |
| Sanar a falta de documento | 10 dias | art. 31, § 1º |
| Prestar informação adicional | 15 dias, prorrogáveis | art. 31, § 2º |
| Recorrer da decisão | 10 dias, só pelo Regularize | art. 34-A |
