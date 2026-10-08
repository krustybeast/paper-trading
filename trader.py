# ============================================================
#  PAPER TRADING GAME
#  Practice buying and selling stocks with fake money!
#  Run it with:  python3 trader.py
# ============================================================

# --- Imports: bringing in tools other people have written ---
import json      # lets us save/load data to a text file in JSON format
import logging   # controls which behind-the-scenes messages libraries print
import os        # lets us check whether a file exists
import warnings  # lets us hide harmless warning messages

# Some libraries print noisy (but harmless) warnings on startup.
# This line hides them so the game screen stays clean.
warnings.filterwarnings("ignore")

import yfinance as yf            # downloads live stock prices from Yahoo Finance
import matplotlib.pyplot as plt  # draws charts (we use it for the portfolio pie chart)

# yfinance prints its own technical error when a symbol isn't found.
# We turn that off because our game shows its own friendlier message instead.
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


# --- Settings (constants) ---
# Writing these in ALL CAPS is a Python habit meaning "this value never changes".
STARTING_CASH = 10000.00          # how much fake money a new player gets
SAVE_FILE = "portfolio.json"      # the file where progress is saved

# Colors for the pie chart slices. These were picked so neighbouring slices are
# easy to tell apart, even for people who are colorblind. Each stock gets the
# next color in this list, in order.
STOCK_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]
CASH_COLOR = "#b4b2a9"     # a neutral gray, so cash looks different from the stocks
OTHER_COLOR = "#e34948"    # used only if you own more stocks than we have colors for


# ============================================================
#  SAVING AND LOADING
# ============================================================

def load_portfolio():
    """Load the saved portfolio from the file, or start a new one."""
    # If the save file exists, read it.
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)  # turns the JSON text back into a Python dictionary
        except (json.JSONDecodeError, OSError):
            # If the file is damaged or unreadable, don't crash - just start fresh.
            print("Couldn't read your save file, so starting a new game.")

    # No save file yet (first time playing): create a brand-new portfolio.
    # "holdings" will look like: {"AAPL": {"shares": 5, "avg_cost": 180.25}}
    #   - shares   = how many shares you own
    #   - avg_cost = the average price you paid per share (used for profit/loss)
    return {"cash": STARTING_CASH, "holdings": {}}


def save_portfolio(portfolio):
    """Write the portfolio to the save file so progress isn't lost."""
    with open(SAVE_FILE, "w") as f:
        # indent=2 makes the file nicely formatted if you open it to look inside
        json.dump(portfolio, f, indent=2)


# ============================================================
#  GETTING STOCK PRICES
# ============================================================

def get_price(symbol):
    """
    Look up the latest price for a stock symbol (like "AAPL").
    Returns the price as a number, or None if it couldn't be found.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Ask for the last 5 days of prices. (We use 5 days instead of 1 so it
        # still works on weekends and holidays when the market is closed.)
        history = ticker.history(period="5d")

        # If no data came back, the symbol probably doesn't exist.
        if history.empty:
            return None

        # "Close" is the closing price column; .iloc[-1] grabs the LAST (newest) row.
        # round(..., 2) rounds to the nearest cent, like a real price.
        return round(float(history["Close"].iloc[-1]), 2)
    except Exception:
        # Any problem (no internet, bad symbol, etc.) -> treat it as "not found".
        return None


# ============================================================
#  HELPER FUNCTIONS FOR USER INPUT
# ============================================================

def ask_symbol():
    """Ask the user for a stock symbol and clean it up (e.g. ' aapl ' -> 'AAPL')."""
    return input("Enter stock symbol (e.g. AAPL, TSLA, MSFT): ").strip().upper()


def ask_whole_number(prompt):
    """
    Keep asking until the user types a positive whole number.
    Returns that number, or None if they typed something invalid.
    """
    text = input(prompt).strip()
    # .isdigit() is True only if every character is 0-9 (no letters, minus signs, or decimals)
    if not text.isdigit() or int(text) <= 0:
        print("Please enter a whole number greater than 0.")
        return None
    return int(text)


def money(amount):
    """Format a number as money, e.g. 1234.5 -> '$1,234.50' and -5 -> '-$5.00'."""
    if amount < 0:
        return f"-${-amount:,.2f}"
    return f"${amount:,.2f}"


# ============================================================
#  MENU ACTIONS
# ============================================================

def check_price():
    """Menu option 1: show the current price of a stock."""
    symbol = ask_symbol()
    print("Looking up price...")
    price = get_price(symbol)

    if price is None:
        print(f"Sorry, couldn't find a price for '{symbol}'.")
    else:
        print(f"{symbol} is currently {money(price)} per share.")


def buy_shares(portfolio):
    """Menu option 2: buy shares of a stock."""
    symbol = ask_symbol()
    print("Looking up price...")
    price = get_price(symbol)
    if price is None:
        print(f"Sorry, couldn't find a price for '{symbol}'.")
        return  # "return" here means: stop this function early

    # Show the price and how many shares the player could afford.
    max_affordable = int(portfolio["cash"] // price)  # // divides and rounds down
    print(f"{symbol} costs {money(price)} per share.")
    print(f"You have {money(portfolio['cash'])} cash (enough for up to {max_affordable} shares).")

    shares = ask_whole_number("How many shares do you want to buy? ")
    if shares is None:
        return

    total_cost = shares * price

    # RULE: you can't spend more cash than you have!
    if total_cost > portfolio["cash"]:
        print(f"Not enough cash! That would cost {money(total_cost)}, "
              f"but you only have {money(portfolio['cash'])}.")
        return

    # Take the money out of your cash.
    # round(..., 2) keeps cash to whole cents (computers can add tiny decimal errors).
    portfolio["cash"] = round(portfolio["cash"] - total_cost, 2)

    holdings = portfolio["holdings"]
    if symbol in holdings:
        # You already own some: update the share count and the average cost.
        # New average = (old total spent + new amount spent) / total shares
        old = holdings[symbol]
        old_total_spent = old["shares"] * old["avg_cost"]
        new_share_count = old["shares"] + shares
        old["avg_cost"] = (old_total_spent + total_cost) / new_share_count
        old["shares"] = new_share_count
    else:
        # First time buying this stock: add a new entry.
        holdings[symbol] = {"shares": shares, "avg_cost": price}

    save_portfolio(portfolio)  # save right away so nothing is lost
    print(f"Bought {shares} share(s) of {symbol} for {money(total_cost)}.")
    print(f"Cash remaining: {money(portfolio['cash'])}")


def sell_shares(portfolio):
    """Menu option 3: sell shares you own."""
    symbol = ask_symbol()
    holdings = portfolio["holdings"]

    # RULE: you can't sell a stock you don't own!
    if symbol not in holdings:
        print(f"You don't own any shares of {symbol}.")
        return

    owned = holdings[symbol]["shares"]
    print(f"You own {owned} share(s) of {symbol}.")

    shares = ask_whole_number("How many shares do you want to sell? ")
    if shares is None:
        return

    # RULE: you can't sell more shares than you have!
    if shares > owned:
        print(f"You can't sell {shares} shares - you only own {owned}.")
        return

    print("Looking up price...")
    price = get_price(symbol)
    if price is None:
        print(f"Sorry, couldn't get a price for '{symbol}' right now. Try again later.")
        return

    sale_amount = shares * price
    # Profit on THIS sale = (sell price - what you paid) x number of shares
    profit = (price - holdings[symbol]["avg_cost"]) * shares

    # Add the money to your cash and remove the shares.
    portfolio["cash"] = round(portfolio["cash"] + sale_amount, 2)
    holdings[symbol]["shares"] -= shares

    # If you sold everything, remove the stock from your holdings entirely.
    if holdings[symbol]["shares"] == 0:
        del holdings[symbol]

    save_portfolio(portfolio)
    print(f"Sold {shares} share(s) of {symbol} at {money(price)} for {money(sale_amount)}.")
    print(f"Profit/loss on this sale: {money(profit)}")
    print(f"Cash now: {money(portfolio['cash'])}")


def view_portfolio(portfolio):
    """Menu option 4: show everything you own, its value, and profit/loss."""
    holdings = portfolio["holdings"]
    cash = portfolio["cash"]

    print("\n================ YOUR PORTFOLIO ================")

    total_stock_value = 0  # we'll add up the value of every stock here

    if not holdings:
        print("You don't own any stocks yet.")
    else:
        print("Fetching current prices...")
        # Print the table header. The numbers like <8 and >12 set column widths
        # (< means left-aligned, > means right-aligned) so everything lines up.
        print(f"{'Symbol':<8}{'Shares':>8}{'Avg Cost':>12}{'Price':>12}{'Value':>14}{'Profit/Loss':>14}")
        print("-" * 68)

        # Loop through each stock you own, one at a time.
        for symbol, info in holdings.items():
            shares = info["shares"]
            avg_cost = info["avg_cost"]
            price = get_price(symbol)

            if price is None:
                # If we can't get a price, fall back to what you paid so the totals still work.
                print(f"{symbol:<8}{shares:>8}  (couldn't get current price)")
                price = avg_cost

            value = shares * price                     # what your shares are worth now
            profit = (price - avg_cost) * shares       # how much you've gained or lost
            total_stock_value += value

            print(f"{symbol:<8}{shares:>8}{money(avg_cost):>12}{money(price):>12}"
                  f"{money(value):>14}{money(profit):>14}")

        print("-" * 68)

    # Summary: stocks + cash, compared to what you started with.
    account_total = cash + total_stock_value
    print(f"Total stock value: {money(total_stock_value)}")
    print(f"Cash:              {money(cash)}")
    print(f"Total account:     {money(account_total)}")
    print(f"Overall gain/loss: {money(account_total - STARTING_CASH)} "
          f"(you started with {money(STARTING_CASH)})")
    print("================================================")


def show_portfolio_chart(portfolio):
    """Menu option 5: show a pie chart of how your account is split up."""
    holdings = portfolio["holdings"]
    cash = portfolio["cash"]

    # Nothing to chart yet - a pie that's 100% cash isn't very interesting.
    if not holdings:
        print("You don't own any stocks yet. Buy some first, then come back to see your chart!")
        return

    print("Fetching current prices...")

    # We'll build up a list of (name, dollar value) pairs - one per slice.
    slices = []
    for symbol, info in holdings.items():
        price = get_price(symbol)
        if price is None:
            # Same as "View my portfolio": fall back to what you paid if the price lookup fails.
            print(f"Couldn't get a current price for {symbol}, so using what you paid instead.")
            price = info["avg_cost"]
        slices.append((symbol, info["shares"] * price))

    # If you own more stocks than we have colors, the smallest ones get
    # grouped together into a single "Other" slice so the chart stays readable.
    other_value = 0
    if len(slices) > len(STOCK_COLORS):
        # Sort biggest first. "key=lambda s: s[1]" means "sort by the dollar value".
        biggest_first = sorted(slices, key=lambda s: s[1], reverse=True)
        keep = len(STOCK_COLORS) - 1  # leave one color free for the "Other" slice
        kept_symbols = [name for name, value in biggest_first[:keep]]
        other_value = sum(value for name, value in biggest_first[keep:])
        # Keep the original order (the order you bought them in), so a stock's
        # color doesn't jump around just because its price changed.
        slices = [(name, value) for name, value in slices if name in kept_symbols]

    # Give each stock its color, in order.
    colors = STOCK_COLORS[:len(slices)]
    if other_value > 0:
        slices.append(("Other", other_value))
        colors.append(OTHER_COLOR)

    # Add cash as the last slice (skip it if you've spent every cent).
    if cash > 0:
        slices.append(("Cash", cash))
        colors.append(CASH_COLOR)

    # Add up every slice to get the total account value.
    total = sum(value for name, value in slices)

    # Build a label for each slice, like "AAPL\n$1,234.56 (12.3%)".
    # "\n" means "start a new line".
    labels = [f"{name}\n{money(value)} ({value / total * 100:.1f}%)" for name, value in slices]
    values = [value for name, value in slices]

    # --- Draw the chart ---
    # fig is the whole window, ax is the area the pie is drawn in.
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(
        values,
        labels=labels,
        colors=colors,
        startangle=90,       # start the first slice at the top (12 o'clock)
        counterclock=False,  # go around clockwise, like a clock
        labeldistance=1.12,  # put labels just outside the pie so small slices stay readable
        wedgeprops={"edgecolor": "white", "linewidth": 2},  # thin white gap between slices
        textprops={"color": "#333333", "fontsize": 10},
    )
    ax.set_title(f"Your Portfolio - Total Account Value: {money(total)}",
                 fontsize=14, fontweight="bold", pad=20)
    ax.axis("equal")  # keeps the pie a perfect circle instead of an oval
    fig.tight_layout()  # makes sure nothing gets cut off at the edges

    print("Opening chart... (close the chart window to get back to the menu)")
    plt.show()  # this pauses the game until you close the window


# ============================================================
#  MAIN PROGRAM (the game loop)
# ============================================================

def main():
    portfolio = load_portfolio()
    print("Welcome to the Paper Trading Game!")
    print(f"You have {money(portfolio['cash'])} in cash.")

    # "while True" repeats forever, until we hit "break" (when you choose Quit).
    while True:
        print("\n----- MENU -----")
        print("1) Check a stock's price")
        print("2) Buy shares")
        print("3) Sell shares")
        print("4) View my portfolio")
        print("5) Show portfolio chart")
        print("6) Quit")  # keep Quit as the last option
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            check_price()
        elif choice == "2":
            buy_shares(portfolio)
        elif choice == "3":
            sell_shares(portfolio)
        elif choice == "4":
            view_portfolio(portfolio)
        elif choice == "5":
            show_portfolio_chart(portfolio)
        elif choice == "6":
            save_portfolio(portfolio)
            print("Progress saved. Goodbye!")
            break  # exit the loop, which ends the program
        else:
            print("That's not a valid option. Please type a number from 1 to 6.")


# This special line means: "only run main() if this file is run directly"
# (not if another file imports it). It's a common Python pattern.
if __name__ == "__main__":
    main()
