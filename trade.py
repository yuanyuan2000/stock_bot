import pandas as pd
import matplotlib.pyplot as plt

class TradingSimulator:
    def __init__(self, indicators, start_time, end_time, indicator_list):
        self.indicators = indicators
        self.start_time = start_time
        self.end_time = end_time
        self.indicator_list = indicator_list

    def calculate_fee(self, transaction_amount):
        if transaction_amount <= 1000:
            return 2
        else:
            return transaction_amount * 0.002

    def calculate_return(self):
        cash = 1000
        stocks = 0
        for i in range(self.start_time, self.end_time + 1):
            buy_signals = 0
            sell_signals = 0
            for indicator_name in self.indicator_list:
                signal = self.indicators.get_signal(indicator_name, i)
                if signal == "Buy":
                    buy_signals += 1
                elif signal == "Sell":
                    sell_signals += 1

            current_price = self.indicators.data.loc[i, "Close"]

            if buy_signals > sell_signals and cash > 0:
                stocks_to_buy = cash // current_price
                cost = stocks_to_buy * current_price
                fee = self.calculate_fee(cost)
                cash -= (cost + fee)
                stocks += stocks_to_buy
            elif sell_signals > buy_signals and stocks > 0:
                cash_from_stocks = stocks * current_price
                fee = self.calculate_fee(cash_from_stocks)
                cash += (cash_from_stocks - fee)
                stocks = 0

        final_cash_from_stocks = stocks * self.indicators.data.loc[self.end_time, "Close"]
        final_fee = self.calculate_fee(final_cash_from_stocks)
        final_cash = cash + final_cash_from_stocks - final_fee

        return final_cash

    def plot_portfolio(self):
        portfolio_values = []
        for i in range(self.start_time, self.end_time + 1):
            self.end_time = i
            portfolio_value = self.calculate_return()
            portfolio_values.append(portfolio_value)

        plt.figure(figsize=(10, 6), dpi=72)
        plt.plot(self.indicators.data.loc[self.start_time:self.end_time, "Date"], portfolio_values)
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value")
        plt.title("Portfolio Value over Time")
        plt.show()
