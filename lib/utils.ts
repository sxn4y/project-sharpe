import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Calculate daily returns from price data
export function calculateReturns(prices: number[]): number[] {
  return prices.slice(1).map((price, i) => (price - prices[i]) / prices[i]);
}

// Calculate average return
export function calculateAverageReturn(returns: number[]): number {
  return returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
}

// Calculate covariance matrix for multiple assets
export function calculateCovarianceMatrix(returns: number[][]): number[][] {
  const numAssets = returns.length;
  const meanReturns = returns.map(calculateAverageReturn);
  const covMatrix = Array(numAssets).fill(0).map(() => Array(numAssets).fill(0));

  for (let i = 0; i < numAssets; i++) {
    for (let j = i; j < numAssets; j++) {
      const cov = returns[i].reduce((sum, _, k) => {
        return sum + (returns[i][k] - meanReturns[i]) * (returns[j][k] - meanReturns[j]);
      }, 0) / (returns[i].length - 1);
      
      covMatrix[i][j] = cov;
      covMatrix[j][i] = cov; // Covariance matrix is symmetric
    }
  }

  return covMatrix;
}

// Calculate portfolio variance
export function calculatePortfolioVariance(weights: number[], covarianceMatrix: number[][]): number {
  const numAssets = weights.length;
  let variance = 0;

  for (let i = 0; i < numAssets; i++) {
    for (let j = 0; j < numAssets; j++) {
      variance += weights[i] * weights[j] * covarianceMatrix[i][j];
    }
  }

  return variance;
}

// Calculate portfolio return
export function calculatePortfolioReturn(weights: number[], returns: number[][]): number {
  const avgReturns = returns.map(calculateAverageReturn);
  return weights.reduce((sum, weight, i) => sum + weight * avgReturns[i], 0);
}

// Calculate Sharpe Ratio
export function calculateSharpeRatio(
  weights: number[],
  returns: number[][],
  covarianceMatrix: number[][],
  riskFreeRate: number = 0.02 // Default annual risk-free rate
): number {
  const portfolioReturn = calculatePortfolioReturn(weights, returns);
  const portfolioStdDev = Math.sqrt(calculatePortfolioVariance(weights, covarianceMatrix));
  
  // Convert annual risk-free rate to daily
  const dailyRiskFreeRate = Math.pow(1 + riskFreeRate, 1/252) - 1;
  
  return (portfolioReturn - dailyRiskFreeRate) / portfolioStdDev;
}

// Generate random portfolio weights that sum to 1
export function generateRandomWeights(numAssets: number): number[] {
  const weights = Array(numAssets).fill(0).map(() => Math.random());
  const sum = weights.reduce((a, b) => a + b, 0);
  return weights.map(w => w / sum);
}

// Generate efficient frontier points
export function generateEfficientFrontier(
  returns: number[][],
  numPortfolios: number = 1000
): { returns: number[]; risks: number[]; weights: number[][]; sharpeRatios: number[] } {
  const numAssets = returns.length;
  const covMatrix = calculateCovarianceMatrix(returns);
  const portfolios = Array(numPortfolios).fill(0).map(() => {
    const weights = generateRandomWeights(numAssets);
    const portReturn = calculatePortfolioReturn(weights, returns);
    const portRisk = Math.sqrt(calculatePortfolioVariance(weights, covMatrix));
    const sharpeRatio = calculateSharpeRatio(weights, returns, covMatrix);
    return { weights, return: portReturn, risk: portRisk, sharpeRatio };
  });

  return {
    returns: portfolios.map(p => p.return),
    risks: portfolios.map(p => p.risk),
    weights: portfolios.map(p => p.weights),
    sharpeRatios: portfolios.map(p => p.sharpeRatio)
  };
}
