# Paper Trading Game

A terminal game where you trade real stocks with fake money. You start with $10,000, buy and sell shares at live market prices, and see whether your picks make or lose money over time. Built while learning to code with VS Code and Claude Code.

## Features

- **Live prices** from Yahoo Finance for any stock or ETF
- **Buy and sell** whole shares, with checks so you can't overspend or sell shares you don't own
- **Portfolio view** showing each holding's average cost, current price, value and profit/loss
- **Portfolio chart**: a pie chart of how your account is split between stocks and cash
- **Saves your progress** to `portfolio.json`, so your portfolio is still there next time you play

## How to run

Install the libraries (one time):

```
python3 -m pip install yfinance matplotlib
```

Then run it from inside the `paper-trading` folder:

```
python3 trader.py
```

## How to play

Type a number and press Enter:

```
1) Check a stock's price
2) Buy shares
3) Sell shares
4) View my portfolio
5) Show portfolio chart
6) Quit
```

Tickers to try:

| Ticker | What it is |
|---|---|
| `D05.SI` | DBS (Singapore) |
| `O39.SI` | OCBC (Singapore) |
| `ES3.SI` | STI ETF (Singapore market) |
| `AAPL` | Apple |
| `VOO` | S&P 500 ETF |

Singapore-listed tickers end in `.SI`.

## Good to know

- You can only trade **whole shares**, not fractions.
- If you buy the same stock more than once, profit/loss uses the **average price** you paid.
- When the market is closed, the price shown is the **most recent closing price**.
- Prices are in each stock's own currency (Singapore stocks in SGD, US stocks in USD).
- To **start over**, delete `portfolio.json`. A fresh $10,000 portfolio is created next time you run the game.
- `portfolio.json` is listed in `.gitignore`, so your personal game data stays on your computer and isn't uploaded to GitHub.

## Ideas for later

- Trade history log with dates and prices
- Line chart of portfolio value over time
- Leaderboard so friends can compete
- A web version with buttons using `streamlit`

## Disclaimer

This is a learning project using fake money. It's not financial advice, and it ignores fees, taxes and currency conversion.
