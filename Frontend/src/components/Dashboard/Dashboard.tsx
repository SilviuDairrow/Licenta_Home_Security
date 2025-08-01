import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

interface dateSenzori {
  Distanta?: number;
  Temperatura?: number;
  Umiditate?: number;
}

interface GalerieImagini {
  jupani: string[];
  straini: string[];
}

const Dashboard = () => {
  const [, setAuthChecked] = useState<boolean>(false);
  const [dateSenzori, setdateSenzori] = useState<dateSenzori>({});
  const [galerie, setGalerie] = useState<GalerieImagini>({ jupani: [], straini: [] });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  const fetchImages = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('Token lipsa');

      const date_token = JSON.parse(atob(token.split('.')[1]));
      const username = date_token.sub;

      const res = await fetch(`http://localhost:8000/api/${username}/ImaginiToate`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error('Eroare fetch imagini');

      const data = await res.json();
      setGalerie(data);
    } catch (err: any) {
      console.error(err);
      if (err.message !== 'Failed to fetch') {
        setError('Nu s-au putut incarca imaginile');
      }
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      alert('Autentificare necesara');
      navigate('/');
      return;
    }

    const validateToken = async () => {
      try {
        const response = await fetch('http://localhost:8000/Dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error('Token invalid');

        setAuthChecked(true);
        setLoading(false);
        fetchImages();

        const ws = new WebSocket('ws://localhost/ws/');

        ws.onmessage = (event: MessageEvent) => {
          try {
            const data: dateSenzori = JSON.parse(event.data);
            setdateSenzori(data);
          } catch {
            setError('Eroare procesare date senzori');
          }
        };

        ws.onerror = () => setError('Websocket deconectat');
        ws.onclose = () => console.log('Websocket inchis');

        return () => ws.close();
      } catch {
        setError('Token invalid, redirectionare');
        localStorage.removeItem('access_token');
        navigate('/');
      }
    };

    validateToken();
  }, [navigate]);

  if (loading) return <div className="loading">Loading...</div>;

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

      <h2 style={{ marginTop: '16px' }}>Imagini Camere</h2>

      {error && <div className="mesaj-eroare">{error}</div>}

      <div className="image-gallery">
        <h3>Imagini Jupani</h3>
        <div className="image-grid">
          {galerie.jupani.length > 0 ? (
            galerie.jupani.map((url, idx) => (
              <div key={idx} className="image-card">
                <img src={url} alt="Jupani" />
                {/* <div className="image-meta"><p>Jupani</p></div> */}
              </div>
            ))
          ) : (
            <div className="image-card empty-placeholder"></div>
          )}
        </div>

        <h3>Imagini Straini</h3>
        <div className="image-grid">
          {galerie.straini.length > 0 ? (
            galerie.straini.map((url, idx) => (
              <div key={idx} className="image-card">
                <img src={url} alt="Straini" />
                {/* <div className="image-meta"><p>Straini</p></div> */}
              </div>
            ))
          ) : (
            <div className="image-card empty-placeholder"></div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
