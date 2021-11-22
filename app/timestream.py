from datetime import datetime, timedelta
import awswrangler as wr
import boto3
from botocore.config import Config
import pandas as pd
import settings
from utils import timeit
from typing import List


class Records:
    write_client = boto3.client("timestream-write")
    query_client = boto3.client("timestream-query")

    database = settings.TIMESTREAM_DATABASE
    table = settings.TIMESTREAM_TABLE

    def __init__(
        self, 
        tickers:tuple=("ETH_USDT", "BTC_USDT")
        ):
        self.tickers = tickers
        self.measure_names = ('high', 'low', 'volume', 'close', 'number_of_trades')

    @staticmethod
    def convert_to_seconds(interval: str):
        if "m" in interval:
            return int(interval[:-1]) * 60
        if "h" in interval:
            return int(interval[:-1]) * 60 * 60
        if "d" in interval:
            return int(interval[:-1]) * 60 * 60 * 24
        if "w" in interval:
            return int(interval[:-1]) * 60 * 60 * 24 * 7

    @timeit
    def get_candles(
        self,
        start: str = "2021-11-10 16:19:59",
        end: str = "2021-11-23 19:19:59",
        interval: str = "5m",
        tail: int = 21,
    ):
        """
        Gets candles between start+tail and end dates
        Tail makes calculated indicator not start from zero
        return dict -> last_prices = {"BTC": {"close": []}, {"time": [16213221,16876876]}, "ETH": {"close": []}, {"time": []}}
        """

        cls = self.__class__


        start_tail = datetime.strptime(start, "%Y-%m-%d %H:%M:%S") - timedelta(
            seconds=(self.convert_to_seconds(interval) * tail)
        )
        try:
            df = wr.timestream.query(
                f"""
                SELECT ticker, measure_name, measure_value::double, time 
                FROM "{self.database}"."{self.table}" 
                WHERE measure_name IN {self.measure_names} 
                AND ticker IN {self.tickers} 
                AND interval='{interval}' 
                AND time >= '{start_tail}' 
                AND time <= '{end}' 
                ORDER BY time ASC"""
            )
        except self.query_client.exceptions.ValidationException:
            raise

        return pd.concat(self.transform(df))

    def transform(self, query_result: pd.DataFrame)->List[pd.DataFrame]:
        """
        input:
              ticker      measure_name  measure_value::double                time
            0  TUSD_USDT            volume          167183.000000 2021-11-20 14:34:59
            1   XVS_USDT  number_of_trades              78.000000 2021-11-20 14:34:59
            2   XVS_USDT             close              22.770000 2021-11-20 14:34:59
            3   MBL_USDT              high               0.011541 2021-11-20 14:34:59
            4   MDT_USDT              high               0.055180 2021-11-20 14:34:59

        output: List of:
             ticker      high       low     volume     close                time
            0  BTC_USDT  58421.02  58317.90  107.27729  58390.01 2021-11-20 14:34:59
            1  BTC_USDT  58496.91  58387.15   63.12707  58454.50 2021-11-20 14:39:59
            2  BTC_USDT  58481.37  58401.01   52.56274  58440.79 2021-11-20 14:44:59
            3  BTC_USDT  58492.83  58414.34   78.86668  58476.66 2021-11-20 14:49:59
            4  BTC_USDT  58495.41  58356.01   77.22721  58386.82 2021-11-20 14:54:59
        """
        result_df_array = []
        for ticker in self.tickers:
            transformed_df_base = {"ticker": ticker}
            for measure_name in self.measure_names:
                transformed_df_base[measure_name] = query_result.loc[query_result["ticker"]==ticker] \
                .loc[query_result["measure_name"]==measure_name]["measure_value::double"] \
                .tolist()

            transformed_df_base["time"] = query_result.loc[query_result["ticker"]==ticker].loc[query_result["measure_name"]=="close"]["time"].tolist()

            new_df = pd.DataFrame(transformed_df_base)
            result_df_array.append(new_df)

        return result_df_array


class MetricsSummary:
    def __init__(self):
        self.table_name = "metrics_summary"
        resource = boto3.resource("dynamodb", config=Config(read_timeout=585, connect_timeout=585))
        self.table = resource.Table("metrics_summary")

    def get_all_tickers(self):
        response = self.table.scan()
        tickers = [row["ticker"] for row in response["Items"]]
        return tuple(set(tickers))