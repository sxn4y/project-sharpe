import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# CLI COLORS
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
CYAN = "\033[96m"

isRunning = True
tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]

# -----------------------
# 1. Data Fetching
# -----------------------
def fetch_yahoo_data(tickers, start=None, end=None):
    print(f"{BLUE}⬇️  Fetching price data for: {tickers}...{RESET}")
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    print(f"{GREEN}✅ Data fetch complete. {len(data)} records loaded.{RESET}")
    return data.dropna()

# -----------------------
# 2. Portfolio Statistics
# -----------------------
def compute_portfolio_stats(weights, mean_returns, cov_matrix, returns, risk_free_rate=0.02):
    weights = np.array(weights)
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)

    # Calculate downside deviation
    portfolio_returns = returns @ weights
    downside_returns = portfolio_returns[portfolio_returns < 0]
    downside_std = np.std(downside_returns) * np.sqrt(252)

    # Sortino Ratio
    sortino = (portfolio_return - risk_free_rate) / downside_std if downside_std > 0 else 0
    return portfolio_return, portfolio_vol, sortino

# -----------------------
# 3. Random Portfolio Simulation
# -----------------------
def simulate_random_portfolios(n_portfolios, mean_returns, cov_matrix, returns, risk_free_rate):
    results = []
    weight_records = []
    n_assets = len(mean_returns)

    print(f"{BLUE}🎲 Simulating {n_portfolios} random portfolios...{RESET}")
    for _ in range(n_portfolios):
        weights = np.random.random(n_assets)
        weights /= weights.sum()
        port_return, port_vol, sortino = compute_portfolio_stats(weights, mean_returns, cov_matrix, returns, risk_free_rate)
        results.append([port_vol, port_return, sortino])
        weight_records.append(weights)

    print(f"{GREEN}✅ Simulation complete.{RESET}")
    df = pd.DataFrame(results, columns=["volatility", "return", "sortino"])
    df["weights"] = weight_records
    return df

# -----------------------
# 4. Max Sortino Portfolio
# -----------------------
def max_sortino_portfolio(mean_returns, cov_matrix, returns, risk_free_rate):
    n = len(mean_returns)
    def neg_sortino(weights):
        return -compute_portfolio_stats(weights, mean_returns, cov_matrix, returns, risk_free_rate)[2]

    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = tuple((0, 1) for _ in range(n))
    return minimize(neg_sortino, n*[1./n], bounds=bounds, constraints=constraints)

# -----------------------
# 5. Plot Results
# -----------------------
def plot_results(results_df, best_portfolio, tickers):
    plt.figure(figsize=(8, 7))

    scatter = plt.scatter(results_df["volatility"], results_df["return"],
                          c=results_df["sortino"], cmap="plasma", alpha=0.5)

    plt.scatter(best_portfolio["volatility"], best_portfolio["return"],
                marker="*", color="red", s=300, label="Max Sortino Portfolio")

    plt.annotate(f"★ Max Sortino\nRatio={best_portfolio['sortino']:.2f}",
                xy=(best_portfolio["volatility"], best_portfolio["return"]),
                xytext=(best_portfolio["volatility"] + 0.02, best_portfolio["return"] - 0.02),
                arrowprops=dict(facecolor='black', arrowstyle="->"))

    weights_text = "\n".join([f"{t}: {w:.2%}" for t, w in zip(tickers, best_portfolio["weights"])])
    textstr = (f"Max Sortino Portfolio:\n"
              f"{weights_text}\n\n"
              f"Return: {best_portfolio['return']:.2%}\n"
              f"Volatility: {best_portfolio['volatility']:.2%}\n"
              f"Sortino: {best_portfolio['sortino']:.2f}")

    props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85)
    plt.gca().text(1.25, 0.5, textstr, transform=plt.gca().transAxes,
                  fontsize=10, verticalalignment='center', bbox=props)

    plt.colorbar(scatter, label="Sortino Ratio")
    plt.title("Sortino Ratio Portfolio Optimization")
    plt.xlabel("Volatility (Risk)")
    plt.ylabel("Expected Annual Return")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

# -----------------------
# 6. Main Program
# -----------------------
if __name__ == "__main__":
    print(f"{CYAN}📊 Sortino Ratio Optimizer{RESET}")

    # User input
    print(f"{YELLOW}💡 Enter custom tickers (comma-separated) or press Enter for default ({tickers}):{RESET} ", end="")
    user_input = input().strip()
    if user_input:
        tickers = [t.strip().upper() for t in user_input.split(",")]

    start = input(f"{CYAN}Enter start date (YYYY-MM-DD) or press Enter for 2 years ago:{RESET} ") or None
    end = input(f"{CYAN}Enter end date (YYYY-MM-DD) or press Enter for today:{RESET} ") or None

    risk_free_rate = 0.05

    price_data = fetch_yahoo_data(tickers, start=start, end=end)
    log_returns = np.log(price_data / price_data.shift(1)).dropna()
    mean_returns = log_returns.mean() * 252
    cov_matrix = log_returns.cov() * 252

    results_df = simulate_random_portfolios(5000, mean_returns, cov_matrix, log_returns, risk_free_rate)

    print(f"{BLUE}🔎 Finding max Sortino ratio portfolio...{RESET}")
    max_sortino = max_sortino_portfolio(mean_returns, cov_matrix, log_returns, risk_free_rate)
    best_weights = max_sortino.x
    best_return, best_vol, best_sortino = compute_portfolio_stats(best_weights, mean_returns, cov_matrix, log_returns, risk_free_rate)
    best_portfolio = {"weights": best_weights, "return": best_return, "volatility": best_vol, "sortino": best_sortino}

    print(f"{GREEN}✅ Max Sortino Portfolio found! Sortino={best_sortino:.2f}{RESET}")
    for t, w in zip(tickers, best_weights):
        print(f"{t}: {w:.2%}")

    plot_results(results_df, best_portfolio, tickers)
