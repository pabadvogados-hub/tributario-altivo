# -*- coding: utf-8 -*-
"""
Avaliador de CAPAG: diz se vale pedir a revisao da capacidade de pagamento, com base na Portaria PGFN
6.757/2022 (arts. 21 a 34-B). Faz so o que da para conferir objetivamente; o juizo final e do advogado.

Uso:
    python capag/avaliar_capag.py capag/exemplo_caso.json
    python capag/avaliar_capag.py caso.json --saida parecer_capag.md

O que ele confere:
  1. prazo do pedido (art. 29: 30 dias da ciencia da CAPAG no Regularize/e-CAC)
  2. trava do art. 34-B (pedido ja julgado: novo pedido so com fato superveniente ou mudanca substancial)
  3. comparacao: CAPAG presumida x capacidade estimada pelo contribuinte x passivo total (art. 21)
  4. creditos que ja sao irrecuperaveis (tipo D) pelo art. 25, sem precisar de revisao
  5. documentos do art. 30 que faltam (sem eles o pedido nao e conhecido, art. 31 par. 1)
  6. DFC pelo metodo indireto (costuma gerar exigencia)

O que ele NAO faz: calcular a faixa A/B/C/D. A formula da PGFN nao e publica e considera o passivo todo
(PGFN + Receita + FGTS). A faixa sai do Regularize.
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

DOCS_ART30 = {
    'laudo': 'laudo tecnico firmado por profissional habilitado (art. 30, I)',
    'balanco': 'Balanco Patrimonial dos 2 ultimos exercicios e do exercicio em curso (art. 30, I)',
    'dre': 'DRE dos 2 ultimos exercicios e do exercicio em curso (art. 30, I)',
    'dfc': 'Demonstracao do Fluxo de Caixa dos 2 ultimos exercicios e do exercicio em curso (art. 30, I)',
    'bens': 'relacao de bens e direitos com matricula/IPTU/ITR, CRLV/IPVA e uso operacional (art. 30, II)',
    'credores': 'relacao nominal completa dos credores, com natureza, valor e vencimentos (art. 30, III)',
    'extratos': 'extratos bancarios e de aplicacoes atualizados (art. 30, IV)',
    'operacoes_credito': 'descricao das operacoes de credito e garantias (art. 30, V)',
}
SITUACOES_D = ('BAIXADA', 'BAIXADO', 'INAPTA', 'INAPTO', 'SUSPENSA', 'SUSPENSO')


def d(s):
    if not s:
        return None
    for f in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            pass
    sys.exit('Data invalida: %s (use AAAA-MM-DD ou DD/MM/AAAA)' % s)


def anos(desde, hoje):
    return (hoje - desde).days / 365.25


def brl(v):
    return ('R$ ' + f'{v:,.2f}').replace(',', 'X').replace('.', ',').replace('X', '.')


def avaliar(c, hoje=None):
    hoje = hoje or date.today()
    out, travas, alertas, a_favor = [], [], [], []

    # 1. prazo
    ciencia = d(c.get('data_ciencia_capag'))
    if ciencia:
        restam = 30 - (hoje - ciencia).days
        if restam < 0:
            travas.append('Prazo do art. 29 vencido ha %d dias (30 dias da ciencia em %s). Conferir se houve nova '
                          'ciencia (nova proposta/edital) antes de desistir.' % (-restam, ciencia.strftime('%d/%m/%Y')))
        elif restam <= 7:
            alertas.append('Restam %d dias do prazo do art. 29. Protocolo exclusivamente pelo Regularize (art. 30).' % restam)
        else:
            out.append('Prazo do art. 29: restam %d dias.' % restam)
    else:
        alertas.append('Data de ciencia da CAPAG nao informada: o prazo do art. 29 (30 dias) nao foi conferido.')

    # 2. art. 34-B
    if c.get('pedido_anterior_julgado'):
        fato = (c.get('fato_superveniente') or '').strip()
        if fato:
            alertas.append('Ja houve pedido julgado. Novo pedido so com fato superveniente (art. 34-B, par. 1). '
                           'Fato alegado: "%s". O pedido precisa demonstrar como ele altera a capacidade.' % fato)
        elif c.get('mudanca_substancial_presumida'):
            alertas.append('Ja houve pedido julgado; a mudanca substancial da CAPAG presumida autoriza novo pedido '
                           '(art. 34-B, par. 2). Guardar o print da presumida anterior e da atual.')
        else:
            travas.append('Ja houve pedido julgado e nao ha fato superveniente nem mudanca substancial da presumida: '
                          'novo pedido nao cabe (art. 34-B).')

    # 3. numeros
    presumida = float(c.get('capag_presumida_valor') or 0)
    passivo = float(c.get('passivo_total') or 0)
    fluxos = [float(x) for x in (c.get('fluxo_caixa_livre_anual') or [])]
    estimada = c.get('capacidade_estimada_5anos')
    if estimada is None and fluxos:
        estimada = sum(fluxos) / len(fluxos) * 5
        out.append('Capacidade estimada = media do fluxo de caixa livre (%s) x 5 anos = %s.'
                   % (', '.join(brl(x) for x in fluxos), brl(estimada)))
    estimada = float(estimada) if estimada is not None else None

    if presumida and passivo:
        out.append('CAPAG presumida: %s, ou %.0f%% do passivo total de %s.' % (brl(presumida), presumida / passivo * 100, brl(passivo)))
    if estimada is not None and presumida:
        dif = (presumida - estimada) / presumida * 100
        if estimada >= presumida:
            travas.append('A capacidade estimada (%s) e IGUAL OU MAIOR que a presumida (%s). A revisao pode piorar '
                          'a classificacao: nao pedir.' % (brl(estimada), brl(presumida)))
        elif dif < 15:
            alertas.append('A estimada (%s) e so %.0f%% menor que a presumida. Ganho incerto: confirmar no Regularize, '
                           'com simulacao, se essa diferenca muda a faixa antes de pedir.' % (brl(estimada), dif))
        else:
            a_favor.append('A estimada (%s) e %.0f%% menor que a presumida (%s).' % (brl(estimada), dif, brl(presumida)))
    elif estimada is None:
        alertas.append('Sem capacidade estimada (laudo ou fluxo de caixa): nao da para saber se a revisao ajuda.')

    if estimada is not None and passivo and estimada >= passivo:
        travas.append('A capacidade estimada paga o passivo inteiro em 5 anos (art. 21). Nesse cenario a tendencia '
                      'e credito de alta recuperacao (sem desconto); a revisao nao ajuda.')

    faixa = (c.get('faixa_atual') or '').upper().strip()
    if faixa == 'D':
        travas.append('A faixa atual ja e D: nao ha faixa melhor para buscar com a revisao.')
    elif faixa in ('A', 'B'):
        a_favor.append('Faixa atual %s nao tem desconto, so entrada facilitada. O desconto esta em C e D.' % faixa)
    elif faixa == 'C':
        out.append('Faixa atual C: ja ha desconto. Revisao so se a estimada indicar D com folga.')

    # 4. art. 25
    sit = (c.get('situacao_cadastral') or '').upper()
    if c.get('recuperacao_judicial') or c.get('falencia'):
        a_favor.append('Recuperacao judicial/falencia: os creditos sao irrecuperaveis pelo art. 25, III, sem revisao. '
                       'Conferir se a situacao consta no CNPJ (par. unico).')
    if any(s in sit for s in SITUACOES_D):
        alertas.append('Situacao cadastral "%s": conferir se esta na lista do art. 25, IV.' % sit)
    tipo_d = []
    for cr in c.get('creditos') or []:
        motivo = None
        di = d(cr.get('data_inscricao'))
        if di and anos(di, hoje) > 15 and not cr.get('garantia_ou_suspensao'):
            motivo = 'inscrito ha %.0f anos, sem garantia nem suspensao (art. 25, I)' % anos(di, hoje)
        sj = d(cr.get('suspensa_judicial_desde'))
        if sj and anos(sj, hoje) > 10:
            motivo = 'suspenso por decisao judicial ha %.0f anos (art. 25, II)' % anos(sj, hoje)
        a40 = d(cr.get('execucao_arquivada_art40_desde'))
        if a40 and anos(a40, hoje) > 3:
            motivo = 'execucao arquivada pelo art. 40 da LEF ha %.0f anos (art. 25, VI)' % anos(a40, hoje)
        if motivo:
            tipo_d.append('%s: %s' % (cr.get('inscricao', '?'), motivo))
    if tipo_d:
        a_favor.append('Creditos que ja sao irrecuperaveis (tipo D) sem revisao: ' + '; '.join(tipo_d) +
                       '. Conferir se o Regularize ja os classifica assim; se nao, isso vai no pedido.')

    # 5. documentos
    docs = c.get('documentos') or {}
    faltam = [txt for k, txt in DOCS_ART30.items() if not docs.get(k)]
    if faltam:
        alertas.append('Faltam %d documentos do art. 30. Sem eles a PGFN da 10 dias para sanar e, se nao vier, '
                       'nao conhece o pedido (art. 31, par. 1):\n' % len(faltam) + '\n'.join('    - ' + f for f in faltam))

    # 6. DFC
    if (c.get('dfc_metodo') or '').lower().startswith('indir'):
        alertas.append('DFC pelo metodo INDIRETO: na pratica gera despacho de exigencia. Refazer pelo metodo direto.')

    if travas:
        veredito = 'NAO PEDIR A REVISAO AGORA'
    elif estimada is None or presumida == 0 or len(faltam) > 3:
        veredito = 'FALTA DADO PARA DECIDIR'
    elif a_favor:
        veredito = 'REVISAO RECOMENDADA, DEPOIS DE CONFIRMAR O GANHO DE FAIXA NO REGULARIZE'
    else:
        veredito = 'REVISAO POSSIVEL, GANHO NAO DEMONSTRADO'
    return veredito, travas, alertas, a_favor, out


def relatorio(c, hoje=None):
    veredito, travas, alertas, a_favor, out = avaliar(c, hoje)
    L = ['# Avaliacao da CAPAG: %s' % (c.get('empresa') or 'empresa'),
         '', 'CNPJ %s · avaliado em %s' % (c.get('cnpj') or '[CONFERIR]', (hoje or date.today()).strftime('%d/%m/%Y')),
         '', '## Veredito', '', '**%s**' % veredito]
    for tit, itens in (('Travas', travas), ('A favor da revisao', a_favor), ('Alertas', alertas), ('Numeros e prazos', out)):
        if itens:
            L += ['', '## ' + tit, ''] + ['- ' + i for i in itens]
    L += ['', '## Limites desta avaliacao', '',
          '- A faixa A/B/C/D nao foi calculada: a formula da PGFN nao e publica. Ela sai do Regularize.',
          '- Edital, desconto, entrada e prazo: conferir no Regularize no dia.',
          '- Base: Portaria PGFN 6.757/2022, arts. 21 a 34-B (texto em `leis/`, `python leis/buscar_lei.py PORT6757 30`).',
          '- Julgado o pedido, cabe recurso em 10 dias pelo Regularize (art. 34-A).',
          '', 'Minuta automatica para revisao do advogado responsavel.']
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('caso')
    ap.add_argument('--saida')
    a = ap.parse_args()
    c = json.loads(Path(a.caso).read_text(encoding='utf-8'))
    txt = relatorio(c)
    if a.saida:
        Path(a.saida).write_text(txt, encoding='utf-8')
        print('OK ->', a.saida)
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        print(txt)


if __name__ == '__main__':
    main()
