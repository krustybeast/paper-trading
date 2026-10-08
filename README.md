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

## What I learned

**Storing the portfolio in nested dictionaries**

The whole account lives in one dictionary, with each stock inside it as its own smaller dictionary:

```python
portfolio = {
    "cash": 8316.65,
    "holdings": {
        "AAPL": {"shares": 5, "avg_cost": 336.67}
    }
}
```

So `portfolio["holdings"]["AAPL"]["shares"]` gets how many Apple shares I own, and looping with `for symbol, info in holdings.items()` goes through every stock.

**Saving and loading with JSON**
- `json.dump()` writes the dictionary to `portfolio.json`, and `json.load()` reads it back, so the data survives after the program closes.
- On the very first run the file doesn't exist yet, so the code checks for that and creates a fresh $10,000 portfolio instead of crashing.

**Passing data into functions**
- Functions like `buy_shares(portfolio)` and `sell_shares(portfolio)` receive the portfolio and change it directly. Because dictionaries are passed by reference, the changes stick after the function ends; nothing needs to be returned.

**The menu loop**
- `while True:` keeps the menu running forever, and `break` exits it when I choose Quit.
- An `if / elif / else` chain decides what to do for each option, with `else` catching anything that isn't 1 to 6.

**Handling bad input**
- `input()` always returns text, so numbers need `int()`. Typing "abc" would crash it, so the conversion is wrapped in `try / except ValueError`.
- `.strip().upper()` cleans up what I type, so `" aapl "` becomes `"AAPL"`.

**Returning `None` to signal failure**
- `get_price()` returns the price, or `None` if anything goes wrong. The caller checks `if price is None:` and shows a friendly message, instead of the whole program crashing.

**The average cost formula**

When buying more of a stock I already own:

```python
new_avg = (old_shares * old_avg + new_shares * price) / (old_shares + new_shares)
```

When a sale brings shares to 0, the stock is removed with `del portfolio["holdings"][symbol]`.

**Formatting money in f-strings**
- `f"${value:,.2f}"` adds commas and 2 decimal places, e.g. `$1,683.35`.
- Width settings like `{symbol:<8}` and `{value:>10}` line the portfolio table up into neat columns.

**`if __name__ == "__main__":`**
- Makes `main()` run only when I run `trader.py` directly, not if another file imports it later.

**Git lessons from this project**
- Used `.gitignore` to keep `portfolio.json` off GitHub while still sharing the code.
- Committed in VS Code while also editing on GitHub, which caused "divergent branches". Now I sync before and after each session.

## Disclaimer

This is a learning project using fake money. It's not financial advice, and it ignores fees, taxes and currency conversion.
