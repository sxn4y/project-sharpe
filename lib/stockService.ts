import { GetStocksAggregatesTimespanEnum, restClient } from '@polygon.io/client-js';
import { calculateReturns, generateEfficientFrontier } from './utils';

// Initialize the Polygon.io client
const rest = restClient(process.env.NEXT_PUBLIC_POLY_API_KEY!);

export interface StockData {
  symbol: string;
  prices: number[];
  returns: number[];
  dates: string[];
}

export async function fetchStockData(
  symbols: string[],
  startDate: string,
  endDate: string
): Promise<StockData[]> {
  try {
    console.log('API Key:', process.env.NEXT_PUBLIC_POLY_API_KEY);
    console.log('Fetching data for:', { symbols, startDate, endDate });
    const stockDataPromises = symbols.map(async (symbol) => {
      const response = await rest.getStocksAggregates(
        symbol,
        1,
        GetStocksAggregatesTimespanEnum.Day,
        startDate,
        endDate
      );

      if (!response.results) {
        throw new Error(`No data found for ${symbol}`);
      }

      const prices = response.results.map(result => result.c); // Using closing prices
      const dates = response.results.map(result => new Date(result.t).toISOString().split('T')[0]);
      const returns = calculateReturns(prices);

      return {
        symbol,
        prices,
        returns,
        dates: dates.slice(1) // Slice to match returns length
      };
    });

    return await Promise.all(stockDataPromises);
  } catch (error) {
    console.error('Error fetching stock data:', error);
    throw error;
  }
}

// Format date string to YYYY-MM-DD
export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

// Get default date range (1 year from today)
export function getDefaultDateRange(): { startDate: string; endDate: string } {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setFullYear(startDate.getFullYear() - 1);
  
  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate)
  };
}

// Calculate the optimal portfolio weights for maximum Sharpe ratio
export async function getOptimalPortfolio(
  symbols: string[],
  startDate?: string,
  endDate?: string
): Promise<{
  weights: number[];
  expectedReturn: number;
  risk: number;
  sharpeRatio: number;
  symbols: string[];
}> {
  const dateRange = getDefaultDateRange();
  const stocksData = await fetchStockData(
    symbols,
    startDate || dateRange.startDate,
    endDate || dateRange.endDate
  );

  // Extract returns arrays for portfolio calculations
  const returns = stocksData.map(stock => stock.returns);

  // Generate efficient frontier points
  const frontier = generateEfficientFrontier(returns);

  // Find the portfolio with the highest Sharpe ratio
  const maxSharpeIndex = frontier.sharpeRatios.indexOf(Math.max(...frontier.sharpeRatios));

  return {
    weights: frontier.weights[maxSharpeIndex],
    expectedReturn: frontier.returns[maxSharpeIndex],
    risk: frontier.risks[maxSharpeIndex],
    sharpeRatio: frontier.sharpeRatios[maxSharpeIndex],
    symbols
  };
}