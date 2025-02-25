import React, { JSX } from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import App from './App'
import Login from './components/Login/Login'
import Dashboard from './components/Dashboard/Dashboard'
import './index.css'

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem('access_token')
  return token ? children : <Navigate to="/" replace />
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Login />
      },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        )
      }
    ]
  }
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)