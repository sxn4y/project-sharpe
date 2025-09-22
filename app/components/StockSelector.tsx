'use client';

import { useState } from 'react';

interface StockSelectorProps {
  selectedStocks: string[];
  startDate: string;
  endDate: string;
  onStocksChange: (symbols: string[]) => void;
  onDateRangeChange: (startDate: string, endDate: string) => void;
}

export function StockSelector({ 
  selectedStocks, 
  startDate, 
  endDate, 
  onStocksChange, 
  onDateRangeChange 
}: StockSelectorProps) {
  const [stockInput, setStockInput] = useState('');

  const handleAddStock = () => {
    const symbol = stockInput.trim().toUpperCase();
    if (symbol && !selectedStocks.includes(symbol)) {
      const newStocks = [...selectedStocks, symbol];
      console.log('Adding stock:', symbol, 'New stock list:', newStocks);
      onStocksChange(newStocks);
      setStockInput('');
    }
  };

  const handleRemoveStock = (symbol: string) => {
    const newStocks = selectedStocks.filter(s => s !== symbol);
    onStocksChange(newStocks);
  };

  const handleDateChange = (newStartDate: string, newEndDate: string) => {
    onDateRangeChange(newStartDate, newEndDate);
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-white shadow-sm">
      <div className="flex gap-4 items-center">
        <input
          type="text"
          value={stockInput}
          onChange={(e) => setStockInput(e.target.value)}
          placeholder="Enter stock symbol (e.g., AAPL)"
          className="flex-1 p-2 border rounded"
          onKeyPress={(e) => e.key === 'Enter' && handleAddStock()}
        />
        <button
          onClick={handleAddStock}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Add Stock
        </button>
      </div>

      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => handleDateChange(e.target.value, endDate)}
            className="mt-1 block w-full p-2 border rounded"
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700">End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => handleDateChange(startDate, e.target.value)}
            className="mt-1 block w-full p-2 border rounded"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {selectedStocks.map(symbol => (
          <div
            key={symbol}
            className="px-3 py-1 bg-gray-100 rounded-full flex items-center gap-2"
          >
            <span>{symbol}</span>
            <button
              onClick={() => handleRemoveStock(symbol)}
              className="text-gray-500 hover:text-red-500"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}