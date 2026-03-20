import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import GamePage from './pages/GamePage';
import './index.css';

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <GamePage />,
      },
      {
        path: 'leaderboard',
        element: <div className="p-8"><h1 className="text-2xl font-display">Ranking Global</h1></div>,
      },
      {
        path: 'wallet',
        element: <div className="p-8"><h1 className="text-2xl font-display">Carteira e Depósitos</h1></div>,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      }
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
