import { useState, useEffect } from 'react';
import cookieLogo from './assets/cookie.png';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [cookies, setCookies] = useState(0);
  const [cookieProduction, setCookieProduction] = useState(0);
  const [clickerRunning, setClickerRunning] = useState(false);
  const [shimmerRunning, setShimmerRunning] = useState(false);
  const [wrinklerRunning, setWrinklerRunning] = useState(false);
  const [maxWrinklers, setMaxWrinklers] = useState(5);
  const [cps, setCps] = useState(12);
  const [delayMs, setDelayMs] = useState(500);

  // Polling: Kekse alle 1s aktualisieren
  useEffect(() => {
    function fetchCookies() {
      fetch(`${API_BASE}/cookies`)
        .then((res) => res.json())
        .then((data) => setCookies(data.cookies))
        .catch((err) => console.error('Fetch cookies fehlgeschlagen:', err));
    }
    
    function fetchCookieProduction() {
      fetch(`${API_BASE}/cookies/production`)
        .then((res) => res.json())
        .then((data) => setCookieProduction(data.cookies_per_second))
        .catch((err) => console.error('Fetch cookies fehlgeschlagen:', err));
    }

    fetchCookies();
    fetchCookieProduction()
    const intervalId = setInterval(fetchCookies, 1000);
    const intervalIdProduction = setInterval(fetchCookieProduction, 1000)
    return () => {
      clearInterval(intervalId);
      clearInterval(intervalIdProduction);
    };
  }, []);



  function toggleClicker() {
    if (clickerRunning) {
      fetch(`${API_BASE}/clicker/stop`, { method: 'POST' })
        .then(() => setClickerRunning(false));
    } else {
      fetch(`${API_BASE}/clicker/start?cps=${cps}`, { method: 'POST' })
        .then(() => setClickerRunning(true));
    }
  }

  function toggleShimmer() {
    if (shimmerRunning) {
      fetch(`${API_BASE}/shimmer/stop`, { method: 'POST' })
        .then(() => setShimmerRunning(false));
    } else {
      fetch(`${API_BASE}/shimmer/start?delay=${delayMs}`, { method: 'POST' })
        .then(() => setShimmerRunning(true));
    }
  }

  function toggleWrinkler() {
    if (wrinklerRunning) {
      fetch(`${API_BASE}/wrinkler/stop`, { method: 'POST' })
        .then(() => setWrinklerRunning(false));
    } else {
      fetch(`${API_BASE}/wrinkler/start?max_wrinklers=${maxWrinklers}`, { method: 'POST' })
        .then(() => setWrinklerRunning(true));
    }
  }

  return (
    <div className="bg-background text-on-surface min-h-screen pb-24">
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-container-padding h-16 bg-surface-container-low shadow-sm">
        <div className="flex items-center gap-3">
          <img src={cookieLogo} alt="Cookie Foundry Logo" className="w-10 h-10 object-contain" />
          <h1 className="font-headline-md text-headline-md text-accent tracking-tight">Cookie Foundry</h1>
        </div>
      </header>

      <main className="pt-24 px-container-padding max-w-[1280px] mx-auto space-y-10">
        <section className="flex flex-col items-center justify-center py-12">
          <div className="animate-soft-pulse relative flex flex-col items-center justify-center p-12 bg-surface-container-lowest rounded-xl border-4 border-secondary-container cookie-glow">
            <span className="font-label-sm text-label-sm uppercase tracking-widest text-primary/60 mb-2">Total Batch Size</span>
            <div className="flex items-center gap-4">
              <span className="font-display-lg text-display-lg-mobile md:text-display-lg text-primary drop-shadow-sm select-none">
                {cookies !== null ? Math.floor(cookies).toLocaleString() : '...'}
              </span>
              <span className="material-symbols-outlined text-5xl text-primary" style={{ fontVariationSettings: '"FILL" 1' }}>cookie</span>
            </div>
            <div className="absolute -bottom-4 right-10 bg-tertiary px-4 py-1 rounded-full shadow-md">
              <span className="font-label-sm text-label-sm text-on-tertiary-container">+{cookieProduction}/sec</span>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-card-gap">
          {/* Auto-Clicker Card */}
          <div className="bg-surface-container-high rounded-lg p-6 flex flex-col gap-4 border-2 border-outline-variant hover:shadow-lg transition-all duration-300 group h-full">
            <div className="flex justify-between items-start">
              <div className="p-3 bg-secondary-container rounded-full text-on-secondary-container">
                <span className="material-symbols-outlined text-2xl">ads_click</span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={clickerRunning}
                  onChange={toggleClicker}
                />
                <div className="w-14 h-8 bg-surface-container-highest peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[4px] after:start-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-tertiary"></div>
              </label>
            </div>
            <div className="flex-1">
              <h3 className="font-headline-md text-headline-md text-on-surface">Auto-Clicker</h3>
              <p className="font-body-md text-body-md text-on-surface-variant min-h-[72px]">
                Automated rolling pin cycles. Currently hammering out {cps} cookies per second.
              </p>
              <div className="mt-4 space-y-2 flex flex-col">
                <label className="font-label-sm text-label-sm text-primary/60 uppercase tracking-widest">Clicks per second</label>
                <input
                  type="number"
                  value={cps}
                  onChange={(e) => setCps(Number(e.target.value))}
                  disabled={clickerRunning}
                  className="bg-surface-container-lowest border-2 border-outline-variant rounded-lg p-2 font-body-md text-on-surface focus:border-primary focus:outline-none transition-colors"
                  style={{ width: '120px' }}
                />
              </div>
            </div>
            <div className="pt-4 flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full font-label-sm text-label-sm ${clickerRunning ? 'bg-tertiary/10 text-tertiary' : 'bg-surface-variant text-on-surface-variant'}`}>
                {clickerRunning ? 'RUNNING' : 'PAUSED'}
              </span>
            </div>
          </div>

          {/* Golden Shimmer Card */}
          <div className="bg-surface-container-high rounded-lg p-6 flex flex-col gap-4 border-2 border-outline-variant hover:shadow-lg transition-all duration-300 group">
            <div className="flex justify-between items-start">
              <div className="p-3 bg-secondary-container rounded-full text-on-secondary-container">
                <span className="material-symbols-outlined text-2xl text-amber-500" style={{ fontVariationSettings: '"FILL" 1' }}>star</span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={shimmerRunning}
                  onChange={toggleShimmer}
                />
                <div className="w-14 h-8 bg-surface-container-highest peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[4px] after:start-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-tertiary"></div>
              </label>
            </div>
            <div>
              <h3 className="font-headline-md text-headline-md text-on-surface">Golden Shimmer</h3>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Detects rare golden cookies and clicks them automatically.
              </p>
              <div className="mt-4 space-y-2 flex flex-col">
                <label className="font-label-sm text-label-sm text-primary/60 uppercase tracking-widest">Click delay (ms)</label>
                <input
                  type="number"
                  value={delayMs}
                  onChange={(e) => setDelayMs(Number(e.target.value))}
                  disabled={shimmerRunning}
                  className="bg-surface-container-lowest border-2 border-outline-variant rounded-lg p-2 font-body-md text-on-surface focus:border-primary focus:outline-none transition-colors"
                  style={{ width: '120px' }}
                />
              </div>
            </div>
            <div className="mt-auto pt-4 flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full font-label-sm text-label-sm ${shimmerRunning ? 'bg-tertiary/10 text-tertiary' : 'bg-surface-variant text-on-surface-variant'}`}>
                {shimmerRunning ? 'SCANNING' : 'STANDBY'}
              </span>
            </div>
          </div>

          {/* Wrinkler Watcher Card */}
          <div className="bg-surface-container-high rounded-lg p-6 flex flex-col gap-4 border-2 border-outline-variant hover:shadow-lg transition-all duration-300 group h-full">
            <div className="flex justify-between items-start">
              <div className="p-3 bg-secondary-container rounded-full text-on-secondary-container">
                <span className="material-symbols-outlined text-2xl">ads_click</span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={wrinklerRunning}
                  onChange={toggleWrinkler}
                />
                <div className="w-14 h-8 bg-surface-container-highest peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[4px] after:start-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-tertiary"></div>
              </label>
            </div>
            <div className="flex-1">
              <h3 className="font-headline-md text-headline-md text-on-surface">Wrinkler Watcher</h3>
              <p className="font-body-md text-body-md text-on-surface-variant min-h-[72px]">
                Monitors wrinklers and automatically pops them when they reach a population of {maxWrinklers}.
              </p>
              <div className="mt-4 space-y-2 flex flex-col">
                <label className="font-label-sm text-label-sm text-primary/60 uppercase tracking-widest">Max Wrinklers</label>
                <input
                  type="number"
                  value={maxWrinklers}
                  onChange={(e) => {
                    const value = Number(e.target.value);
                    const clamped = Math.min(12, Math.max(1, value));
                    setMaxWrinklers(clamped);
                  }}
                  disabled={wrinklerRunning}
                  min={1}
                  max={12}
                  className="bg-surface-container-lowest border-2 border-outline-variant rounded-lg p-2 font-body-md text-on-surface focus:border-primary focus:outline-none transition-colors"
                  style={{ width: '120px' }}
                />
              </div>
            </div>
            <div className="pt-4 flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full font-label-sm text-label-sm ${wrinklerRunning ? 'bg-tertiary/10 text-tertiary' : 'bg-surface-variant text-on-surface-variant'}`}>
                {wrinklerRunning ? 'RUNNING' : 'PAUSED'}
              </span>
            </div>
          </div>

        </section>
      </main>
    </div>
  );
}

export default App;
