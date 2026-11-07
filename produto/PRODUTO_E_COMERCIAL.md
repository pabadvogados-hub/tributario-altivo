# Produto e comercial da transação tributária

## O produto

O escritório negocia a dívida federal de empresas com a PGFN. A entrada é um **parecer pago**. O contrato
combina um **valor fixo parcelado** com uma **porcentagem sobre a economia real**.

**Para quem:** empresas com dívida ativa na PGFN ou débito vencido na Receita, de preferência acima de
R$ 100 mil. Os sinais de urgência são execução fiscal, certidão travada, risco de exclusão do Simples e
parcelamento prestes a cair. **A dívida não ajuizada é o melhor lead**, porque ainda há margem para negociar
antes da execução.

**O que se entrega:**

1. **Diagnóstico gratuito de 20 minutos (R1)**, com a consulta pública na tela.
2. **Parecer pago, em 24 a 48 horas**, com o passivo real, a CAPAG, as teses e três cenários de desconto.
3. **Execução**, que pode incluir:
   - a remessa dos débitos da Receita para a PGFN (requerimento ou mandado de segurança);
   - a revisão da CAPAG;
   - a adesão ao edital ou a transação individual;
   - a correção de entrada indevida (art. 14-A).
4. **Acompanhamento das parcelas**, vendido como plano anual separado.

**Estrutura de preço** (cada escritório define os valores):

| Item | Forma |
| --- | --- |
| Diagnóstico R1 | gratuito |
| Parecer | valor fixo, abatido da 1ª parcela se fechar |
| Honorário fixo | parcelado em 12x |
| Êxito | porcentagem sobre o desconto **efetivamente obtido** |
| Acompanhamento | mensalidade por 12 meses |

**Nunca prometer porcentagem de desconto ao lead.** "Até 70%" só aparece como teto legal, nunca como garantia.

## O fluxo

```
Lead -> robô/SDR -> R1 (diagnóstico) -> parecer pago -> R2 (proposta) -> contrato
     -> remessa à PGFN e/ou revisão da CAPAG (se o parecer indicar) -> adesão
     -> acompanhamento mensal -> êxito cobrado sobre o desconto efetivo
```

Nenhum lead some. Quem não avança vai para retorno com data ou para nutrição.

## Organograma (papéis, não pessoas)

| Frente | Papel | Faz | Não faz |
| --- | --- | --- | --- |
| Comercial | Robô SDR | Primeiro toque em menos de 5 min, triagem, move o card | Falar de valor ou desconto |
| Comercial | SDR | Cadência de 8 toques, qualificação, agenda e confirma a R1 | Fechar, dar parecer, prometer valor |
| Comercial | Closer | Conduz R1 e R2, vende o parecer, negocia e fecha | Prometer desconto sem parecer |
| Técnica | Advogado tributário | Parecer, estratégia, peças | — |
| Técnica | Analista fiscal | Coleta no e-CAC e no Regularize, remessa, controle mensal | Decidir estratégia |
| Técnica | Responsável técnico | Aprova o parecer antes da R2 | — |
| Marketing | Marketing | Listas do motor, criativos, campanhas | Contato direto com o lead |

No começo, uma pessoa acumula vários papéis. O que não muda é a ordem e quem aprova.

## Comercial

O tributário vende em duas reuniões. **Na R1, o diagnóstico gratuito vende o parecer. Na R2, o parecer vende o
contrato.** Quem decide é o sócio da empresa, muitas vezes junto com o contador.

**Etapas do funil no CRM:**

1. Novo lead
2. Em cadência (SDR)
3. R1 agendada
4. R1 realizada
5. Parecer vendido
6. Parecer em elaboração
7. R2 agendada
8. Proposta enviada
9. Contrato assinado (passa para o operacional)
10. Perdido / nutrição (o card nunca é apagado)

**Lead qualificado: 7 campos antes da R1**

- CNPJ
- valor aproximado da dívida
- regime: Simples, Presumido ou Real
- situação: CDA, execução fiscal, parcelamento, citação
- gatilho: CND, licitação, crédito, penhora
- quem decide: sócio, cônjuge ou contador
- reunião com data e hora confirmadas

Dívida alta não é motivo de descarte. O lead só é desqualificado se:

- a dívida for baixa e já estiver parcelada;
- a empresa já tiver advogado tributário;
- for só pessoa física sem CNPJ (nesse caso, avaliar).

**Canais**

- **Prospecção ativa:** a lista do `motor/`, com dívida não ajuizada, faixa de valor e telefone. A abertura cita
  a inscrição ou a execução, que são informação pública.
- **Campanha paga:** criativos de dor (execução, bloqueio, CND) levando ao WhatsApp do robô.
- **Parceiros:** contadores. A reunião a três com o contador do cliente responde à objeção "meu contador cuida".

**Metas iniciais (calibrar no primeiro mês)**

| Indicador | Meta |
| --- | --- |
| Tempo até o primeiro contato | até 5 min |
| Toques diferentes em 7 dias | pelo menos 3 |
| Comparecimento à R1 | pelo menos 70% |
| Registro no CRM, ligações inclusive | 100% |
| Parecer vendido sobre R1 realizada | medir a partir do mês 1 |
| Contrato sobre R2 realizada | medir a partir do mês 1 |

**O que o comercial não diz:** "vou te dar 70%", valor de honorário antes da R2, prazo garantido, e "tudo bem?"
sozinho como abertura.

## Implantação em 90 dias

1. **Dias 1 a 30, montar:**
   - o funil no CRM;
   - os modelos de contrato, procuração e parecer no timbrado do escritório;
   - a IA de `ia/` e os agentes de `.claude/`;
   - um caso-piloto do começo ao fim.
2. **Dias 31 a 60, vender:**
   - primeira lista do motor (dívida não ajuizada, R$ 100 mil a R$ 1 milhão, na sua UF);
   - robô SDR em horário comercial;
   - R1 e R2 com o closer;
   - medir a conversão de cada etapa.
3. **Dias 61 a 90, escalar:**
   - campanha paga;
   - parceria com contadores;
   - plano anual de acompanhamento;
   - meta mensal de contratos com os números reais.

**Indicadores do painel mensal**

- leads novos e tempo até o primeiro contato
- R1 agendadas e realizadas
- pareceres vendidos
- R2 realizadas e contratos assinados
- honorários contratados e ticket médio
- dívida negociada e desconto obtido
- clientes no farol amarelo, vermelho e preto (POP-OP-06)

## Decisões que o escritório toma antes de ir a campo

- [ ] Tabela de preço: parecer, fixo, êxito e acompanhamento
- [ ] Quem assina tecnicamente
- [ ] Quem é a SDR e quem é o analista fiscal
- [ ] Texto único sobre desconto para o marketing ("até 70%" só como teto legal)
- [ ] Validade da procuração no e-CAC: 1 ano ou 5 anos
- [ ] Competência do mandado de segurança de remessa (Brasília ou a sede do cliente)
- [ ] Contrato sem cláusula de penhora de remuneração e sem uso do nome do cliente sem consentimento específico
- [ ] Pedir sempre CAPAG D ou avaliar caso a caso (recomendação: caso a caso, com o `avaliador-capag`)
