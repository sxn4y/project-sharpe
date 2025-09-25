import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

isRunning = True;

# ticker selection
tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]

while isRunning:
    print("Create new graph? (Y/n): ")
    choice = input().lower()
    if (choice.replace(' ', '') == 'n'):
        isRunning = False
        
    print("Do you want to select custom tickers? (y/N) Default tickers are [\"AAPL\", \"MSFT\", \"GOOG\", \"AMZN\"]: ")
    choice = input().lower()
    if (choice.replace(' ', '') == 'y'):
        tickers = input("Enter tickers separated by commas: ").replace(" ", "").capitalize().split(",")
        print(f"Selected tickers: {tickers}")
    elif (choice.replace(' ', '') == 'n'):
        print(f"Using default tickers: {tickers}")
    else:
        print(f"Using default tickers: {tickers}")


    # -----------------------
    # 1. Fetch Price Data
    # -----------------------
    def fetch_yahoo_data(tickers, period="2y"):
        """
        Fetch adjusted close prices for given tickers.
        Returns DataFrame with aligned dates.
        """
        data = yf.download(tickers, period=period, auto_adjust=True)["Close"]
        return data.dropna()

    # -----------------------
    # 2. Portfolio Metrics
    # -----------------------
    def compute_portfolio_stats(weights, mean_returns, cov_matrix, risk_free_rate=0.02):
        weights = np.array(weights)
        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(weights.T @ cov_matrix @ weights)
        sharpe = (port_return - risk_free_rate) / port_vol
        return port_return, port_vol, sharpe

    # -----------------------
    # 3. Random Portfolios
    # -----------------------
    def simulate_random_portfolios(n_portfolios, mean_returns, cov_matrix, risk_free_rate):
        results = []
        weight_records = []
        n_assets = len(mean_returns)

        for _ in range(n_portfolios):
            weights = np.random.random(n_assets)
            weights /= weights.sum()
            port_return, port_vol, sharpe = compute_portfolio_stats(weights, mean_returns, cov_matrix, risk_free_rate)
            results.append([port_vol, port_return, sharpe])
            weight_records.append(weights)

        df = pd.DataFrame(results, columns=["volatility", "return", "sharpe"])
        df["weights"] = weight_records
        return df

    # -----------------------
    # 4. Efficient Frontier
    # -----------------------
    def min_variance(mean_returns, cov_matrix):
        n = len(mean_returns)
        args = (cov_matrix,)
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n))
        result = minimize(lambda w, cov: w.T @ cov @ w, n*[1./n], args=args, bounds=bounds, constraints=constraints)
        return result.x

    def efficient_frontier(mean_returns, cov_matrix, target_returns):
        frontier_vols = []
        n = len(mean_returns)
        bounds = tuple((0, 1) for _ in range(n))

        for r in target_returns:
            constraints = (
                {"type": "eq", "fun": lambda w: np.sum(w) - 1},
                {"type": "eq", "fun": lambda w: np.dot(w, mean_returns) - r}
            )
            result = minimize(lambda w, cov: w.T @ cov @ w, n*[1./n], args=(cov_matrix,), bounds=bounds, constraints=constraints)
            if result.success:
                frontier_vols.append(np.sqrt(result.fun))
            else:
                frontier_vols.append(np.nan)
        return frontier_vols

    # -----------------------
    # 5. Max Sharpe Ratio Optimizer
    # -----------------------
    def max_sharpe_portfolio(mean_returns, cov_matrix, risk_free_rate):
        n = len(mean_returns)
        def neg_sharpe(w):
            port_return, port_vol, sharpe = compute_portfolio_stats(w, mean_returns, cov_matrix, risk_free_rate)
            return -sharpe
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n))
        result = minimize(neg_sharpe, n*[1./n], bounds=bounds, constraints=constraints)
        return result

    # -----------------------
    # 6. Plot Function
    # -----------------------
    def plot_results(results_df, frontier_returns, frontier_vols, best_portfolio, tickers):
        plt.figure(figsize=(12, 7))

        # Scatter random portfolios
        scatter = plt.scatter(results_df["volatility"], results_df["return"],
                              c=results_df["sharpe"], cmap="viridis", alpha=0.5)
        # plt.colorbar(scatter, label="Sharpe Ratio")

        # Plot efficient frontier
        plt.plot(frontier_vols, frontier_returns, 'r--', linewidth=2, label="Efficient Frontier")

        # Mark max Sharpe portfolio with a star
        plt.scatter(best_portfolio["volatility"], best_portfolio["return"],
                    marker="*", color="red", s=300, label="Max Sharpe Portfolio")

        # Annotate the star point
        plt.annotate(f"★ Max Sharpe\nRatio={best_portfolio['sharpe']:.2f}",
                    xy=(best_portfolio["volatility"], best_portfolio["return"]),
                    xytext=(best_portfolio["volatility"] + 0.02, best_portfolio["return"] - 0.02),
                    arrowprops=dict(facecolor='black', arrowstyle="->"))

        # Create text box with portfolio analytics
        weights_text = "\n".join([f"{t}: {w:.2%}" for t, w in zip(tickers, best_portfolio["weights"])])
        textstr = (f"Max Sharpe Portfolio:\n"
                  f"{weights_text}\n\n"
                  f"Return: {best_portfolio['return']:.2%}\n"
                  f"Volatility: {best_portfolio['volatility']:.2%}\n"
                  f"Sharpe: {best_portfolio['sharpe']:.2f}")

        props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85)
        plt.gca().text(1.05, 0.5, textstr, transform=plt.gca().transAxes,
                      fontsize=10, verticalalignment='center', bbox=props)

        plt.title("Markowitz Portfolio Optimization")
        plt.xlabel("Volatility (Risk)")
        plt.ylabel("Expected Annual Return")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()


    # -----------------------
    # Main Execution
    # -----------------------
    if __name__ == "__main__":
        risk_free_rate = 0.05

        print("Fetching price data...")
        price_data = fetch_yahoo_data(tickers)
        log_returns = np.log(price_data / price_data.shift(1)).dropna()
        mean_returns = log_returns.mean() * 252
        cov_matrix = log_returns.cov() * 252

        print("Simulating portfolios...")
        results_df = simulate_random_portfolios(5000, mean_returns, cov_matrix, risk_free_rate)

        print("Finding max Sharpe portfolio...")
        max_sharpe = max_sharpe_portfolio(mean_returns, cov_matrix, risk_free_rate)
        best_weights = max_sharpe.x
        best_return, best_vol, best_sharpe = compute_portfolio_stats(best_weights, mean_returns, cov_matrix, risk_free_rate)
        best_portfolio = {"weights": best_weights, "return": best_return, "volatility": best_vol, "sharpe": best_sharpe}

        # Compute efficient frontier
        frontier_returns = np.linspace(results_df["return"].min(), results_df["return"].max(), 100)
        frontier_vols = efficient_frontier(mean_returns, cov_matrix, frontier_returns)

        print("\nMax Sharpe Portfolio:")
        for t, w in zip(tickers, best_weights):
            print(f"{t}: {w:.2%}")
        print(f"Expected Return: {best_return:.2%}")
        print(f"Volatility: {best_vol:.2%}")
        print(f"Sharpe Ratio: {best_sharpe:.2f}")

        # Plot results
        plot_results(results_df, frontier_returns, frontier_vols, best_portfolio, tickers)