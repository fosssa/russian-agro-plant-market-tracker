import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import {
  getFilterOptions,
  getChartData,
} from '../services/visualizationService';
import type {
  FilterOption,
  ChartData,
} from '../services/visualizationService';
import './Visualization.css';

const Visualization: React.FC = () => {
  const [sourceOptions, setSourceOptions] = useState<FilterOption[]>([]);
  const [productOptions, setProductOptions] = useState<FilterOption[]>([]);
  const [selectedSource, setSelectedSource] = useState<string | number>('');
  const [selectedProduct, setSelectedProduct] = useState<string | number>('');
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Load filter options on mount
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const [sources, products] = await Promise.all([
          getFilterOptions('source'),
          getFilterOptions('product'),
        ]);
        setSourceOptions(sources);
        setProductOptions(products);
        
        // Set default selections
        if (sources.length > 0 && products.length > 0) {
          setSelectedSource(sources[0].value);
          setSelectedProduct(products[0].value);
        }
      } catch (error) {
        console.error('Error loading filter options:', error);
      }
    };

    loadFilterOptions();
  }, []);

  // Load chart data when filters change
  useEffect(() => {
    if (selectedSource && selectedProduct) {
      const loadChartData = async () => {
        try {
          setLoading(true);
          const data = await getChartData(selectedSource, selectedProduct);
          setChartData(data);
        } catch (error) {
          console.error('Error loading chart data:', error);
        } finally {
          setLoading(false);
        }
      };

      loadChartData();
    }
  }, [selectedSource, selectedProduct]);

  const getChartOptions = () => {
    if (!chartData) return {};

    return {
      title: {
        text: 'Динамика цен',
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        formatter: (params: any) => {
          const param = params[0];
          return `${param.name}<br/>${param.seriesName}: ${param.value} руб.`;
        },
      },
      xAxis: {
        type: 'category',
        data: chartData.xAxisData,
        name: 'Время',
        nameLocation: 'middle',
        nameGap: 30,
      },
      yAxis: {
        type: 'value',
        name: 'Цена (руб.)',
        nameLocation: 'middle',
        nameGap: 50,
      },
      series: [
        {
          name: chartData.seriesName,
          type: 'line',
          data: chartData.seriesData,
          smooth: true,
          itemStyle: {
            color: '#5470c6',
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: 'rgba(84, 112, 198, 0.3)',
                },
                {
                  offset: 1,
                  color: 'rgba(84, 112, 198, 0.05)',
                },
              ],
            },
          },
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100,
        },
        {
          start: 0,
          end: 100,
        },
      ],
      grid: {
        left: '10%',
        right: '5%',
        bottom: '15%',
        top: '15%',
      },
    };
  };

  return (
    <div className="visualization">
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="source-filter">Источник:</label>
          <select
            id="source-filter"
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
          >
            {sourceOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="product-filter">Продукт:</label>
          <select
            id="product-filter"
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
          >
            {productOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="chart-container">
        {loading ? (
          <div className="loading">Загрузка данных графика...</div>
        ) : chartData ? (
          <ReactECharts
            option={getChartOptions()}
            style={{ height: '500px', width: '100%' }}
            notMerge={true}
            lazyUpdate={true}
          />
        ) : (
          <div className="no-data">Нет данных для отображения</div>
        )}
      </div>
    </div>
  );
};

export default Visualization;
