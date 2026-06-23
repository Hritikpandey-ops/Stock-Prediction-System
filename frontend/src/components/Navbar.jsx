import { NavLink } from 'react-router-dom';
import { TrendingUp, BarChart3, Search, Star, Newspaper } from 'lucide-react';

export default function Navbar() {
  const linkClass = ({ isActive }) =>
    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700 hover:text-white'
    }`;

  return (
    <nav className="bg-slate-900 border-b border-slate-700 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <TrendingUp className="text-blue-400" size={24} />
        <span className="text-white font-bold text-lg">StockPredict</span>
      </div>
      <div className="flex items-center gap-3">
        <NavLink to="/" end className={linkClass}>
          <BarChart3 size={16} /> Dashboard
        </NavLink>
        <NavLink to="/fundamentals" className={linkClass}>
          <Search size={16} /> Fundamentals
        </NavLink>
        <NavLink to="/news" className={linkClass}>
          <Newspaper size={16} /> News
        </NavLink>
        <NavLink to="/screener" className={linkClass}>
          <Search size={16} /> Screener
        </NavLink>
        <NavLink to="/watchlist" className={linkClass}>
          <Star size={16} /> Watchlist
        </NavLink>
      </div>
    </nav>
  );
}