import React, { JSX } from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import App from './App'
import Login from './components/Login/Login'
import Dashboard from './components/Dashboard/Dashboard'
import CreeazaCont from './components/Cont_nou/CreereCont'
import './index.css'
import Camera1 from './components/Camera1/Camera1'
import Camera2 from './components/Camera2/Camera2'

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
      },
      {
        path: 'creeaza-cont',
        element: <CreeazaCont />
      },
      {
        path: 'camera1',
        element: <Camera1/>
      },
      {
        path: 'camera2',
        element: <Camera2/>
      }
    ]
  }
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)