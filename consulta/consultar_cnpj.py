# -*- coding: utf-8 -*-
"""
Raio-x tributario de UMA empresa: cadastro na Receita (BrasilAPI) + todas as inscricoes em divida ativa
da Uniao (dados abertos da PGFN), num relatorio HTML pronto para imprimir em PDF e levar para a R1.

Uso:
    python consulta/consultar_cnpj.py 12345678000199
    python consulta/consultar_cnpj.py 12345678000199 --escritorio "Seu Escritorio Advocacia"

Usa os zips que o motor ja baixou (motor/data/<trimestre>/). Se nao houver nenhum, baixa o trimestre mais
recente (cerca de 1,5 GB, uma vez so). Procura pela RAIZ do CNPJ (8 digitos), entao pega matriz e filiais.
Saida: consulta/saida/relatorio_<cnpj>.html
"""
import argparse
import csv
import html
import io
import json
import sys
import zipfile
from datetime import date
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_REPO / 'motor'))
import motor_autonomo as motor  # noqa: E402

SAIDA = Path(__file__).resolve().parent / 'saida'


def fmt(v):
    return ('R$ ' + f'{v:,.2f}').replace(',', 'X').replace('.', ',').replace('X', '.')


def masc(c):
    return f'{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}'


def pasta_trimestre():
    pastas = sorted(p for p in motor.DATA.glob('20*_T*') if any(p.glob('Dados_abertos_*.zip')))
    if pastas:
        return pastas[-1]
    nome, pasta_site = motor.ultimo_trimestre()
    print('Nenhum trimestre baixado. Baixando', pasta_site, '(uma vez so)...', flush=True)
    return motor.baixar_trimestre(nome, pasta_site)


def inscricoes(raiz, pasta):
    csv.field_size_limit(50_000_000)
    achados = []
    for z in sorted(pasta.glob('Dados_abertos_*.zip')):
        origem = 'PREVIDENCIARIO' if 'Previdenciario' in z.name else 'NAO PREVIDENCIARIO'
        with zipfile.ZipFile(z) as zf:
            for m in [x for x in zf.namelist() if x.lower().endswith('.csv')]:
                with zf.open(m) as raw:
                    for row in csv.DictReader(io.TextIOWrapper(raw, encoding='latin-1', newline=''), delimiter=';'):
                        dig = ''.join(c for c in (row.get('CPF_CNPJ') or '') if c.isdigit())
                        if dig.startswith(raiz):
                            a = {k: (v or '').strip() for k, v in row.items()}
                            a['_origem'] = origem
                            achados.append(a)
                print(f'  lido {z.name} / {m}: {len(achados)} inscricoes ate agora', flush=True)
    return achados


def valor(a):
    return motor.num((a.get('VALOR_CONSOLIDADO') or '0').replace(',', '.'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cnpj')
    ap.add_argument('--escritorio', default='')
    args = ap.parse_args()
    cnpj = ''.join(c for c in args.cnpj if c.isdigit())
    if len(cnpj) != 14:
        sys.exit('CNPJ precisa ter 14 digitos.')
    esc = html.escape(args.escritorio)
    e = lambda s: html.escape(str(s or ''))  # noqa: E731

    with motor.http('https://brasilapi.com.br/api/cnpj/v1/' + cnpj, timeout=40) as r:
        rf = json.load(r)

    pasta = pasta_trimestre()
    insc = inscricoes(cnpj[:8], pasta)
    total = sum(valor(a) for a in insc)
    ajuiz = [a for a in insc if (a.get('INDICADOR_AJUIZADO') or '').upper().startswith('S')]
    total_aj = sum(valor(a) for a in ajuiz)
    total_adm = total - total_aj
    pct_adm = (total_adm / total * 100) if total else 0
    prev = sum(valor(a) for a in insc if a['_origem'] == 'PREVIDENCIARIO')

    porrec = {}
    for a in insc:
        k = (a.get('RECEITA_PRINCIPAL') or a.get('TIPO_CREDITO') or 'Nao informado').strip()
        d = porrec.setdefault(k, {'qtd': 0, 'valor': 0.0})
        d['qtd'] += 1
        d['valor'] += valor(a)
    porrec = sorted(porrec.items(), key=lambda x: -x[1]['valor'])

    datas = sorted(a.get('DATA_INSCRICAO', '') for a in insc if a.get('DATA_INSCRICAO'))
    situacao = (rf.get('descricao_situacao_cadastral') or '').upper()
    porte = (rf.get('porte') or '').upper()

    # Sinais para a R1. Nao e a CAPAG: a faixa A/B/C/D so sai do Regularize.
    sinais, nota = [], 0
    if total:
        nota += 30
        sinais.append((f'Tem divida ativa na Uniao: {fmt(total)} em {len(insc)} inscricoes', True))
    else:
        sinais.append(('Nenhuma inscricao na base aberta da PGFN. Pode ser divida recente ou so na Receita: conferir no e-CAC', False))
    if total and pct_adm >= 50:
        nota += 25
        sinais.append((f'{pct_adm:.0f}% ainda nao ajuizado: melhor momento para negociar', True))
    elif total:
        sinais.append((f'So {pct_adm:.0f}% fora de execucao: checar citacao, penhora e prazo de embargos', False))
    if 'MICRO' in porte or 'PEQUENO' in porte:
        nota += 20
        sinais.append(('ME/EPP: costuma ter condicoes melhores nos editais. Conferir o edital do dia', True))
    if situacao == 'ATIVA':
        nota += 15
        sinais.append(('Empresa ATIVA, com operacao em curso', True))
    else:
        sinais.append((f'Situacao cadastral: {situacao or "nao informada"}', False))
    if len(insc) >= 3:
        nota += 10
        sinais.append(('3 ou mais inscricoes: ha o que separar e o que analisar', True))

    if nota >= 70:
        veredito, cor = 'BOM CANDIDATO A TRANSACAO', '#1f7a44'
    elif nota >= 45:
        veredito, cor = 'VALE A CONVERSA', '#b8923f'
    else:
        veredito, cor = 'CONFIRMAR DADOS ANTES DE ABORDAR', '#9a3b2f'

    socios = ''.join(
        f"<tr><td>{e(s.get('nome_socio'))}</td><td>{e(s.get('qualificacao_socio'))}</td>"
        f"<td>{e(s.get('faixa_etaria'))}</td><td>{e(s.get('data_entrada_sociedade'))}</td></tr>"
        for s in (rf.get('qsa') or [])) or "<tr><td colspan=4>Nao informado</td></tr>"
    linhas_rec = ''.join(
        f"<tr><td>{e(k)}</td><td class=c>{d['qtd']}</td><td class=r>{fmt(d['valor'])}</td></tr>"
        for k, d in porrec) or "<tr><td colspan=3 class=c>Nenhuma inscricao localizada</td></tr>"
    linhas_insc = ''.join(
        f"<tr><td>{e(a.get('NUMERO_INSCRICAO'))}</td><td>{e(a.get('DATA_INSCRICAO'))}</td>"
        f"<td>{e(a.get('SITUACAO_INSCRICAO'))}</td><td class=c>{e(a.get('INDICADOR_AJUIZADO'))}</td>"
        f"<td class=r>{fmt(valor(a))}</td></tr>"
        for a in sorted(insc, key=lambda a: -valor(a))[:60])
    li = ''.join(f"<li class={'ok' if b else 'no'}>{e(t)}</li>" for t, b in sinais)
    simples = 'Optante' if rf.get('opcao_pelo_simples') else 'Nao optante'
    if rf.get('data_exclusao_do_simples'):
        simples += ' (excluida em %s)' % rf['data_exclusao_do_simples']
    hoje = date.today().strftime('%d/%m/%Y')

    doc = f"""<!doctype html><html lang=pt-br><head><meta charset=utf-8><title>Raio-x {masc(cnpj)}</title>
<style>
@page{{size:A4;margin:14mm}}*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;color:#222;font-size:10.5pt;line-height:1.5;max-width:900px;margin:auto;padding:16px}}
.cap{{background:linear-gradient(135deg,#0e1726,#1c2b45);color:#fff;padding:28px 32px;border-radius:6px;margin-bottom:16px}}
.cap h1{{font-size:20pt}}.cap .sub{{color:#d4b36a;font-weight:600}}.cap .meta{{margin-top:12px;font-size:9pt;color:#aeb4c2}}
h2{{font-size:12.5pt;color:#0e1726;border-left:4px solid #b8923f;padding-left:10px;margin:22px 0 10px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px 24px}}.kv{{display:flex;justify-content:space-between;gap:12px;border-bottom:1px dotted #ccd;padding:4px 0}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:9.5pt}}th{{background:#0e1726;color:#fff;text-align:left;padding:7px 9px}}
td{{padding:6px 9px;border-bottom:1px solid #e6e8ee}}.c{{text-align:center}}.r{{text-align:right}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.card{{background:#f6f7fa;border:1px solid #e4e7ee;border-radius:6px;padding:12px;text-align:center}}
.card .n{{font-size:15pt;font-weight:700;color:#0e1726}}.card .l{{font-size:8.5pt;color:#667;text-transform:uppercase}}
.verd{{color:#fff;padding:14px;border-radius:6px;font-size:13pt;font-weight:700;text-align:center;margin:6px 0 12px}}
ul.s{{list-style:none}}ul.s li{{padding:6px 0 6px 24px;position:relative;border-bottom:1px solid #eee}}
ul.s li.ok:before{{content:'+';position:absolute;left:4px;color:#1f7a44;font-weight:700}}ul.s li.no:before{{content:'!';position:absolute;left:6px;color:#9a3b2f;font-weight:700}}
.box{{background:#fbf6ea;border:1px solid #e8d8a8;border-radius:6px;padding:14px 16px;margin-top:8px}}
.foot{{margin-top:24px;border-top:2px solid #b8923f;padding-top:10px;font-size:8pt;color:#889;text-align:center}}
@media(max-width:640px){{.grid,.cards{{grid-template-columns:1fr}}}}
</style></head><body>
<div class=cap><div class=sub>RAIO-X TRIBUTARIO</div><h1>{e(rf.get('razao_social'))}</h1>
<div class=sub>CNPJ {masc(cnpj)}</div>
<div class=meta>Emitido em {hoje}{(' · ' + esc) if esc else ''} · Fontes: Receita Federal (BrasilAPI) e dados abertos da PGFN, {pasta.name}</div></div>

<h2>1. Cadastro</h2><div class=grid>
<div class=kv><b>Situacao</b><span>{e(rf.get('descricao_situacao_cadastral'))}</span></div>
<div class=kv><b>Porte</b><span>{e(rf.get('porte'))}</span></div>
<div class=kv><b>Abertura</b><span>{e(rf.get('data_inicio_atividade'))}</span></div>
<div class=kv><b>Natureza juridica</b><span>{e(rf.get('natureza_juridica'))}</span></div>
<div class=kv><b>Atividade</b><span>{e(rf.get('cnae_fiscal_descricao'))}</span></div>
<div class=kv><b>Simples Nacional</b><span>{e(simples)}</span></div>
<div class=kv><b>Municipio/UF</b><span>{e(rf.get('municipio'))} / {e(rf.get('uf'))}</span></div>
<div class=kv><b>Telefone</b><span>{e(rf.get('ddd_telefone_1'))} {e(rf.get('ddd_telefone_2'))}</span></div></div>

<h2>2. Socios</h2><table><tr><th>Socio</th><th>Qualificacao</th><th>Faixa etaria</th><th>Entrada</th></tr>{socios}</table>

<h2>3. Divida ativa da Uniao</h2><div class=cards>
<div class=card><div class=n>{fmt(total)}</div><div class=l>Total</div></div>
<div class=card><div class=n>{len(insc)}</div><div class=l>Inscricoes</div></div>
<div class=card><div class=n>{fmt(total_adm)}</div><div class=l>Nao ajuizada</div></div>
<div class=card><div class=n>{fmt(total_aj)}</div><div class=l>Em execucao</div></div></div>
<div class=grid style="margin-top:10px">
<div class=kv><b>Inscricao mais antiga</b><span>{e(datas[0] if datas else '-')}</span></div>
<div class=kv><b>Inscricao mais recente</b><span>{e(datas[-1] if datas else '-')}</span></div>
<div class=kv><b>Previdenciario</b><span>{fmt(prev)}</span></div>
<div class=kv><b>FGTS</b><span>fora desta consulta</span></div></div>
<table><tr><th>Receita</th><th class=c>Inscricoes</th><th class=r>Valor</th></tr>{linhas_rec}</table>
<table><tr><th>Inscricao</th><th>Data</th><th>Situacao</th><th class=c>Ajuizada</th><th class=r>Valor</th></tr>{linhas_insc}</table>

<h2>4. Leitura para a primeira reuniao</h2>
<div class=verd style="background:{cor}">{veredito} · {nota}/100</div><ul class=s>{li}</ul>
<div class=box><b>O que este relatorio NAO diz.</b> A faixa da CAPAG (A, B, C ou D), o edital aberto, o desconto, a entrada
e o prazo so saem do Regularize, com a procuracao do cliente, no dia da analise. Faixas A e B nao tem desconto; o desconto
esta em C e D. A base aberta da PGFN e trimestral e nao mostra debitos que ainda estao na Receita.
<br><br><b>Proximos passos:</b> (1) procuracao no e-CAC; (2) situacao fiscal no e-CAC e relatorio consolidado no Regularize;
(3) simulacao da adesao no edital vigente; (4) parecer.</div>
<div class=foot>Dados publicos. Confirmar tudo no e-CAC e no Regularize antes de qualquer adesao. Uso interno.</div>
</body></html>"""

    SAIDA.mkdir(exist_ok=True)
    out = SAIDA / f'relatorio_{cnpj}.html'
    out.write_text(doc, encoding='utf-8')
    print('OK ->', out)
    print(f'   divida: {fmt(total)} | inscricoes: {len(insc)} | {veredito} ({nota}/100)')


if __name__ == '__main__':
    main()
