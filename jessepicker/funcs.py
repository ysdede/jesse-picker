# testpairs

def split(s):
    ll = s.split(' ')
    r = ll[len(ll) - 1].replace('%', '')
    r = r.replace(')', '')
    r = r.replace('(', '')
    r = r.replace(',', '')
    return r


def getmetrics(_pair, _tf, _dna, metrics, _startdate, _enddate):
    metr = [_pair, _tf, _dna, _startdate, _enddate]
    lines = metrics.splitlines()
    for index, line in enumerate(lines):

        if 'Aborted!' in line:
            print(metrics)
            print("Aborted! error. Possibly pickle database is corrupt. Delete temp/ folder to fix.")
            exit(1)

        if 'CandleNotFoundInDatabase:' in line:
            print(metrics)
            return [_pair, _tf, _dna, _startdate, _enddate, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        if 'Uncaught Exception' in line:
            print(metrics)
            exit(1)

        if 'No trades were made' in line:
            return [_pair, _tf, _dna, _startdate, _enddate, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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

        if 'Serenity Index' in line:
            a = split(line)
            metr.append(a)
            # print('Serenity:', a)

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
