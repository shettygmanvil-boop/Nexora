import React, { useEffect, useState } from 'react';
import { Compass, ShieldAlert, Cpu, RefreshCw } from 'lucide-react';
import { ApiService } from '../services/api';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [checking, setChecking] = useState<boolean>(false);

  const checkStatus = async () => {
    setChecking(true);
    const online = await ApiService.testConnection();
    setApiOnline(online);
    setChecking(false);
  };

  useEffect(() => {
    checkStatus();
    // Poll every 15 seconds
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-white/5 px-6 py-4 flex items-center justify-between">
      {/* Brand Logo */}
      <div className="flex items-center gap-3 select-none">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-teal-500/10 border border-teal-500/30 shadow-[0_0_15px_rgba(20,184,166,0.15)]">
          <Compass className="w-5 h-5 text-teal-400 animate-pulse" />
          <div className="absolute inset-0 rounded-lg bg-gradient-to-tr from-teal-500/20 to-indigo-500/20 blur opacity-45"></div>
        </div>
        <div className="flex flex-col">
          <span className="font-orbitron font-extrabold text-lg tracking-wider bg-gradient-to-r from-teal-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent text-glow-teal">
            MAPROOM AI
          </span>
          <span className="text-[10px] text-slate-400 font-medium tracking-widest uppercase -mt-1">
            Travel Crew Orchestrator
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-lg border border-white/5">
        {[
          { id: 'dashboard', label: 'Planner', icon: Compass },
          { id: 'agents', label: 'AI Agents', icon: Cpu },
          { id: 'docs', label: 'API Specs', icon: ShieldAlert }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all duration-300 ${
                isActive
                  ? 'bg-teal-500/10 text-teal-300 border border-teal-500/20 shadow-[0_0_10px_rgba(20,184,166,0.1)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Server Status Indicators */}
      <div className="flex items-center gap-3">
        <button 
          onClick={checkStatus} 
          disabled={checking}
          className="p-2 rounded-md bg-white/5 border border-white/5 text-slate-400 hover:text-teal-400 hover:border-teal-500/20 transition-all duration-300 disabled:opacity-50"
          title="Refresh server status"
        >
          <RefreshCw className={`w-4 h-4 ${checking ? 'animate-spin' : ''}`} />
        </button>
        
        <div className="flex items-center gap-2 px-3.py-1.5 rounded-full bg-slate-950/80 border border-white/5 text-xs font-semibold py-1 px-3">
          <span className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              apiOnline === null ? 'bg-amber-400' : apiOnline ? 'bg-teal-400' : 'bg-rose-400'
            }`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${
              apiOnline === null ? 'bg-amber-500' : apiOnline ? 'bg-teal-500' : 'bg-rose-500'
            }`}></span>
          </span>
          <span className="text-slate-400 tracking-wide">
            API: {apiOnline === null ? 'CHECKING' : apiOnline ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>
      </div>
    </nav>
  );
};
