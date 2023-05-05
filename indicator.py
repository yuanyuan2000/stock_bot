from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, StochRSIIndicator, WilliamsRIndicator, ROCIndicator
from ta.trend import ADXIndicator, CCIIndicator, MACD, macd
from ta.volatility import AverageTrueRange
import re
import warnings
warnings.filterwarnings('ignore')

class TechnicalIndicators:
    def __init__(self, data):
        self.data = data

    # SMA: average "column_name" prices over the past "window" periods
    # Buy: when it lower than the current price
    # Sell: when it higher than the current price
    def add_sma(self, column_name, window):
        sma_indicator = SMAIndicator(self.data[column_name], window=window)
        self.data[f'sma_{window}'] = sma_indicator.sma_indicator()
        return self.data

    # EMA: average "column_name" prices over the past "window" periods but recent price have a higher weight
    # Buy: when it lower than the current price
    # Sell: when it higher than the current price
    def add_ema(self, column_name, window):
        ema_indicator = EMAIndicator(self.data[column_name], window=window)
        self.data[f'ema_{window}'] = ema_indicator.ema_indicator()
        return self.data

    # RSI: measures the speed of price changes. RSI=100-100/(1+RS),
    #      where RS is the ratio of the average up close to the average down close over the past "window" periods
    # Return: The return value of this function is the RSI value, which is a number between 0 and 100
    # Buy: when the RSI is less than "oversold"(generally is 30), the market is considered oversold
    # Sell: when RSI is greater than "overbought"(generally is 70), the market is considered overbought
    # Neutral: when RSI is between "oversold" and "overbought"
    def add_rsi(self, column_name, window):
        rsi_indicator = RSIIndicator(self.data[column_name], window=window)
        self.data[f'rsi_({window})'] = rsi_indicator.rsi()
        return self.data

    # STOCH: measure the momentum of an asset's price over a "k_window" period of time
    #        First, %K = (C-L)/(H-L)*100 (represents the current price in relation to recent price range)
    #        where C is the most recent closing price, L and H is the lowest/highest price during "k_window" period
    #        Then, %D represents the "d_window"-period average of %K.
    #        STOCH(9,6) is more sensitive, but STOCH(14,3,3) is popular(the last '3' means 3-period average of %D)
    # Return: The return value of this function is stoch(), which means the value of %K
    # Threshold: The default thresholds are 20 for oversold and 80 for overbought.
    def add_stoch(self, high_column, low_column, close_column, k_window, d_window):
        stoch_indicator = StochasticOscillator(self.data[high_column], self.data[low_column], 
                                            self.data[close_column], k_window, d_window)
        self.data[f'stoch_({k_window},{d_window})'] = stoch_indicator.stoch_signal()
        return self.data

    # StochRSI: measure the momentum of RSI over a "window" period of time
    #           First, RSI = 100-100/(1+RS), where RS is as we said above over the past "window" periods
    #           Next, StochRSI = (RSI-L)/(H-L)*100 (represents the current RSI in relation to recent RSI range)
    #           where L and H is the lowest/highest RSI during "window" period
    #           Then, %K is the moving average of StochRSI over "k_window" period
    #           Finally, %D is the moving average of %K over "d_window" period
    #           STOCHRSI(14,14,3,3) is popular, which means 14-period RSI, 14-period StochRSI, 3-period %K, 3-period %D
    # Return: The return value of this function is stochrsi(), which means the StochRSI value here
    # Overbought: when the StochRSI is greater than "overbought", default is 80
    # Oversold: when the StochRSI is less than "oversold", default is 20
    #           But here it just simply alert traders that RSI is near the extremes of its recent readings
    def add_stochrsi(self, column_name, window, k_window, d_window, overbought=80, oversold=20):
        stochrsi_indicator = StochRSIIndicator(self.data[column_name], window, k_window, d_window)
        self.data[f'stochrsi_({window},{window},{k_window},{d_window})'] = stochrsi_indicator.stochrsi()
        return self.data

    # MACD: Moving Average Convergence Divergence, shows the relation between two moving averages of prices
    #       The MACD line is calculated by EMA(12)-EMA(26), 12 and 26 are "short_window" and "long_window" here
    #       Then, a "signal_window"-day EMA of the MACD line is called the signal line, which is plotted on top of the MACD line
    # Return: The return value of this function is macd(), which means the MACD line value here
    # Buy: when the MACD line crosses above the signal line
    # Sell: when the MACD line crosses below the signal line
    def add_MACD(self, column_name, short_window, long_window, signal_window):
        macd_indicator = MACD(self.data[column_name], short_window, long_window, signal_window)
        self.data[f'macd_({short_window},{long_window},{signal_window})'] = macd_indicator.macd()
        self.data[f'macd_diff_({short_window},{long_window},{signal_window})'] = macd_indicator.macd_diff()
        self.data[f'macd_signal_({short_window},{long_window},{signal_window})'] = macd_indicator.macd_signal()
        return self.data
    def add_macd(self, column_name, window_fast=12, window_slow=26):
        macd_indicator = macd(self.data[column_name], window_slow, window_fast)
        self.data[f'macd_({window_fast},{window_slow})'] = macd_indicator
        return self.data

    # ADX: Average Directional Movement Index, measures the strength of a trend
    #      ADX = 100 * EMA(ABS(+DI-(-DI))/(+DI+(-DI)), window)
    #      where +DI and -DI are the positive and negative directional indicators
    #      +DI = 100 * EMA(+DM/TR, window), -DI = 100 * EMA(-DM/TR, window)
    #      where +DM = +DM = H - H(-1), -DM = L(-1) - L
    #      where H is the current high, H(-1) is the previous high, L(-1) is the previous low, L is the current low
    #      TR = MAX(H-L, ABS(H-C(-1)), ABS(L-C(-1)))
    #      where C(-1) is the previous close, C is the current close
    # Return: The return value of this function is adx(), which means the ADX value here
    # Buy: a strong trend is present when ADX is above 20 (or 25)
    # Sell: no trend is present when ADX is below 20 (or 25)
    def add_adx(self, high_column, low_column, close_column, window):
        adx_indicator = ADXIndicator(self.data[high_column], self.data[low_column], self.data[close_column], window)
        self.data[f'adx_({window})'] = adx_indicator.adx()
        return self.data

    # Williams %R: a momentum indicator that is the inverse of the Fast Stochastic Oscillator
    #              %R = (Highest High - Close)/(Highest High - Lowest Low) * -100
    #              the %R range is from 0 to -100, usually use -20 as the overbought threshold and -80 as the oversold threshold
    # Return: The return value of this function is williams_r(), which means the Williams %R value here
    # Oversold: From -100 to -80, this indicates oversold market condition
    # Overbought: From 0 to -20, this indicates overbought market condition
    # Neutral: From -80 to -20, this indicates normal market condition
    def add_williamsr(self, high_column, low_column, close_column, window):
        williamsr_indicator = WilliamsRIndicator(self.data[high_column], self.data[low_column], self.data[close_column], window)
        self.data[f'williamsr_({window})'] = williamsr_indicator.williams_r()
        return self.data

    # CCI: measures the difference between price change and its average price change to identify new trend or extreme conditions
    #      Assume the "window" is 20, so CCI = (Typical Price - 20-period SMA of TP) / (0.015 * Mean Deviation)
    #      where TP = (H+L+C)/3, Mean Deviation = Sum(|TP - 20-period SMA of TP|)/(20)
    # Return: The return value of this function is cci(), which means the CCI value here
    # Buy: When the CCI moves above +100, a new, strong uptrend is beginning, signaling a buy
    # Sell: When the CCI moves below −100, a new, strong downtrend is beginning, signaling a sell
    # Neutral: Between +100 and −100, this indicates normal market condition
    def add_cci(self, high_column, low_column, close_column, window):
        cci_indicator = CCIIndicator(self.data[high_column], self.data[low_column], self.data[close_column], window)
        self.data[f'cci_({window})'] = cci_indicator.cci()
        return self.data

    # ATR: Average True Range, measures market volatility over "window" days (usually 14 days)
    #      ATR = EMA(TR, window), where TR = MAX(H-L, ABS(H-C(-1)), ABS(L-C(-1)))
    #      where H is the current high, H(-1) is the previous high, L(-1) is the previous low, L is the current low
    #      where C(-1) is the previous close, C is the current close
    #      TR is the true range, which measures the greatest of the following:
    #      1. Current high less the current low
    #      2. The absolute value of the current high less the previous close
    #      3. The absolute value of the current low less the previous close
    # Return: The return value of this function is average_true_range(), which means the ATR value here
    # Less Volatility: A low ATR value indicates less volatility
    # High Volatility: A high ATR value indicates high volatility
    #                 However, no threshold here, it depends on the context and the timeframe being analyzed
    def add_atr(self, high_column, low_column, close_column, window):
        atr_indicator = AverageTrueRange(self.data[high_column], self.data[low_column], self.data[close_column], window)
        self.data[f'atr_({window})'] = atr_indicator.average_true_range()
        return self.data


    # ROC: Rate of Change, measures the percentage change in price between the current price and the price "window" days ago
    #      ROC = (Close - Close(-window))/Close(-window)
    #      where Close is the current close, Close(-window) is the close "window" days ago
    # Return: The return value of this function is rate_of_change(), which means the ROC value here
    # Buy: When the ROC crosses above the zero line, this indicates a buy signal
    # Sell: When the ROC crosses below the zero line, this indicates a sell signal
    def add_roc(self, column_name, window):
        roc_indicator = ROCIndicator(self.data[column_name], window)
        self.data[f'roc_({window})'] = roc_indicator.roc()
        return self.data

    # Bull bear power: measures the ability of bulls and bears to push price beyond an SMA of price
    #                  Bull Power = High - EMA(Close, window)
    #                  Bear Power = Low - EMA(Close, window)
    # Return: The return value of this function is bull_bear_power(), which means the bull bear power value here
    # Buy: When the Bull Power crosses above zero, this indicates a buy signal
    # Sell: When the Bear Power crosses below zero, this indicates a sell signal
    def add_bull_bear_power(self, high_column, low_column, close_column, window=13):
        ema = self.data[close_column].ewm(span=window).mean()
        bull_power = self.data[high_column] - ema
        bear_power = self.data[low_column] - ema
        self.data[f'bull/bear power_({window})'] = bull_power + bear_power
        return self.data

    @staticmethod
    def parse_column_name(column_name):
        indicator_type, params_str = column_name.split("_", 1)
        params = [int(x) for x in re.findall(r'\d+', params_str)]
        return indicator_type, params

    def get_signal(self, column_name, row_index=-1):
        indicator_type, params = self.parse_column_name(column_name)
        value = self.data[column_name].iloc[row_index]
        signal = "Neutral"

        # print(f"Indicator: {indicator_type}, params: {params}, value: {value}")

        if indicator_type == "sma" or indicator_type == "ema":
            current_price = self.data["Close"].iloc[row_index]
            if value < current_price:
                signal = "Buy"
            elif value > current_price:
                signal = "Sell"

        elif indicator_type == "rsi":
            oversold = 30
            overbought = 70
            if value < oversold:
                signal = "Oversold"
            elif value > overbought:
                signal = "Overbought"

        elif indicator_type == "stoch":
            oversold = 20
            overbought = 80
            if value < oversold:
                signal = "Oversold"
            elif value > overbought:
                signal = "Overbought"

        elif indicator_type == "stochrsi":
            oversold = 20
            overbought = 80
            if value < oversold:
                signal = "Oversold"
            elif value > overbought:
                signal = "Overbought"

        elif indicator_type == "macd":
            if value > 0:
                signal = "Buy"
            elif value < 0:
                signal = "Sell"

        elif indicator_type == "adx":
            strong_trend = 25
            if value > strong_trend:
                signal = "Buy"
            else:
                signal = "Sell"

        elif indicator_type == "williamsr":
            overbought = -20
            oversold = -80
            if value > overbought:
                signal = "Overbought"
            elif value < oversold:
                signal = "Oversold"

        elif indicator_type == "cci":
            overbought = 100
            oversold = -100
            if value > overbought:
                signal = "Buy"
            elif value < oversold:
                signal = "Sell"

        elif indicator_type == "atr":
            threshold = 0.06
            if value >= threshold:
                signal = "Less Volatility"
            elif value < threshold:
                signal = "High Volatility"

        elif indicator_type == "roc":
            if value > 0:
                signal = "Buy"
            elif value < 0:
                signal = "Sell"

        elif indicator_type == "bull/bear power":
            if value > 0:
                signal = "Buy"
            elif value < 0:
                signal = "Sell"

        return signal

