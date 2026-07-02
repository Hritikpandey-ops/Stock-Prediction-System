import { useState, useEffect } from 'react';
import { getLatestNews, getStockNews, getSymbols } from '../services/api';
import { SkeletonNews } from '../components/SkeletonLoader';
import { Newspaper, ExternalLink, Filter } from 'lucide-react';

const SENTIMENT_COLORS = {
  POSITIVE: 'bg-green-900/50 text-green-400 border-green-700',
  NEGATIVE: 'bg-red-900/50 text-red-400 border-red-700',
  NEUTRAL: 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
};

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return dateStr; // Return original string if invalid date
  }
  
  // Format as DD MMM YYYY, HH:MM AM/PM
  const day = date.getDate().toString().padStart(2, '0');
  const month = date.toLocaleString('default', { month: 'short' });
  const year = date.getFullYear();
  let hours = date.getHours();
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // Convert 0 to 12
  
  return `${day} ${month} ${year}, ${hours}:${minutes} ${ampm}`;
}

function SentimentBadge({ label, score }) {
  if (!label) return null;
  const cls = SENTIMENT_COLORS[label] || SENTIMENT_COLORS.NEUTRAL;
  return (
    <div className="flex items-center gap-1.5">
      <span className={`px-2 py-0.5 text-xs rounded-full border font-medium ${cls}`}>
        {label}
      </span>
      {score != null && (
        <span className="text-xs text-slate-500">{score >= 0 ? '+' : ''}{score.toFixed(2)}</span>
      )}
    </div>
  );
}

function NewsCard({ item }) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          {item.symbol && (
            <span className="px-2 py-0.5 text-xs rounded bg-blue-900/50 text-blue-400 border border-blue-700 font-medium">
              {item.symbol}
            </span>
          )}
          <span className="text-xs text-slate-500">{item.source}</span>
          <span className="text-xs text-slate-600">·</span>
           <span className="text-xs text-slate-500">{formatDate(item.published_at)}</span>
        </div>
        <SentimentBadge label={item.sentiment_label} score={item.sentiment_score} />
      </div>
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block group"
      >
        <h3 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-3 mb-2">
          {item.headline}
        </h3>
      </a>
      {item.url && (
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-blue-400 transition-colors"
        >
          Read more <ExternalLink size={11} />
        </a>
      )}
    </div>
  );
}

export default function News() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('ALL');
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(30);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    getSymbols().then(r => setSymbols(r.data.symbols)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const fetchNews = selectedSymbol === 'ALL'
      ? getLatestNews(limit)
      : getStockNews(selectedSymbol, limit);

    fetchNews
      .then(r => {
        setNews(r.data.news || []);
        setTotal(r.data.count || 0);
      })
      .catch(() => setNews([]))
      .finally(() => setLoading(false));
  }, [selectedSymbol, limit]);

  const positiveCount = news.filter(n => n.sentiment_label === 'POSITIVE').length;
  const negativeCount = news.filter(n => n.sentiment_label === 'NEGATIVE').length;
  const neutralCount = news.filter(n => n.sentiment_label === 'NEUTRAL').length;
  const totalWithLabel = positiveCount + negativeCount + neutralCount;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Newspaper size={22} className="text-blue-400" />
          Market News
        </h1>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-slate-400" />
          <select
            value={selectedSymbol}
            onChange={e => {
              setSelectedSymbol(e.target.value);
              setLimit(30);
            }}
            className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm min-w-[140px]"
          >
            <option value="ALL">All Stocks</option>
            {symbols.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      {totalWithLabel > 0 && (
        <div className="grid grid-cols-3 gap-3 mb-6 max-w-md">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-center">
            <div className="text-green-400 text-lg font-bold">{positiveCount}</div>
            <div className="text-xs text-slate-400">Positive</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-center">
            <div className="text-yellow-400 text-lg font-bold">{neutralCount}</div>
            <div className="text-xs text-slate-400">Neutral</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-center">
            <div className="text-red-400 text-lg font-bold">{negativeCount}</div>
            <div className="text-xs text-slate-400">Negative</div>
          </div>
        </div>
      )}

      {loading ? (
        <SkeletonNews />
      ) : news.length === 0 ? (
        <div className="text-center py-20 text-slate-500">
          No news found.
          <div className="text-sm mt-2">Run <code className="text-blue-400">python scripts/fetch_news.py</code> to ingest news data.</div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
            {news.map(item => (
              <NewsCard key={item.id || item.url} item={item} />
            ))}
          </div>
          {total > news.length && (
            <div className="flex justify-center">
              <button
                onClick={() => setLimit(l => l + 30)}
                className="px-6 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
              >
                Load More ({total - news.length} remaining)
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}