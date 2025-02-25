import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeftEndOnRectangleIcon, HomeIcon, CameraIcon } from '@heroicons/react/24/solid';
import './App.css';

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
  };

  return (
    <div className="app-container">
      <header>
        <h1 className='titlu-pagina'>Home Security System</h1>
        {location.pathname !== '/' && (
          <div className="navbar">
            <div className="butoane-navbar">
              <button className="buton-navbar" onClick={() => navigate('/dashboard')}>
                <HomeIcon className="h-4 w-4"/>
                Dashboard
              </button>
              <button className="buton-navbar" onClick={() => navigate('/camera1')}>
                <CameraIcon className="h-4 w-4"/>
                Camera 1
              </button>
              <button className="buton-navbar" onClick={() => navigate('/camera2')}>
                <CameraIcon className="h-4 w-4"/>
                Camera 2
              </button>
              <button className="buton-navbar" onClick={handleLogout}>
                <ArrowLeftEndOnRectangleIcon className="h-4 w-4"/>
                Logout
              </button>
            </div>
          </div>
        )}
      </header>

      <main>
        <Outlet /> {}
      </main>

      <footer>
        <p>© 2025 Secan Silviu-Gabriel. All credits reserved.</p>
      </footer>
    </div>
  );
}

export default App;