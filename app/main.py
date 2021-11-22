from timestream import Records, MetricsSummary
import utils

import settings

all_tickers = MetricsSummary().get_all_tickers()
print(all_tickers[:40])
records = Records(tickers=all_tickers[:40])
result = records.get_candles()
import pdb
pdb.set_trace()

for tickers in utils.split(all_tickers, 5):
    pass