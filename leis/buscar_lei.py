"""Busca no banco de leis tributario.

    python IVA/BANCO_DE_LEIS/TRIBUTARIO/buscar_lei.py CTN 174          # artigo exato
    python IVA/BANCO_DE_LEIS/TRIBUTARIO/buscar_lei.py "capacidade de pagamento revisao"   # busca livre
    python IVA/BANCO_DE_LEIS/TRIBUTARIO/buscar_lei.py PORT6757 30
"""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent / 'banco_leis.db'


def artigo(sigla, art):
    with sqlite3.connect(DB) as c:
        return c.execute('SELECT sigla, art, texto FROM artigos WHERE sigla = ? AND art = ?',
                         (sigla.upper(), art.upper())).fetchall()


def buscar(q, n=8):
    termos = ' '.join('"%s"' % t.replace('"', '') for t in q.split())
    with sqlite3.connect(DB) as c:
        return c.execute('SELECT sigla, art, snippet(artigos_fts, 2, "[", "]", " ... ", 30) FROM artigos_fts '
                         'WHERE artigos_fts MATCH ? ORDER BY rank LIMIT ?', (termos, n)).fetchall()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    a = sys.argv[1:]
    if len(a) == 2 and not a[0].islower() and a[1][:1].isdigit():
        r = artigo(a[0], a[1])
        print('\n\n'.join('%s art. %s\n%s' % x for x in r) or 'Nao achei esse artigo.')
    else:
        for s, n, t in buscar(' '.join(a)):
            print('%s art. %s: %s\n' % (s, n, t))
