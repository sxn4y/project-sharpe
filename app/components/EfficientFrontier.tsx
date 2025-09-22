'use client';

import { useEffect, useState } from 'react';
import { fetchStockData, getOptimalPortfolio } from '@/lib/stockService';
import { generateEfficientFrontier } from '@/lib/utils';
import dynamic from 'next/dynamic';

const DynamicPlot = dynamic(() => import('./Plot'), { ssr: false });

interface EfficientFrontierProps {
  symbols: string[];
  startDate?: string;
  endDate?: string;
}

export function EfficientFrontier({ symbols, startDate, endDate }: EfficientFrontierProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [plotData, setPlotData] = useState<any>(null);

  useEffect(() => {
    async function createEfficientFrontierPlot() {
      try {
        setIsLoading(true);
        setError(null);

        console.log('Fetching data for symbols:', symbols);
        const stocksData = await fetchStockData(
          symbols, 
          startDate || new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          endDate || new Date().toISOString().split('T')[0]
        );
        console.log('Received stock data:', stocksData);
        
        const returns = stocksData.map(stock => stock.returns);

        const frontier = generateEfficientFrontier(returns, 1000);
        console.log('Generated frontier points:', frontier);
        
        const optimal = await getOptimalPortfolio(symbols, startDate, endDate);

        const annualizedRisks = frontier.risks.map(r => r * Math.sqrt(252));
        const annualizedReturns = frontier.returns.map(r => (1 + r) ** 252 - 1);

        const data = [
          {
            x: annualizedRisks,
            y: annualizedReturns,
            mode: 'markers',
            type: 'scatter',
            name: 'Portfolio',
            marker: {
              size: 8,
              color: frontier.sharpeRatios,
              colorscale: 'Viridis',
              showscale: true,
              colorbar: {
                title: 'Sharpe Ratio'
              }
            },
            hovertemplate:
              'Risk: %{x:.2%}<br>' +
              'Return: %{y:.2%}<br>' +
              'Sharpe Ratio: %{marker.color:.2f}<br>' +
              '<extra></extra>'
          },
          {
            x: [optimal.risk * Math.sqrt(252)],
            y: [(1 + optimal.expectedReturn) ** 252 - 1],
            mode: 'markers',
            type: 'scatter',
            name: 'Optimal Portfolio',
            marker: {
              size: 12,
              symbol: 'star',
              color: 'red'
            },
            hovertemplate:
              'Optimal Portfolio<br>' +
              'Risk: %{x:.2%}<br>' +
              'Return: %{y:.2%}<br>' +
              'Sharpe Ratio: ' + optimal.sharpeRatio.toFixed(2) + '<br>' +
              '<extra></extra>'
          }
        ];

        const layout = {
          title: 'Efficient Frontier',
          xaxis: {
            title: 'Annualized Risk',
            tickformat: '.2%',
            hoverformat: '.2%'
          },
          yaxis: {
            title: 'Annualized Expected Return',
            tickformat: '.2%',
            hoverformat: '.2%'
          },
          hovermode: 'closest',
          showlegend: true,
          width: undefined,
          height: undefined,
          autosize: true
        };

        setPlotData({ data, layout });
        setIsLoading(false);
      } catch (err) {
        console.error('Error in createEfficientFrontierPlot:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
        setIsLoading(false);
      }
    }

    if (symbols.length >= 2) {
      createEfficientFrontierPlot();
    }
  }, [symbols, startDate, endDate]);

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="w-full h-[600px] p-4 bg-white">
      {isLoading ? (
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      ) : plotData ? (
        <DynamicPlot data={plotData.data} layout={plotData.layout} />
      ) : null}
    </div>
  );
}