"""Motor autonomo de prospeccao do PAB Tributario (transacao na PGFN).

Roda sozinho (Agendador de Tarefas do Windows, todo dia) e faz, nesta ordem:
  1. Confere no site da PGFN se saiu trimestre novo dos Dados Abertos; se saiu, baixa.
  2. Le os CSVs direto do zip (SIDA = nao previdenciario, + Previdenciario), so pessoa juridica
     devedora principal, e soma a divida por CNPJ: total, em cobranca, em negociacao, ajuizado ou nao,
     tipos de tributo, inscricao mais recente.  (so quando o trimestre muda)
  3. Da uma nota a cada empresa (melhor lead = divida em cobranca, NAO ajuizada, na faixa, inscricao recente).
  4. Enriquece um lote por dia pela BrasilAPI (situacao, telefone, e-mail, CNAE, socios), com cache.
  5. Grava leads/leads_tributario.csv e .json (so empresas ATIVAS com telefone), ordenados pela nota.

NAO manda mensagem, NAO mexe no CRM nem no sistema. A lista fica pronta para a SDR / robo usar.

    python PESQUISA_PGFN/motor_autonomo.py                 # rodada normal (lote do dia)
    python PESQUISA_PGFN/motor_autonomo.py --lote 500      # lote maior
    python PESQUISA_PGFN/motor_autonomo.py --reprocessar   # refaz a agregacao do trimestre atual
"""
import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.request
import zipfile
from datetime import date, datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
DATA = PASTA / 'data'
LEADS = PASTA / 'leads'
CACHE = LEADS / 'cache_brasilapi.json'
BASE = LEADS / 'base_trimestre.json'
LOG = LEADS / 'motor.log'
SITE = 'https://dadosabertos.pgfn.gov.br/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

CONFIG = {
    'faixa_min': 100_000,       # ICP da mentoria: acima de R$ 100 mil
    'faixa_max': 10_000_000,    # acima de 10 mi = transacao individual (outro rito)
    'ufs': [],                  # vazio = Brasil todo; a nota favorece SP
    'uf_preferida': 'SP',
}
EXCLUI = ('MUNICIPIO', 'MASSA FALIDA', 'FALIDA', 'FALIDO', 'ESPOLIO', 'PREFEITURA', 'ESTADO DE', 'ESTADO DO',
          'UNIAO', 'FAZENDA PUBLICA', 'CAMARA MUNICIPAL', 'FUNDACAO UNIVERSIDADE', 'AUTARQUIA',
          'EM RECUPERACAO JUDIC', 'EM LIQUIDACAO', 'DEPARTAMENTO ESTADUAL', 'SECRETARIA', 'INSTITUTO NACIONAL',
          'CONSELHO REGIONAL', 'CONSELHO FEDERAL', 'SINDICATO', 'CONDOMINIO', 'IGREJA', 'PARTIDO')


def log(msg):
    linha = '%s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M'), msg)
    print(linha, flush=True)
    LEADS.mkdir(exist_ok=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(linha + '\n')


def http(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout)


# ---------- 1. trimestre ----------
def ultimo_trimestre():
    html = http(SITE).read().decode('latin-1')
    tri = sorted(set(re.findall(r'(20\d\d)_trimestre_(0[1-4])', html)))
    ano, t = tri[-1]
    return '%s_T%d' % (ano, int(t)), '%s_trimestre_%s' % (ano, t)


def baixar_trimestre(nome, pasta_site):
    destino = DATA / nome
    destino.mkdir(parents=True, exist_ok=True)
    html = http(SITE + pasta_site + '/').read().decode('latin-1')
    arqs = [a for a in re.findall(r'href="(Dados_abertos_[^"]+\.zip)"', html)
            if 'FGTS' not in a]  # FGTS nao entra na transacao da PGFN deste produto
    for a in arqs:
        alvo = destino / a
        if alvo.exists() and alvo.stat().st_size > 1_000_000:
            continue
        log('baixando %s/%s' % (pasta_site, a))
        tmp = alvo.with_suffix('.parcial')
        with http(SITE + pasta_site + '/' + a, timeout=600) as r, open(tmp, 'wb') as f:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
        tmp.replace(alvo)
    return destino


# ---------- 2. agregacao ----------
def num(v):
    try:
        return float(v or 0)
    except ValueError:
        return 0.0


def agregar(pasta):
    csv.field_size_limit(50_000_000)
    agg = {}
    for z in sorted(pasta.glob('Dados_abertos_*.zip')):
        prev = 'Previdenciario' in z.name
        with zipfile.ZipFile(z) as zf:
            for m in [x for x in zf.namelist() if x.lower().endswith('.csv')]:
                with zf.open(m) as raw:
                    for row in csv.DictReader(io.TextIOWrapper(raw, encoding='latin-1', newline=''), delimiter=';'):
                        if not row.get('TIPO_PESSOA', '').startswith('Pessoa jur'):
                            continue
                        if (row.get('TIPO_DEVEDOR') or '').strip().upper() != 'PRINCIPAL':
                            continue
                        cnpj = (row.get('CPF_CNPJ') or '').strip()
                        if '/' not in cnpj:
                            continue
                        uf = (row.get('UF_DEVEDOR') or '').strip()
                        if CONFIG['ufs'] and uf not in CONFIG['ufs']:
                            continue
                        v = num(row.get('VALOR_CONSOLIDADO'))
                        tipo = (row.get('TIPO_SITUACAO_INSCRICAO') or '').strip().lower()
                        d = agg.get(cnpj)
                        if d is None:
                            d = agg[cnpj] = {'cnpj': cnpj, 'nome': (row.get('NOME_DEVEDOR') or '').strip(), 'uf': uf,
                                             'total': 0.0, 'em_cobranca': 0.0, 'em_negociacao': 0.0,
                                             'ajuizado': 0.0, 'previdenciario': 0.0, 'inscricoes': 0,
                                             'ultima_inscricao': '', 'tributos': {}}
                        d['total'] += v
                        d['inscricoes'] += 1
                        if 'cobran' in tipo:
                            d['em_cobranca'] += v
                        elif 'negocia' in tipo:
                            d['em_negociacao'] += v
                        if (row.get('INDICADOR_AJUIZADO') or '').strip().upper() == 'SIM':
                            d['ajuizado'] += v
                        if prev:
                            d['previdenciario'] += v
                        dt = (row.get('DATA_INSCRICAO') or '').strip()
                        if len(dt) == 10:
                            iso = dt[6:] + '-' + dt[3:5] + '-' + dt[:2]
                            if iso > d['ultima_inscricao']:
                                d['ultima_inscricao'] = iso
                        trib = re.sub(r'^(Receita da d.vida ativa|DIV\.ATIVA)\s*-\s*', '', row.get('RECEITA_PRINCIPAL') or '').strip()[:40]
                        d['tributos'][trib] = d['tributos'].get(trib, 0) + 1
                log('  %s/%s lido: %d CNPJs' % (z.name, m, len(agg)))
    base = []
    for d in agg.values():
        if not (CONFIG['faixa_min'] <= d['total'] <= CONFIG['faixa_max']):
            continue
        if any(k in d['nome'].upper() for k in EXCLUI):
            continue
        d['tributos'] = [k for k, _ in sorted(d['tributos'].items(), key=lambda x: -x[1])[:4]]
        d['nota'] = nota(d)
        base.append(d)
    base.sort(key=lambda d: -d['nota'])
    return base


def nota(d):
    """0 a 100. Melhor lead: em cobranca (nao negociado), nao ajuizado, inscricao recente, SP, faixa 100k-1mi."""
    n = 0.0
    t = d['total'] or 1
    n += 30 * (d['em_cobranca'] / t)                 # ainda nao negociou
    n += 25 * (1 - d['ajuizado'] / t)                # cobranca administrativa = margem antes da execucao
    if d['ultima_inscricao'] >= str(date.today().year - 1):
        n += 15                                      # inscricao recente = dor nova
    if 100_000 <= d['total'] <= 1_000_000:
        n += 15                                      # faixa da adesao por edital
    elif d['total'] <= 5_000_000:
        n += 8
    if d['uf'] == CONFIG['uf_preferida']:
        n += 10
    if d['inscricoes'] >= 3:
        n += 5
    return round(n, 1)


# ---------- 4. enriquecimento ----------
def brasilapi(cnpj_num):
    with http('https://brasilapi.com.br/api/cnpj/v1/' + cnpj_num, timeout=30) as r:
        return json.load(r)


def enriquecer(base, lote, cache):
    feitos = 0
    for d in base:
        if feitos >= lote:
            break
        cn = re.sub(r'\D', '', d['cnpj'])
        if cn in cache:
            continue
        try:
            rf = brasilapi(cn)
            cache[cn] = {
                'situacao': rf.get('descricao_situacao_cadastral'), 'porte': rf.get('porte'),
                'abertura': rf.get('data_inicio_atividade'), 'cnae': rf.get('cnae_fiscal_descricao'),
                'telefone': rf.get('ddd_telefone_1') or '', 'telefone2': rf.get('ddd_telefone_2') or '',
                'email': rf.get('email') or '', 'municipio': rf.get('municipio'), 'cep': rf.get('cep'),
                'simples': rf.get('opcao_pelo_simples'),
                'socios': [s.get('nome_socio') for s in (rf.get('qsa') or [])][:3],
                'consultado_em': date.today().isoformat()}
        except urllib.error.HTTPError as ex:
            if ex.code == 429:
                log('BrasilAPI pediu para esperar (429); paro o lote aqui')
                break
            cache[cn] = {'erro': ex.code, 'consultado_em': date.today().isoformat()}
        except Exception as ex:
            log('  falhou %s: %s' % (d['cnpj'], ex))
            time.sleep(3)
            continue
        feitos += 1
        if feitos % 25 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
            log('  enriquecidas %d' % feitos)
        time.sleep(0.9)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
    return feitos


# ---------- 5. saida ----------
def gravar_leads(base, cache, trimestre):
    leads = []
    for d in base:
        c = cache.get(re.sub(r'\D', '', d['cnpj']))
        if not c or (c.get('situacao') or '').upper() != 'ATIVA' or not c.get('telefone'):
            continue
        leads.append({**{k: d[k] for k in ('cnpj', 'nome', 'uf', 'nota', 'inscricoes', 'ultima_inscricao', 'tributos')},
                      'divida_total': round(d['total'], 2), 'em_cobranca': round(d['em_cobranca'], 2),
                      'em_negociacao': round(d['em_negociacao'], 2), 'ajuizado': round(d['ajuizado'], 2),
                      'previdenciario': round(d['previdenciario'], 2), **c, 'trimestre': trimestre})
    LEADS.mkdir(exist_ok=True)
    (LEADS / 'leads_tributario.json').write_text(json.dumps(leads, ensure_ascii=False, indent=1), encoding='utf-8')
    campos = ['nota', 'nome', 'cnpj', 'uf', 'municipio', 'telefone', 'telefone2', 'email', 'divida_total',
              'em_cobranca', 'em_negociacao', 'ajuizado', 'previdenciario', 'inscricoes', 'ultima_inscricao',
              'tributos', 'porte', 'simples', 'cnae', 'socios', 'abertura', 'trimestre']
    with open(LEADS / 'leads_tributario.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=';', extrasaction='ignore')
        w.writeheader()
        for l in leads:
            w.writerow({**l, 'tributos': ', '.join(l['tributos']), 'socios': ', '.join(s for s in l['socios'] if s)})
    return leads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lote', type=int, default=300, help='empresas enriquecidas por rodada')
    ap.add_argument('--reprocessar', action='store_true')
    a = ap.parse_args()
    LEADS.mkdir(exist_ok=True)
    estado = json.loads(BASE.read_text(encoding='utf-8')) if BASE.exists() else {}
    try:
        nome, pasta_site = ultimo_trimestre()
    except Exception as ex:
        log('site da PGFN fora do ar (%s); sigo com o que tenho' % ex)
        nome, pasta_site = estado.get('trimestre'), None
    if nome and pasta_site and estado.get('trimestre') != nome:
        log('trimestre novo na PGFN: %s' % nome)
        baixar_trimestre(nome, pasta_site)
    if nome and (a.reprocessar or estado.get('trimestre') != nome):
        log('agregando %s (leva alguns minutos)' % nome)
        base = agregar(DATA / nome)
        estado = {'trimestre': nome, 'gerado_em': datetime.now().isoformat(timespec='minutes'),
                  'config': CONFIG, 'empresas': base}
        BASE.write_text(json.dumps(estado, ensure_ascii=False), encoding='utf-8')
        log('%d empresas na faixa, com nota' % len(base))
    base = estado.get('empresas', [])
    cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    n = enriquecer(base, a.lote, cache)
    leads = gravar_leads(base, cache, estado.get('trimestre'))
    log('rodada ok: +%d consultas, %d no cache, %d leads prontos (ativa + telefone) em leads/leads_tributario.csv'
        % (n, len(cache), len(leads)))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
