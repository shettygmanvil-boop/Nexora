import React from 'react';
import { motion } from 'framer-motion';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

interface ScoreBarProps {
  compatibilityScore: number;
  factorScores: Record<string, number>;
}

const keyToLabel: Record<string, string> = {
  mood_match: 'Mood Sync',
  travel_purpose_match: 'Purpose Match',
  budget_suitability: 'Budget Fit',
  vibe_match: 'Vibe Harmony',
  age_suitability: 'Age Match',
  medical_suitability: 'Health Safety',
  activity_level_compatibility: 'Activity Pace',
  food_preference_compatibility: 'Food Compatibility',
};

const keyToColor: Record<string, string> = {
  mood_match: 'bg-teal-500',
  travel_purpose_match: 'bg-sky-500',
  budget_suitability: 'bg-indigo-500',
  vibe_match: 'bg-purple-500',
  age_suitability: 'bg-pink-500',
  medical_suitability: 'bg-rose-500',
  activity_level_compatibility: 'bg-amber-500',
  food_preference_compatibility: 'bg-emerald-500',
};

export const ScoreBar: React.FC<ScoreBarProps> = ({ compatibilityScore, factorScores }) => {
  // Convert factorScores to Recharts Radar data format
  const chartData = Object.keys(factorScores).map((key) => ({
    subject: keyToLabel[key] || key,
    value: factorScores[key],
    fullMark: 100,
  }));

  // Setup SVG circular gauge variables
  const radius = 60;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(100, Math.max(0, compatibilityScore)) / 100) * circumference;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
      {/* Circle Gauge (3 cols) */}
      <div className="lg:col-span-4 flex flex-col items-center justify-center p-4 bg-slate-950/40 rounded-xl border border-white/5">
        <span className="font-orbitron font-extrabold text-xs tracking-widest text-slate-400 uppercase mb-4 text-center">
          Compatibility Score
        </span>
        <div className="relative w-40 h-40 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background Circle */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              className="stroke-slate-800"
              strokeWidth={strokeWidth}
              fill="transparent"
            />
            {/* Foreground Glow Circle */}
            <motion.circle
              cx="80"
              cy="80"
              r={radius}
              className="stroke-teal-500"
              strokeWidth={strokeWidth}
              fill="transparent"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
              strokeLinecap="round"
              style={{
                filter: 'drop-shadow(0 0 6px rgba(20, 184, 166, 0.5))',
              }}
            />
          </svg>
          {/* Inner Text */}
          <div className="absolute flex flex-col items-center justify-center">
            <motion.span
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="font-orbitron font-black text-3xl text-slate-100 text-glow-teal"
            >
              {compatibilityScore.toFixed(0)}%
            </motion.span>
            <span className="text-[10px] text-teal-400 font-bold tracking-widest uppercase mt-0.5">
              Sync Rate
            </span>
          </div>
        </div>
      </div>

      {/* Radar Chart (4 cols) */}
      <div className="lg:col-span-4 h-56 flex flex-col items-center justify-center bg-slate-950/40 rounded-xl border border-white/5 p-2">
        <span className="font-orbitron font-extrabold text-xs tracking-widest text-slate-400 uppercase mb-2">
          Sync Metrics
        </span>
        <div className="w-full h-full min-h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: 'rgba(203, 213, 225, 0.7)', fontSize: 9, fontFamily: 'Orbitron' }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 8 }}
                axisLine={false}
                tickLine={false}
              />
              <Radar
                name="Group compatibility"
                dataKey="value"
                stroke="#14b8a6"
                fill="#14b8a6"
                fillOpacity={0.25}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Linear progress bars (4 cols) */}
      <div className="lg:col-span-4 space-y-3 p-4 bg-slate-950/40 rounded-xl border border-white/5 h-full flex flex-col justify-between">
        <span className="font-orbitron font-extrabold text-xs tracking-widest text-slate-400 uppercase mb-1">
          Factor Breakdown
        </span>
        <div className="space-y-2 flex-grow overflow-y-auto max-h-[160px] pr-1">
          {Object.entries(factorScores).map(([key, score]) => {
            const label = keyToLabel[key] || key;
            const barColor = keyToColor[key] || 'bg-teal-500';
            return (
              <div key={key} className="space-y-0.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-medium">{label}</span>
                  <span className="font-orbitron font-bold text-slate-400">{score.toFixed(0)}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden border border-white/5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${score}%` }}
                    transition={{ duration: 1.2, ease: 'easeOut' }}
                    className={`h-full rounded-full ${barColor}`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
