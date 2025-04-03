import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import './CreereCont.css';

interface CreateAccountResponse {
  status: string;
  message?: string;
  error?: string;
}

const CreeazaCont = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleCreateAccount = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await fetch('http://localhost:8001/creeaza_cont', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: username, password }),
      });

      const data: CreateAccountResponse = await response.json();

      if (data.status === 'success') {
        setSuccess(data.message || 'Cont creat cu succes!');
        setTimeout(() => navigate('/'), 2000); 
      } else {
        setError(data.error || 'Exista deja un cont cu acest Username!');
      }
    } catch (err) {
      setError('Eroare la crearea contului, incearca iar!');
      console.error('Eroare creare cont:', err);
    }
  };

  return (
    <div className = "creeaza-cont-container">
      <h2>Creeaza Cont Nou</h2>
      <form onSubmit = {handleCreateAccount}>

        <div className = "form-creeaza-cont">
          <label htmlFor = "username">Username:</label>
          <input
            id = "username"
            type = "text"
            value = {username}
            onChange = {(e) => setUsername(e.target.value)}
            required
          />
        </div>
        
        <div className = "form-creeaza-cont">
          <label htmlFor = "password">Password:</label>
          <input
            id = "password"
            type = "password"
            value = {password}
            onChange = {(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {error && <p className = "mesaj-eroare">{error}</p>}
        {success && <p className = "mesaj-succes">{success}</p>}

        <button type = "submit" className = "buton-creeaza-cont">
          Creeaza Cont
        </button>

        <button type = "button" 
        className = "buton-login-creeaza" 
        onClick={() => navigate('/')}>
          Inapoi la Login
        </button>
      </form>
    </div>
  );
};

export default CreeazaCont;