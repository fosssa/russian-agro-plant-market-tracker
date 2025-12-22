import React, { useEffect, useState } from 'react';
import { getDataSources } from '../services/dataSourcesService';
import type { DataSource } from '../services/dataSourcesService';
import './DataSources.css';

const DataSources: React.FC = () => {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await getDataSources();
        setDataSources(data);
        setError(null);
      } catch (err) {
        setError('Ошибка загрузки данных источников');
        console.error('Error fetching data sources:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="data-sources">
        <div className="loading">Загрузка данных...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-sources">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="data-sources">
      <div className="table-container">
        <table className="data-sources-table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Местоположение</th>
              <th>Последний запуск</th>
            </tr>
          </thead>
          <tbody>
            {dataSources.map((source) => (
              <tr key={source.id}>
                <td>{source.name}</td>
                <td>{source.location}</td>
                <td>
                  <span className={`status-icon ${source.lastRunStatus ? 'success' : 'failed'}`}>
                    {source.lastRunStatus ? '✔' : '✖'}
                  </span>
                  {' '}
                  {source.lastRunDate}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataSources;
