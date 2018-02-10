import numpy as np
import oanda_trader
import pandas as pd
from multiprocessing import Pool as ThreadPool
from pprint import pprint
import json

instruments = ['SPX500_USD', 'NAS100_USD', 'NATGAS_USD', 'XAU_USD', 'DE30_EUR', 'XAG_USD', 'XCU_USD', 'US30_USD', 'JP225_USD', 'WTICO_USD', 'XPT_USD', 'AU200_AUD']
#granularities = ['M5', 'H1', 'H2', 'H4', 'D']

granularities = ['M5', '1H', '4H', 'D']

print('H = 0.5 is Random Walk')
print('H < 0.5 is Mean Reversion')
print('H > 0.5 is Momentum\n')

num_of_years = 1


def Calculate_Hurst(instrument):

    values = []

    for period in granularities:

        if 'M' in period:
            count = int(1440 / int(period[-1])) * (252 * num_of_years)
        elif 'H' in period:
            count = int(24 / int(period[-1]) * (252 * num_of_years))
        elif 'D' in period:
            count = 252 * num_of_years
        else:
            count = 52 * num_of_years

        # first, create an arbitrary time series, ts
        history = oanda_trader.get_history(instrument, period, count)
        data = oanda_trader.map_history(history)[0]

        df = pd.DataFrame.from_dict(data)
        df = df.set_index('Date Time')
        closes = df[['Close']].as_matrix()

        # calculate standard deviation of differenced series using various lags
        lags = range(2, 20)
        tau = [
            np.sqrt(np.std(np.subtract(closes[lag:], closes[:-lag])))
            for lag in lags
        ]

        # calculate Hurst as slope of log-log plot
        m = np.polyfit(np.log(lags), np.log(tau), 1)
        hurst = m[0] * 2.0
        print('Instrument: ', instrument, ' -- Period: ', period, ' -- Hurst: ',
              hurst)

        values.append(hurst)

    return values


if len(instruments) < 8:
    threads = len(instruments)
else:
    threads = 8

pool = ThreadPool(threads)
results = pool.map(Calculate_Hurst, instruments)
pool.close()

results_dict = {}
for i in range(len(instruments)):
    results_dict[instruments[i]] = round(results[i][0], 4)

with open('hurst.json', 'w') as outfile:
    json.dump(results_dict, outfile)

# USED FOR PLOTTING
import matplotlib.pyplot as plt
x = np.array(list(range(len(granularities))))
plt.xticks(x, granularities)
for i in range(len(instruments)):
    plt.scatter(x, results[i], label=instruments[i])

plt.axhline(y=0.5, linewidth=1, color='k')
plt.legend(loc='upper right')
plt.ylim(ymin=0, ymax=1)

plt.show()

