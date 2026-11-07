# Banco de Leis Tributário — PAB

Montado em 06/11/2026 com as normas que sustentam as teses da Mentoria CRT (transação tributária na PGFN).
Texto **vigente**: o que está riscado no Planalto (revogado) sai do texto. Cada norma é cortada por artigo e
indexada para busca (SQLite FTS5, sem acento).

## Como usar

```
python IVA/BANCO_DE_LEIS/TRIBUTARIO/buscar_lei.py CTN 174                 # artigo exato
python IVA/BANCO_DE_LEIS/TRIBUTARIO/buscar_lei.py PORT6757 30
python IVA/BANCO_DE_LEIS/TRIBUTARIO/buscar_lei.py revisao capacidade pagamento   # busca livre
python IVA/BANCO_DE_LEIS/TRIBUTARIO/montar_banco_leis.py                  # baixa de novo (atualiza)
```

Regra: antes de citar um artigo numa peça, puxar o texto daqui (não de memória) e conferir a data em
`normas.json` (`baixado_em`). Editais da PGFN (PGDAU) **não** entram aqui: mudam a cada rodada e são
conferidos no Regularize no dia do caso.

## Normas (19)

| Sigla | Norma | Para que serve nas teses |
| --- | --- | --- |
| CTN | Lei 5.172/1966 | prescrição (174), decadência (150 §4º, 173), CDA (202/203), responsabilidade (134/135), fraude (185) |
| LEF | Lei 6.830/1980 | execução fiscal, prescrição intercorrente (40), garantia, embargos |
| L13988 | Lei 13.988/2020 | transação por adesão e individual, descontos, prazos, rescisão, impedimento |
| L14375 | Lei 14.375/2022 | alterou a 13.988: prejuízo fiscal, prazo de 120 meses |
| L10522 | Lei 10.522/2002 | parcelamento convencional, entrada do reparcelamento (14-A), NJP (19) |
| L11941 | Lei 11.941/2009 | origem do art. 14-A |
| L13496 | Lei 13.496/2017 | PERT: conta como parcelamento anterior |
| DL147 | Decreto-Lei 147/1967 | art. 22: dever de remessa dos débitos à PGFN (base do MS de remessa) |
| PORTMF447 | Portaria MF 447/2018 | art. 2º: 90 dias para a RFB encaminhar à PGFN |
| L9784 | Lei 9.784/1999 | arts. 48 a 50: dever de decidir em 30 dias |
| L12016 | Lei 12.016/2009 | mandado de segurança: cabimento, autoridade, liminar (7º, III) |
| CPC | Lei 13.105/2015 | tutela de urgência (294, 300), negócio jurídico processual (190), agravo (1.015) |
| LC123 | LC 123/2006 | exclusão do Simples, parcelamento do Simples, reingresso |
| PAF | Decreto 70.235/1972 | impugnação, prazos, contencioso administrativo |
| L8137 | Lei 8.137/1990 | risco penal: apropriação indébita tributária (2º, II) |
| L10684 | Lei 10.684/2003 | art. 9º: suspensão da pretensão punitiva com parcelamento |
| PORT6757 | Portaria PGFN 6.757/2022 | CAPAG presumida e efetiva (arts. 20 a 31), irreversibilidade (30), impedimento (64) |
| PORT448 | Portaria PGFN 448/2019 | art. 17: entrada do reparcelamento por inscrição; separação (7º) |
| PORT742 | Portaria PGFN 742/2018 | NJP: saída quando há impedimento de transação |

Fontes: [Planalto](https://www.planalto.gov.br/ccivil_03/) para leis, decretos e LC; espelho
[Normas Legais](https://www.normaslegais.com.br/legislacao/portaria-pgfn-6757-2022.htm) para as portarias
6.757 e 448; [Legisweb](https://www.legisweb.com.br/legislacao/?id=368654) para a MF 447/2018 e
[Legisweb](https://www.legisweb.com.br/legislacao/?id=373099) para a PGFN 742/2018. As portarias vêm de
espelhos: na dúvida sobre redação de artigo alterado, conferir no DOU.

Ligação com as teses: `IVA/BANCO_DE_TESES/TRIBUTARIO/` (cada tese aponta os artigos daqui).
