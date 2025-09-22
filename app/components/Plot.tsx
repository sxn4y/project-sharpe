'use client';

import { useEffect, useRef } from 'react';

interface PlotData {
  x: number[];
  y: number[];
  mode: string;
  type: string;
  name: string;
  marker: {
    size: number;
    color?: number[] | string;
    colorscale?: string;
    showscale?: boolean;
    colorbar?: {
      title: string;
    };
    symbol?: string;
  };
  hovertemplate: string;
}

interface PlotProps {
  data: PlotData[];
  layout: {
    title: string;
    xaxis: {
      title: string;
      tickformat: string;
      hoverformat: string;
    };
    yaxis: {
      title: string;
      tickformat: string;
      hoverformat: string;
    };
    hovermode: string;
    showlegend: boolean;
    width?: number;
    height?: number;
    autosize?: boolean;
  };
}

export default function Plot({ data, layout }: PlotProps) {
  const plotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function initPlot() {
      try {
        const Plotly = (await import('plotly.js-dist-min')).default;
        if (plotRef.current) {
          await Plotly.newPlot(plotRef.current, data, layout);
        }
      } catch (error) {
        console.error('Error initializing plot:', error);
      }
    }

    initPlot();
  }, [data, layout]);

  return (
    <div 
      ref={plotRef} 
      className="w-full h-full border border-gray-200 rounded-lg"
      style={{ minHeight: '500px' }}
    />
  );
}