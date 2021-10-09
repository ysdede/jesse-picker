import importlib
import os

import jesse.helpers as jh
from jesse.routes import router

jessepickerdir = 'jessepickerdata'


def readlog(_fn):
    with open(_fn, 'r') as ff:
        logsbody = ff.read()
    return logsbody


def picklines(_body, _limit: int = 0):
    _rows = []
    lines = _body.splitlines()

    llines = lines[-_limit:] if _limit != 0 else lines
    for index, line in enumerate(llines):
        _row = []
        if '|| win-rate:' in line:
            ll = line.replace('%', '')
            ll = ll.split('total:')
            dna = ll[0].split(' == ')[1].replace(' ', '')

            #    .replace("""\'""", """\\'""").replace('\\t', '\\\\t')
            winrate1 = ll[0].split('win-rate')[1].replace(' ', '').replace(',', '').replace(':', '').replace('None',
                                                                                                             '0')
            winrate2 = ll[1].split('win-rate')[1].replace(' ', '').replace(',', '').replace(':', '').replace('None',
                                                                                                             '0')
            pnl1 = ll[1].split(' ')[3].replace(' ', '').replace('None', '0')
            pnl2 = ll[2].split(' ')[3].replace(' ', '').replace('None', '0')
            total1 = ll[1].split(' ')[1].replace(' ', '').replace(',', '').replace('None', '0')
            total2 = ll[2].split(' ')[1].replace(' ', '').replace(',', '').replace('None', '0')
            # print('Line: ', line) print('ll[0]', ll[0]) print('ll[1]', ll[1]) print('ll[2]', ll[2]) print('DNA:',
            # dna, 'wr1:', winrate1, 'total1:', total1, 'pnl1:', pnl1, 'wr2:', winrate2, 'total2:', total2, 'pnl2:',
            # pnl2 )
            _row = [dna, int(winrate1), int(total1), float(pnl1), int(winrate2), int(total2), float(pnl2)]
            if _row not in _rows:
                _rows.append(_row)
            # print(_rows)
    return _rows


def sortdnas(inputfile: str, _stratname: str, stratclass, _top: int = 25, _rng: int = 100, _criteria: str = 'pnl1'):
    a = readlog(inputfile)  # TODO: Take input from args
    rows = picklines(a)

    fitrows = picklines(a, 30)  # get values from last iteration

    # print(rows[len(rows) - 1])
    print(f' Total {len(rows)} unique dnas found.')

    sortedbypnl1 = sorted(rows, key=lambda x: int(x[3]), reverse=True)
    sortedbypnl2 = sorted(rows, key=lambda x: int(x[6]), reverse=True)
    sortedbywr1 = sorted(rows, key=lambda x: int(x[1]), reverse=True)
    sortedbywr2 = sorted(rows, key=lambda x: int(x[4]), reverse=True)

    toppnl1 = sortedbypnl1[0:_rng]
    toppnl2 = sortedbypnl2[0:_rng]

    toptenpnl1 = sortedbypnl1[0:_top]
    toptenpnl2 = sortedbypnl2[0:_top]

    topwr1 = sortedbywr1[0:_rng]
    topwr2 = sortedbywr2[0:_rng]

    toptenwr1 = sortedbypnl1[0:_top]
    toptenwr2 = sortedbypnl2[0:_top]

    # print('PNL1', toppnl1)
    # print('PNL2', toppnl2)
    # print('Winrate1', topwr1)
    # print('Winrate2', topwr2)

    besties = fitrows
    criteria = _criteria.lower()

    """for __dna in topwr1:
        if __dna not in besties and __dna in topwr2:
            # print('pnl1 not in besties:', __dna)
            besties.append(__dna)"""
    for __dna in toptenwr1:
        if __dna not in besties:
            # print('pnl1 not in besties:', __dna)
            besties.append(__dna)

    for __dna in toptenwr2:
        if __dna not in besties:
            # print('pnl1 not in besties:', __dna)
            besties.append(__dna)

    for __dna in toptenpnl1:
        if __dna not in besties:
            # print('pnl1 not in besties:', __dna)
            besties.append(__dna)

    for __dna in toptenpnl2:
        if __dna not in besties:
            # print('pnl2 not in besties:', __dna)
            besties.append(__dna)

    for __dna in toppnl1:
        # print(sortedbypnl2[i])
        if __dna not in besties:  # and __dna in toppnl2:  # and __dna in topwr1:  # and sortedbypnl2[i] in topwr1 and sortedbypnl2[i] in topwr2:
            besties.append(__dna)
            # print(__dna)

    for __dna in toppnl2:
        # print(sortedbypnl2[i])
        if __dna not in besties:  # __dna in toppnl2 and :  # and __dna in topwr1:  # and sortedbypnl2[i] in topwr1 and sortedbypnl2[i] in topwr2:
            besties.append(__dna)
            # print(__dna)

    sortkey = 3
    criteria = _criteria.lower()
    if criteria == 'pnl1':
        sortkey = 3
    elif criteria == 'pnl2':
        sortkey = 6

    elif criteria == 'wr1':
        sortkey = 1
    elif criteria == 'wr2':
        sortkey = 4
    # print(f'*{criteria}* *{sortkey}*')
    sortedbesties = sorted(besties, key=lambda x: int(x[sortkey]), reverse=True)
    # print(besties)
    print(f'Picked dnas count: {len(sortedbesties)}')
    # Create dna output file and write header
    dnafilename = f'{jessepickerdir}/dnafiles/{_stratname}dnas.py'
    if os.path.exists(dnafilename):
        os.remove(dnafilename)
    with open(dnafilename, 'w') as f:
        f.write('dnas = [\n')

        for dd in sortedbesties:
            dnastr = dd[0]
            # print('DNASTR:', dnastr)
            hyperparameters = jh.dna_to_hp(stratclass.hyperparameters(None),
                                           dnastr)  # routes_moded.run(dnastr, dna=True, _ret=True)
            if not hyperparameters:
                print(
                    'Could not decode dnas! Please check strategy name in routes.py file.\nCheck strategy file for hyperparameters definition! Bye.')
                exit()

            # print('encoded:', hyperparameters)
            dd.append(hyperparameters)
            f.write(str(dd).replace("""\n['""", """\n[r'""") + ',\n')

        f.write(']\n')
        f.flush()
        os.fsync(f.fileno())
    return sortedbesties


def valideoutputfile(_sortedbesties, _stratname):
    p = f'{jessepickerdir}.dnafiles.{_stratname}dnas'
    # {jessepickerdir}.dnafiles.wtewoHyper2dnas
    dnas = importlib.import_module(p)
    if len(dnas.dnas) == len(_sortedbesties):
        print(f'Validated dna file. {len(dnas.dnas)}/{len(_sortedbesties)}')
    else:
        print('Creating dna file failed!')


if __name__ == "__main__":
    r = router.routes[0]  # Read first route from routes.py
    strategy = r.strategy_name
    StrategyClass = jh.get_strategy_class(r.strategy_name)

    sortedbesties = sortdnas('{jessepickerdir}/ewoHyper2-Binance-BTC-USDT-2h.txt', strategy, StrategyClass, 25, 100)
    valideoutputfile(sortedbesties, strategy)
