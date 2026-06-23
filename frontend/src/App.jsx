import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Fundamentals from './pages/Fundamentals';
import News from './pages/News';
import Screener from './pages/Screener';
import Watchlist from './pages/Watchlist';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900">
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/fundamentals" element={<Fundamentals />} />
          <Route path="/news" element={<News />} />
          <Route path="/screener" element={<Screener />} />
          <Route path="/watchlist" element={<Watchlist />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}