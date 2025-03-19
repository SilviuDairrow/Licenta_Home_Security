import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

interface dateSenzori {
  Distanta?: number;
  Temperatura?: number;
  Umiditate?: number;
}

const Dashboard = () => {
  const [, setAuthChecked] = useState<boolean>(false);
  const [dateSenzori, setdateSenzori] = useState<dateSenzori>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      alert('Atentificarea este necesara! Esti redirectionat catre Login!');
      navigate('/login');
      return;
    }

    const validateToken = async () => {
      try {
        const response = await fetch('http://localhost:8000/Dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error('Token invalid');
        }

        setAuthChecked(true);
        setLoading(false);

        const ws = new WebSocket('ws://localhost/ws/');

        ws.onmessage = (event: MessageEvent) => {
          try {
            const data: dateSenzori = JSON.parse(event.data);
            setdateSenzori({
              Distanta: data.Distanta,
              Temperatura: data.Temperatura,
              Umiditate: data.Umiditate,
            });
          } catch (error) {
            console.error('Eroare la procesarea datelor de pe senzori:', error);
            setError('Eroare la procesarea datelorr de pe senzori');
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('websocketul a pierdut conexiunea');
        };

        ws.onclose = () => {
          console.log('Inchide conex cu websocketu');
        };

        return () => ws.close();
      } catch (error) {
        console.error('Eroare la validarea tokenului', error);
        setError('Token invalid, redirectionare catre Login');
        localStorage.removeItem('access_token');
        navigate('/login');
      }
    };

    validateToken();
  }, [navigate]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="mesaj-eroare">{error}</div>;
  }

  return (
    <div className="dashboard-container"> 
      <h2>Dashboard Date Senzori</h2>
      <div className="date-senzori">
        <div className="card-senzor">
          <p>Distanta: {dateSenzori.Distanta?.toFixed(2) ?? 'N/A'} cm</p>
        </div>
        <div className="card-senzor">
          <p>Temperatura: {dateSenzori.Temperatura?.toFixed(2) ?? 'N/A'} °C</p>
        </div>
        <div className="card-senzor">
          <p>Umiditate: {dateSenzori.Umiditate?.toFixed(2) ?? 'N/A'} %</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;