'use client'

import { useSearchParams, useRouter } from 'next/navigation';
import { StockSelector } from './components/StockSelector';
import { EfficientFrontier } from './components/EfficientFrontier';

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const selectedStocks = searchParams.get('stocks')?.split(',').filter(Boolean) || [];
  const startDate = searchParams.get('startDate') || 
    new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  const endDate = searchParams.get('endDate') || 
    new Date().toISOString().split('T')[0];

  const handleStocksChange = (symbols: string[]) => {
    const params = new URLSearchParams(searchParams.toString());
    if (symbols.length > 0) {
      params.set('stocks', symbols.join(','));
    } else {
      params.delete('stocks');
    }
    router.push(`?${params.toString()}`);
  };

  const handleDateRangeChange = (newStartDate: string, newEndDate: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('startDate', newStartDate);
    params.set('endDate', newEndDate);
    router.push(`?${params.toString()}`);
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-gray-900">Portfolio Optimization</h1>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Select Stocks</h2>
          <StockSelector
            selectedStocks={selectedStocks}
            startDate={startDate}
            endDate={endDate}
            onStocksChange={handleStocksChange}
            onDateRangeChange={handleDateRangeChange}
          />
        </div>

        {selectedStocks.length > 1 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Efficient Frontier</h2>
            <EfficientFrontier
              symbols={selectedStocks}
              startDate={startDate}
              endDate={endDate}
            />
          </div>
        )}

        {selectedStocks.length <= 1 && (
          <div className="text-center p-8 bg-white rounded-lg shadow-sm">
            <p className="text-gray-600">
              Please select at least two stocks to generate the efficient frontier.
            </p>
            <p className="text-gray-500 mt-2">
              Current stocks: {selectedStocks.length ? selectedStocks.join(', ') : 'none'}
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
