import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

interface LoginResponse {
  status: string;
  access_token?: string;
  error?: string;
}

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('http://localhost:8001/Login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: username, password }),
      });

      const data: LoginResponse = await response.json();

      if (data.status === 'success' && data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        navigate('/dashboard');
      } else {
        setError(data.error || 'Login incorect!');
      }
    } catch (err) {
      setError('Login incorect, incearca iar!');
      console.error('Eroare login:', err);
    }
  };

  const handleCreateAccount = () => {
    navigate('/creeaza-cont');
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div className="form-login">
          <label htmlFor="username">Username:</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-login">
          <label htmlFor="password">Password:</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="mesaj-eroare">{error}</p>}
        <button type="submit" className="buton-login">
          Login
        </button>
        <button
          type="button"
          className="buton-creaza-cont"
          onClick={handleCreateAccount}
        >
          Creeaza Cont Nou
        </button>
      </form>
    </div>
  );
};

export default Login;