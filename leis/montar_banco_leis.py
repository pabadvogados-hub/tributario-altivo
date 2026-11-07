"""Banco de leis tributario do PAB: baixa o texto VIGENTE das normas usadas nas teses da Mentoria CRT,
corta por artigo e indexa (SQLite FTS5) para busca rapida pelos agentes e pelo painel.

    python IVA/BANCO_DE_LEIS/TRIBUTARIO/montar_banco_leis.py            # baixa/atualiza tudo
    python IVA/BANCO_DE_LEIS/TRIBUTARIO/montar_banco_leis.py --so-indexar

Fontes: Planalto (leis, decretos, LC) e espelho Normas Legais (portarias PGFN/MF, com notas de alteracao).
Texto riscado no Planalto (<strike>) = revogado: sai do texto vigente.
Saida: textos/<SIGLA>.txt, banco_leis.db (tabelas normas, artigos, artigos_fts), normas.json.
"""
import argparse
import html
import json
import re
import sqlite3
import time
import urllib.request
from datetime import date
from pathlib import Path

PASTA = Path(__file__).resolve().parent
TEXTOS = PASTA / 'textos'
DB = PASTA / 'banco_leis.db'
PL = 'https://www.planalto.gov.br/ccivil_03/'
NL = 'https://www.normaslegais.com.br/legislacao/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'

# sigla, nome, urls (tenta em ordem), para que serve nas teses
NORMAS = [
    ('CTN', 'Codigo Tributario Nacional - Lei 5.172/1966', [PL + 'leis/l5172compilado.htm'],
     'prescricao (174), decadencia (150 par.4 e 173), fraude (185), responsabilidade (134/135), CDA (202/203)'),
    ('LEF', 'Lei de Execucoes Fiscais - Lei 6.830/1980', [PL + 'leis/l6830.htm'],
     'execucao fiscal, prescricao intercorrente (40), garantia, embargos'),
    ('L13988', 'Lei da Transacao Tributaria - Lei 13.988/2020', [PL + '_ato2019-2022/2020/lei/l13988.htm'],
     'transacao por adesao e individual, descontos, prazos, rescisao e impedimento'),
    ('L10522', 'Lei 10.522/2002 (CADIN, parcelamentos)', [PL + 'leis/2002/l10522.htm'],
     'parcelamento convencional, entrada do reparcelamento (14-A), NJP (19)'),
    ('L11941', 'Lei 11.941/2009', [PL + '_ato2007-2010/2009/lei/l11941.htm'],
     'origem do art. 14-A (reparcelamento)'),
    ('L13496', 'Lei 13.496/2017 (PERT)', [PL + '_ato2015-2018/2017/lei/l13496.htm'],
     'PERT: conta como parcelamento anterior'),
    ('DL147', 'Decreto-Lei 147/1967 (Lei Organica da PGFN)', [PL + 'decreto-lei/del0147.htm'],
     'art. 22: dever de remessa dos debitos a PGFN (base do MS de remessa)'),
    ('L9784', 'Lei 9.784/1999 (Processo Administrativo Federal)', [PL + 'leis/l9784.htm'],
     'arts. 48-50: dever de decidir em 30 dias (omissao no pedido de remessa)'),
    ('L12016', 'Lei 12.016/2009 (Mandado de Seguranca)', [PL + '_ato2007-2010/2009/lei/l12016.htm'],
     'cabimento, autoridade coatora, liminar (7, III)'),
    ('LC123', 'Lei Complementar 123/2006 (Simples Nacional)', [PL + 'leis/lcp/lcp123.htm'],
     'exclusao do Simples, parcelamento do Simples (21 par.15-24), reingresso'),
    ('PAF', 'Decreto 70.235/1972 (Processo Administrativo Fiscal)', [PL + 'decreto/d70235cons.htm'],
     'impugnacao, prazos, contencioso administrativo'),
    ('L8137', 'Lei 8.137/1990 (crimes contra a ordem tributaria)', [PL + 'leis/l8137.htm'],
     'risco penal: apropriacao (2, II)'),
    ('L10684', 'Lei 10.684/2003', [PL + 'leis/2003/l10.684.htm'],
     'art. 9: suspensao da pretensao punitiva com parcelamento'),
    ('L14375', 'Lei 14.375/2022 (alterou a 13.988)', [PL + '_ato2019-2022/2022/lei/l14375.htm'],
     'ampliacao da transacao: prejuizo fiscal, prazo de 120 meses'),
    ('CPC', 'Codigo de Processo Civil - Lei 13.105/2015', [PL + '_ato2015-2018/2015/lei/l13105.htm'],
     'tutela de urgencia (294, 300), negocio juridico processual (190), agravo (1.015)'),
    ('PORT6757', 'Portaria PGFN 6.757/2022 (regulamenta a transacao)', [NL + 'portaria-pgfn-6757-2022.htm'],
     'CAPAG presumida e efetiva (arts. 20-31), irreversibilidade (30), impedimento (64)'),
    ('PORT448', 'Portaria PGFN 448/2019 (parcelamento na PGFN)', [NL + 'portaria-pgfn-448-2019.htm'],
     'art. 17: entrada do reparcelamento por inscricao; separacao (7)'),
    ('PORTMF447', 'Portaria MF 447/2018 (prazo de remessa a PGFN)', [NL + 'portaria-mf-447-2018.htm',
                                                                    'https://www.legisweb.com.br/legislacao/?id=368654'],
     'art. 2: 90 dias na RFB para encaminhar a PGFN'),
    ('PORT742', 'Portaria PGFN 742/2018 (negocio juridico processual)', [NL + 'portaria-pgfn-742-2018.htm',
                                                                       'https://www.legisweb.com.br/legislacao/?id=373099'],
     'NJP: alternativa quando ha impedimento de transacao'),
]
# Pistas de que a pagina baixada e a norma certa (e nao pagina de erro do espelho)
PISTA = {'PORT6757': 'capacidade de pagamento', 'PORT448': 'parcelamento', 'PORTMF447': '(noventa) dias',
         'PORT742': 'negócio jurídico processual'}


def baixar(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'pt-BR'})
    with urllib.request.urlopen(req, timeout=60) as r:
        bruto = r.read()
    for cod in ('utf-8', 'cp1252'):
        try:
            return bruto.decode(cod)
        except UnicodeDecodeError:
            continue
    return bruto.decode('latin-1')


def limpar(h):
    h = re.sub(r'(?is)<(script|style|head)\b.*?</\1>', ' ', h)
    h = re.sub(r'(?is)<(strike|s|del)\b.*?</\1>', ' ', h)          # revogado
    h = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h\d|tr|table)>', '\n', h)
    h = re.sub(r'<[^>]+>', ' ', h)
    t = html.unescape(h).replace('\xa0', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return '\n'.join(l.strip() for l in t.splitlines() if l.strip())


ART = re.compile(r'^Art\.?\s*(\d+(?:\.\d+)?)\s*[º°o]?\s*(?:-\s*([A-Z]{1,2}))?\b', re.M)


def cortar_artigos(texto):
    pos = [(m.start(), m.group(1).replace('.', '') + ('-' + m.group(2) if m.group(2) else '')) for m in ART.finditer(texto)]
    arts = []
    for i, (ini, num) in enumerate(pos):
        fim = pos[i + 1][0] if i + 1 < len(pos) else len(texto)
        corpo = texto[ini:fim].strip()
        if len(corpo) > 12:
            arts.append((num, corpo[:20000]))
    return arts


def indexar(meta):
    DB.unlink(missing_ok=True)
    c = sqlite3.connect(DB)
    c.executescript('''
      CREATE TABLE normas (sigla TEXT PRIMARY KEY, nome TEXT, uso TEXT, url TEXT, baixado_em TEXT, caracteres INT);
      CREATE TABLE artigos (id INTEGER PRIMARY KEY, sigla TEXT, art TEXT, texto TEXT);
      CREATE VIRTUAL TABLE artigos_fts USING fts5(sigla, art, texto, content='artigos', content_rowid='id',
                                                  tokenize='unicode61 remove_diacritics 2');''')
    for m in meta:
        arq = TEXTOS / (m['sigla'] + '.txt')
        if not arq.exists():
            continue
        txt = arq.read_text(encoding='utf-8')
        c.execute('INSERT INTO normas VALUES (?,?,?,?,?,?)',
                  (m['sigla'], m['nome'], m['uso'], m.get('url'), m.get('baixado_em'), len(txt)))
        for num, corpo in cortar_artigos(txt):
            cur = c.execute('INSERT INTO artigos (sigla, art, texto) VALUES (?,?,?)', (m['sigla'], num, corpo))
            c.execute('INSERT INTO artigos_fts (rowid, sigla, art, texto) VALUES (?,?,?,?)',
                      (cur.lastrowid, m['sigla'], num, corpo))
    c.commit()
    n = c.execute('SELECT sigla, COUNT(*) FROM artigos GROUP BY sigla').fetchall()
    c.close()
    return dict(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--so-indexar', action='store_true')
    a = ap.parse_args()
    TEXTOS.mkdir(parents=True, exist_ok=True)
    meta_arq = PASTA / 'normas.json'
    anterior = {m['sigla']: m for m in json.loads(meta_arq.read_text(encoding='utf-8'))} if meta_arq.exists() else {}
    meta = []
    for sigla, nome, urls, uso in NORMAS:
        m = dict(anterior.get(sigla, {}), sigla=sigla, nome=nome, uso=uso)
        if not a.so_indexar:
            for u in urls:
                try:
                    t = limpar(baixar(u))
                except Exception as ex:
                    print('  falhou %s: %s' % (u, ex))
                    continue
                pista = PISTA.get(sigla)
                if len(t) < 3000 or (pista and pista.lower() not in t.lower()):
                    print('  %s: pagina sem o texto da norma (%s)' % (sigla, u))
                    continue
                (TEXTOS / (sigla + '.txt')).write_text(t, encoding='utf-8')
                m.update(url=u, baixado_em=date.today().isoformat())
                print('[ok] %-9s %8d caracteres  %s' % (sigla, len(t), nome))
                break
            else:
                print('[--] %-9s NAO BAIXADA (%s)' % (sigla, nome))
            time.sleep(1)
        meta.append(m)
    meta_arq.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    n = indexar(meta)
    print('\nIndexado: %d normas, %d artigos -> %s' % (len(n), sum(n.values()), DB))
    for s, q in sorted(n.items()):
        print('   %-9s %5d artigos' % (s, q))


if __name__ == '__main__':
    main()
