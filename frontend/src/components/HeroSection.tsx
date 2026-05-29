import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Users, Compass, Activity } from 'lucide-react';

export const HeroSection: React.FC = () => {
  const stats = [
    { label: 'Active Agents', value: '7 AI Crews', icon: Cpu, color: 'text-teal-400' },
    { label: 'Resolved Conflicts', value: 'Instant', icon: Users, color: 'text-indigo-400' },
    { label: 'Destinations', value: '4 Hubs', icon: Compass, color: 'text-purple-400' },
    { label: 'Latency', value: 'Real-Time', icon: Activity, color: 'text-rose-400' },
  ];

  return (
    <div className="relative pt-32 pb-8 overflow-hidden">
      {/* Background glow layers */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-7xl h-96 cyber-radial-glow pointer-events-none z-0"></div>

      <div className="max-w-6xl mx-auto px-4 relative z-10 text-center">
        {/* Banner badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-xs font-semibold text-teal-300 tracking-wider uppercase mb-6"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse"></span>
          CrewAI Orchestrated Routing Engine
        </motion.div>

        {/* Hero Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="text-4xl md:text-6xl font-orbitron font-black tracking-tight leading-none mb-6"
        >
          Group Travel Planner For the{' '}
          <span className="bg-gradient-to-r from-teal-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent text-glow-indigo">
            AI Generation
          </span>
        </motion.h1>

        {/* Hero Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.3 }}
          className="max-w-2xl mx-auto text-slate-400 text-base md:text-lg mb-10 leading-relaxed font-sans"
        >
          Maproom AI resolves travel conflicts by coordinating multiple specialized AI agents to generate highly personalized group itineraries and customized solo tracks.
        </motion.p>

        {/* Statistics Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto"
        >
          {stats.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div
                key={idx}
                className="glass-panel p-4 rounded-xl flex flex-col items-center justify-center border border-white/5 shadow-lg group hover:border-teal-500/30 transition-all duration-300"
              >
                <div className={`p-3 rounded-lg bg-slate-900/50 mb-3 border border-white/5 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
                <div className="font-orbitron font-extrabold text-base md:text-lg text-slate-100">
                  {stat.value}
                </div>
                <div className="text-xs text-slate-400 font-medium tracking-wide mt-1">
                  {stat.label}
                </div>
              </div>
            );
          })}
        </motion.div>
      </div>
    </div>
  );
};
