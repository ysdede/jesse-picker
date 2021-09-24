import os
from datetime import datetime
from subprocess import Popen, PIPE
from time import gmtime
from time import strftime
from timeit import default_timer as timer

from jesse.routes import router

from pairs import ftx_pairs

jessepickerdir = 'jessepickerdata'
anchor = 'ANCHOR!'


def make_routes(template, symbol):
    global anchor
    if anchor not in template:
        os.system('color')
        print('\nPlease replace the symbol strings in routes.py with anchors. eg:\n')
        print("""(\033[32m'FTX Futures', 'ANCHOR!', '15m', 'noStra'\033[0m),\n""")
        exit()

    template = template.replace(anchor, symbol)

    if os.path.exists('routes.py'):
        os.remove('routes.py')

    f = open('routes.py', 'w', encoding='utf-8')
    f.write(template)
    f.flush()
    os.fsync(f.fileno())
    f.close()


def write_file(_fn, _body):
    if os.path.exists(_fn):
        os.remove(_fn)

    f = open(_fn, 'w', encoding='utf-8')
    f.write(_body)
    f.flush()
    os.fsync(f.fileno())
    f.close()


def read_file(_file):
    ff = open(_file, 'r', encoding='utf-8')
    _body = ff.read()
    ff.close()
    return _body


def split(_str):
    _ll = _str.split(' ')
    _r = _ll[len(_ll) - 1].replace('%', '')
    _r = _r.replace(')', '')
    _r = _r.replace('(', '')
    _r = _r.replace(',', '')
    return _r


def getmetrics(_pair, _tf, _dna, metrics, _startdate, _enddate):
    metr = [_pair, _tf, _dna, _startdate, _enddate]
    lines = metrics.splitlines()
    for index, line in enumerate(lines):

        if 'Aborted!' in line:
            print(metrics)
            print("Aborted! error. Possibly pickle database is corrupt. Delete temp/ folder to fix.")
            exit(1)

        if 'CandleNotFoundInDatabase' in line:
            print(metrics)
            return [_pair, _tf, _dna, _startdate, _enddate, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        if 'Uncaught Exception' in line:
            print(metrics)
            exit(1)

        if 'No trades were made' in line:
            return [_pair, _tf, _dna, _startdate, _enddate, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        if 'Total Closed Trades' in line:
            a = split(line)
            metr.append(a)
            # print('Total closed:', a)

        if 'Total Net Profit' in line:
            a = split(line)
            metr.append(a)
            # print('Net Profit:', a)

        if 'Max Drawdown' in line:
            a = split(line)
            metr.append(a)
            # print('Max Drawdown:', a)

        if 'Annual Return' in line:
            a = float(split(line))
            metr.append(round(a))
            # print('Annual Return:', a)

        if 'Percent Profitable' in line:
            a = split(line)
            metr.append(a)
            # print('Percent Profitable:', a)

        if 'Sharpe Ratio' in line:
            a = split(line)
            metr.append(a)
            # print('Sharpe Ratio:', a)

        if 'Calmar Ratio' in line:
            a = split(line)
            metr.append(a)
            # print('Calmar Ratio:', a)

        if 'Winning Streak' in line:
            a = split(line)
            metr.append(a)
            # print('Winning Streak:', a)

        if 'Losing Streak' in line:
            a = split(line)
            metr.append(a)
            # print('Losing Streak:', a)

        if 'Largest Winning Trade' in line:
            a = float(split(line))
            metr.append(round(a))
            # print('Largest Winning Trade:', a)

        if 'Largest Losing Trade' in line:
            a = float(split(line))
            metr.append(round(a))
            # print('Largest Losing Trade:', a)

        if 'Total Winning Trades' in line:
            a = split(line)
            metr.append(a)
            # print('Total Winning Trades:', a)

        if 'Total Losing Trades' in line:
            a = split(line)
            metr.append(a)
            # print('Total Losing Trades:', a)

        if 'Market Change' in line:
            a = split(line)
            metr.append(a)
            # print('Market Change:', a)
    return metr


def runtest(_start_date, _finish_date, _pair, _tf, symbol):
    process = Popen(['jesse', 'backtest', _start_date, _finish_date], stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    res = output.decode('utf-8')
    # print(res)
    return getmetrics(_pair, _tf, symbol, res, _start_date, _finish_date)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')

    # Restore routes.py
    write_file('routes.py', routes_template)
    import sys
    sys.exit(0)


def run(_start_date, _finish_date):
    import signal

    signal.signal(signal.SIGINT, signal_handler)

    results = []
    sortedresults = []

    r = router.routes[0]  # Read first route from routes.py
    exchange = r.exchange
    pair = r.symbol
    timeframe = r.timeframe

    headerforfiles = ['Pair', 'TF', 'Dna', 'Start Date', 'End Date', 'Total Trades', 'Total Net Profit', 'Max.DD',
                      'Annual Profit', 'Winrate',
                      'Sharpe', 'Calmar', 'Winning Strike', 'Losing Strike', 'Largest Winning', 'Largest Losing',
                      'Num. of Wins', 'Num. of Loses',
                      'Market Change']

    header1 = ['Pair', 'TF', 'Dna', 'Start Date', 'End Date', 'Total', 'Total Net', 'Max.', 'Annual', 'Win',
               'Sharpe', 'Calmar', 'Winning', 'Losing', 'Largest', 'Largest', 'Winning', 'Losing',
               'Market']
    header2 = [' ', ' ', ' ', '   ', '   ', 'Trades', 'Profit %', 'DD %', 'Return %', 'Rate %',
               'Ratio', 'Ratio', 'Streak', 'Streak', 'Win. Trade', 'Los. Trade', 'Trades', 'Trades',
               'Change %']

    formatter = '{: <10} {: <5} {: <12} {: <12} {: <12} {: <6} {: <12} {: <8} {: <10} {: <8} {: <8} {: <12} {: <8} {: <8} ' \
                '{: <12} {: <12} {: <10} {: <10} {: <12}'

    clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    ts = datetime.now().strftime("%Y%m%d %H%M%S")

    filename = f'Pairs-{exchange}-{timeframe}--{_start_date}--{_finish_date}'

    reportfilename = f'{jessepickerdir}/results/{filename}--{ts}.csv'
    logfilename = f'{jessepickerdir}/logs/{filename}--{ts}.log'
    f = open(logfilename, 'w', encoding='utf-8')
    f.write(str(headerforfiles) + '\n')

    print('Please wait while loading candles...')

    # Read routes.py as template
    global routes_template
    routes_template = read_file('routes.py')
    num_of_pairs = len(ftx_pairs)
    start = timer()

    for index, pair in enumerate(ftx_pairs, start=1):
        make_routes(routes_template, pair)

        # Run jesse backtest and grab console output

        ress = runtest(_start_date=_start_date, _finish_date=_finish_date, _pair=pair, _tf=timeframe, symbol=pair)

        if ress not in results:
            results.append(ress)

        f.write(str(ress) + '\n')
        f.flush()
        sortedresults = sorted(results, key=lambda x: float(x[11]), reverse=True)

        clearConsole()
        rt = ((timer() - start) / index) * (num_of_pairs - index)
        rtformatted = strftime("%H:%M:%S", gmtime(rt))
        print(f'{index}/{num_of_pairs}\tRemaining Time: {rtformatted}')

        print(
            formatter.format(*header1))
        print(
            formatter.format(*header2))
        topresults = sortedresults[0:30]
        # print(topresults)
        for r in topresults:
            print(
                formatter.format(*r))
        delta = timer() - start

    # Restore routes.py
    write_file('routes.py', routes_template)

    # Sync and close log file
    os.fsync(f.fileno())
    f.close()

    # Create csv report
    # TODO: Pick better csv escape character, standart ',' fails sometimes
    f = open(reportfilename, 'w', encoding='utf-8')
    f.write(str(headerforfiles).replace('[', '').replace(']', '').replace(' ', '') + '\n')
    for srline in sortedresults:
        f.write(str(srline).replace('[', '').replace(']', '').replace(' ', '') + '\n')
    os.fsync(f.fileno())
    f.close()

    # Rewrite dnas.py, sorted by calmar
    symbol_fn = f'{jessepickerdir}/pairfiles/{pair} {_start_date} {_finish_date}.py'
    if os.path.exists(symbol_fn):
        os.remove(symbol_fn)

    f = open(symbol_fn, 'w', encoding='utf-8')
    f.write('dnas = [\n')

    sorteddnas = []
    for srr in sortedresults:
        for pair in ftx_pairs:
            # print(srr[2], dnac[0], 'DNAC:', dnac)
            if srr[2] == pair[0]:
                # f.write(str(dnac) + ',\n')
                # f.write(str(dnac).replace("""['""", """[r'""") + ',\n')
                # f.write(str(dnac).replace("""\n['""", """\n[r'""") + ',\n')
                f.write(str(pair) + ',\n')
                # sorteddnas.append(dnac)

    f.write(']\n')
    f.flush()
    os.fsync(f.fileno())
    f.close()
