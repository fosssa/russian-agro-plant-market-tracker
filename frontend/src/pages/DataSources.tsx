import React, { useEffect, useState } from 'react';
import { getDataSources, triggerDataCollection } from '../services/dataSourcesService';
import type { DataSource } from '../services/dataSourcesService';
import './DataSources.css';

const DataSources: React.FC = () => {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingSourceId, setLoadingSourceId] = useState<number | null>(null);

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

  useEffect(() => {
    fetchData();
  }, []);

  const handleCollectData = async (sourceId: number) => {
    try {
      setLoadingSourceId(sourceId);
      const response = await triggerDataCollection(sourceId);
      if (response.success) {
        // Обновляем список источников после успешного запуска
        await fetchData();
      }
    } catch (err) {
      console.error('Error triggering data collection:', err);
    } finally {
      setLoadingSourceId(null);
    }
  };

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
              <th>Действия</th>
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
                <td>
                  <button
                    className="collect-button"
                    onClick={() => handleCollectData(source.id)}
                    disabled={loadingSourceId === source.id}
                  >
                    {loadingSourceId === source.id ? 'Запуск...' : 'Запустить'}
                  </button>
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
