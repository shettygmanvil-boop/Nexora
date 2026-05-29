import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { 
  MapPin, Clock, DollarSign, Activity, AlertTriangle, 
  ChevronDown, ChevronUp, Star, Lightbulb, Users, Compass, BookOpen 
} from 'lucide-react';
import { RecommendationDetails, CrewRecommendationResponse } from '../services/api';
import { ScoreBar } from './ScoreBar';
import { WarningBadge } from './WarningBadge';

interface RecommendationCardProps {
  fastResult?: RecommendationDetails[];
  crewResult?: CrewRecommendationResponse;
  mode: 'fast' | 'crew';
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  fastResult,
  crewResult,
  mode,
}) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0); // Expand first by default
  const [itineraryTab, setItineraryTab] = useState<'group' | 'solo' | 'reunion'>('group');
  const [selectedSoloMember, setSelectedSoloMember] = useState<string>('');

  if (mode === 'fast' && fastResult) {
    if (fastResult.length === 0) return null;

    return (
      <div className="max-w-4xl mx-auto space-y-6 px-4 pb-20">
        <div className="flex flex-col items-center text-center mb-8">
          <span className="font-orbitron font-extrabold text-xs tracking-widest text-teal-400 uppercase bg-teal-500/10 border border-teal-500/20 px-3 py-1 rounded-full mb-3">
            Ranked Recommendations
          </span>
          <h2 className="font-orbitron font-black text-2xl md:text-3xl text-slate-100 uppercase">
            Synthesized Destination Ranks
          </h2>
          <p className="text-xs text-slate-400 max-w-sm mt-2 leading-relaxed">
            The Fast Routing matrix resolved compatibility across all 4 hub destinations. Click a destination to view full metrics.
          </p>
        </div>

        {fastResult.map((rec, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div
              key={rec.destination}
              className={`glass-panel rounded-2xl border transition-all duration-500 overflow-hidden ${
                isExpanded 
                  ? 'border-teal-500/40 shadow-[0_0_25px_rgba(20,184,166,0.12)]' 
                  : 'border-white/5 shadow-md hover:border-white/10'
              }`}
            >
              {/* Header summary row (clickable) */}
              <button
                type="button"
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className="w-full text-left p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 focus:outline-none"
              >
                <div className="flex items-center gap-4">
                  {/* Rank circle */}
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-orbitron font-black border text-sm ${
                    idx === 0 
                      ? 'bg-teal-500/15 border-teal-500 text-teal-300 shadow-[0_0_10px_rgba(20,184,166,0.2)]'
                      : 'bg-slate-900 border-white/10 text-slate-400'
                  }`}>
                    #{idx + 1}
                  </div>
                  <div>
                    <h3 className="font-orbitron font-black text-lg md:text-xl text-slate-200 tracking-wide flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-teal-400" />
                      {rec.destination}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-lg truncate leading-relaxed">
                      {rec.reasons[0] || 'Top matching destination matching preferred vibes.'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 justify-between md:justify-end">
                  {/* Compatibility Score Pill */}
                  <div className="flex flex-col items-end">
                    <span className="font-orbitron font-black text-xl text-teal-400 text-glow-teal">
                      {rec.compatibility_score.toFixed(0)}%
                    </span>
                    <span className="text-[9px] text-slate-400 font-extrabold uppercase tracking-widest -mt-0.5">
                      Sync rate
                    </span>
                  </div>

                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-slate-500" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-slate-500" />
                  )}
                </div>
              </button>

              {/* Collapsed detailed panel */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: 'auto' }}
                    exit={{ height: 0 }}
                    transition={{ duration: 0.4, ease: 'easeInOut' }}
                    className="border-t border-white/5"
                  >
                    <div className="p-6 space-y-6">
                      {/* Visual Dashboard row (Radial gauge, radar chart, factor bars) */}
                      <ScoreBar
                        compatibilityScore={rec.compatibility_score}
                        factorScores={rec.factor_scores}
                      />

                      {/* Reasons & Activities Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-white/5">
                        {/* Reasons */}
                        <div className="space-y-3">
                          <h4 className="font-orbitron font-extrabold text-xs tracking-widest text-slate-400 uppercase flex items-center gap-2">
                            <Star className="w-4 h-4 text-teal-400" />
                            AI Recommendation Logic
                          </h4>
                          <ul className="space-y-2">
                            {rec.reasons.map((reason, i) => (
                              <li key={i} className="text-xs text-slate-300 flex items-start gap-2 leading-relaxed">
                                <span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0"></span>
                                {reason}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Top Attractions */}
                        <div className="space-y-3">
                          <h4 className="font-orbitron font-extrabold text-xs tracking-widest text-slate-400 uppercase flex items-center gap-2">
                            <Compass className="w-4 h-4 text-indigo-400" />
                            Top Activities & Attractions
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {rec.top_activities.map((act, i) => (
                              <span
                                key={i}
                                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-white/5 text-xs text-slate-300 font-medium"
                              >
                                {act}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Expectation Match Row */}
                      <div className="p-4 bg-slate-950/60 border border-white/5 rounded-xl flex flex-col md:flex-row md:items-center gap-4">
                        <div className="flex-shrink-0 flex flex-col items-center justify-center p-3.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-lg w-20">
                          <span className="font-orbitron font-black text-lg">
                            {rec.expectation_match.match_percentage.toFixed(0)}%
                          </span>
                          <span className="text-[8px] font-extrabold uppercase tracking-widest text-center mt-0.5 leading-none">
                            Match
                          </span>
                        </div>
                        <div className="space-y-1">
                          <h5 className="font-orbitron font-extrabold text-[10px] tracking-widest text-slate-400 uppercase">
                            Reality Check vs Expectations
                          </h5>
                          <p className="text-xs text-slate-300 leading-relaxed font-sans">
                            {rec.expectation_match.summary}
                          </p>
                        </div>
                      </div>

                      {/* Explainable AI narrative paragraph */}
                      <div className="p-4 bg-teal-950/10 border border-teal-500/10 text-teal-200/90 rounded-xl space-y-1.5">
                        <h5 className="font-orbitron font-extrabold text-[10px] tracking-widest text-teal-400 uppercase flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5" />
                          Orchestration Logic Breakdown
                        </h5>
                        <p className="text-xs leading-relaxed font-sans font-medium">
                          {rec.score_explanation}
                        </p>
                      </div>

                      {/* Explore Experiences Button */}
                      <div className="pt-2">
                        <Link
                          href={`/activities/${rec.destination}`}
                          className="w-full text-center py-2.5 bg-gradient-to-r from-teal-500/10 to-indigo-500/10 hover:from-teal-500/25 hover:to-indigo-500/25 border border-teal-500/30 hover:border-teal-500/50 text-teal-300 hover:text-teal-200 rounded-xl text-xs font-orbitron font-extrabold uppercase tracking-wider transition-all duration-300 shadow-md flex items-center justify-center gap-2 cursor-pointer"
                        >
                          <Compass className="w-4 h-4 text-teal-400" />
                          Explore Experiences in {rec.destination}
                        </Link>
                      </div>

                      {/* Health / Environmental Warning Panels */}
                      <div className="space-y-2 pt-2">
                        <h4 className="font-orbitron font-extrabold text-xs tracking-widest text-slate-400 uppercase">
                          System Warning Checks
                        </h4>
                        <div className="grid grid-cols-1 gap-2">
                          {rec.warnings.map((w, i) => (
                            <WarningBadge key={i} warning={w} />
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    );
  }

  if (mode === 'crew' && crewResult) {
    const defaultSoloMember = Object.keys(crewResult.solo_itineraries)[0] || '';
    if (selectedSoloMember === '' && defaultSoloMember !== '') {
      setSelectedSoloMember(defaultSoloMember);
    }

    return (
      <div className="max-w-4xl mx-auto px-4 pb-20 space-y-8">
        {/* Destination Header card */}
        <div className="glass-panel p-6 md:p-8 rounded-2xl border border-teal-500/30 relative overflow-hidden shadow-2xl">
          {/* Top subtle glow */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-teal-500/10 to-indigo-500/10 blur-3xl pointer-events-none"></div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10 border-b border-white/5 pb-6 mb-6">
            <div className="space-y-2">
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-xs font-semibold text-teal-300 uppercase tracking-widest">
                <MapPin className="w-3.5 h-3.5" />
                Recommended Destination
              </span>
              <h2 className="font-orbitron font-black text-3xl md:text-4xl text-slate-100 tracking-wider">
                {crewResult.destination_name}
              </h2>
              <p className="text-xs md:text-sm text-slate-300 max-w-xl leading-relaxed">
                {crewResult.description}
              </p>
              <div className="pt-2">
                <Link
                  href={`/activities/${crewResult.destination_name}`}
                  className="inline-flex items-center gap-2 px-4 py-2 border border-teal-500/30 hover:border-teal-500/50 bg-teal-500/10 hover:bg-teal-500/20 rounded-xl text-xs font-orbitron font-bold uppercase tracking-wider text-teal-300 hover:text-teal-200 transition-all duration-300 shadow-md cursor-pointer"
                >
                  <Compass className="w-4 h-4 text-teal-400" />
                  Explore Experiences
                </Link>
              </div>
            </div>

            <div className="flex items-center gap-4 bg-slate-950/80 border border-white/5 p-4 rounded-xl">
              <div className="text-center border-r border-white/5 pr-4">
                <span className="font-orbitron font-black text-3xl text-teal-400 text-glow-teal">
                  {crewResult.group_compatibility_score.toFixed(0)}%
                </span>
                <span className="text-[9px] text-slate-400 font-extrabold uppercase tracking-widest block">
                  Group Sync
                </span>
              </div>
              <div className="text-center pl-1">
                <span className="font-orbitron font-black text-3xl text-indigo-400 text-glow-indigo">
                  {crewResult.expectation_reality_match.score.toFixed(0)}%
                </span>
                <span className="text-[9px] text-slate-400 font-extrabold uppercase tracking-widest block">
                  Reality Match
                </span>
              </div>
            </div>
          </div>

          {/* Explainable AI block */}
          <div className="space-y-4 relative z-10">
            <div className="p-4 bg-indigo-950/10 border border-indigo-500/10 text-indigo-200/90 rounded-xl space-y-1.5">
              <h5 className="font-orbitron font-extrabold text-[10px] tracking-widest text-indigo-400 uppercase flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5" />
                Crew orchestrator summary
              </h5>
              <p className="text-xs leading-relaxed font-sans font-medium">
                {crewResult.conflict_resolution_summary}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {crewResult.explainable_ai_reasons.map((r, i) => (
                <div key={i} className="flex items-start gap-2.5 text-xs text-slate-300 bg-slate-950/40 p-3 rounded-lg border border-white/5">
                  <Lightbulb className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                  <span>{r}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Dashboard Itinerary Stepper Panels */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-white/5 pb-2">
            <h3 className="font-orbitron font-extrabold text-sm text-slate-300 tracking-wider">
              HYBRID ITINERARY SCHEDULER
            </h3>
            <div className="flex items-center gap-1.5 bg-slate-900/80 p-0.5 rounded-lg border border-white/5">
              {[
                { id: 'group', label: 'Group Track' },
                { id: 'solo', label: 'Solo Tracks' },
                { id: 'reunion', label: 'Evening Reunions' }
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setItineraryTab(t.id as any)}
                  className={`px-3 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider transition-all duration-300 ${
                    itineraryTab === t.id
                      ? 'bg-teal-500/10 text-teal-300 border border-teal-500/20 shadow-[0_0_10px_rgba(20,184,166,0.1)]'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Active Schedule Output */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5">
            {/* If Solo, render member toggle */}
            {itineraryTab === 'solo' && (
              <div className="flex items-center gap-3 border-b border-white/5 pb-4 mb-4">
                <span className="text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400">
                  Select Traveler Solo Schedule:
                </span>
                <select
                  value={selectedSoloMember}
                  onChange={(e) => setSelectedSoloMember(e.target.value)}
                  className="bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300"
                >
                  {Object.keys(crewResult.solo_itineraries).map((m) => (
                    <option key={m} value={m}>
                      {m}'s Track
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* List Schedule Days */}
            <div className="space-y-6">
              {(() => {
                let activeItinerary = crewResult.group_itinerary;
                if (itineraryTab === 'solo') {
                  activeItinerary = crewResult.solo_itineraries[selectedSoloMember] || [];
                } else if (itineraryTab === 'reunion') {
                  activeItinerary = crewResult.reunion_schedule;
                }

                if (activeItinerary.length === 0) {
                  return (
                    <div className="text-center py-10 text-slate-500 text-sm">
                      No activities scheduled for this track.
                    </div>
                  );
                }

                return activeItinerary.map((day) => (
                  <div key={day.day} className="relative pl-6 md:pl-10 border-l border-white/5">
                    {/* Day indicator */}
                    <div className="absolute top-0 -left-4.5 md:-left-5.5 w-9 h-9 rounded-full bg-slate-900 border border-white/10 flex items-center justify-center font-orbitron font-extrabold text-[10px] text-teal-400 shadow-md">
                      D{day.day}
                    </div>

                    <div className="space-y-4 pb-4">
                      <h4 className="font-orbitron font-extrabold text-xs text-slate-300 uppercase tracking-widest mb-3 pt-2">
                        Day {day.day} Schedule
                      </h4>

                      <div className="grid grid-cols-1 gap-4">
                        {day.activities.map((act, aIdx) => (
                          <div
                            key={aIdx}
                            className="bg-slate-950/40 p-4 rounded-xl border border-white/5 flex flex-col md:flex-row md:items-start justify-between gap-4 hover:border-white/10 transition-all duration-300"
                          >
                            <div className="space-y-2 flex-grow">
                              <div className="flex items-center gap-2">
                                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-[9px] font-orbitron font-bold uppercase tracking-widest text-indigo-400">
                                  <Clock className="w-3 h-3" />
                                  {act.time}
                                </span>
                                <h5 className="font-sans font-bold text-slate-200">
                                  {act.activity_name}
                                </h5>
                              </div>
                              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                                {act.description}
                              </p>
                              <div className="flex flex-wrap items-center gap-4 text-[10px] text-slate-400">
                                <span className="flex items-center gap-1">
                                  <Users className="w-3.5 h-3.5 text-slate-500" />
                                  Assigned to: {act.assigned_to.join(', ')}
                                </span>
                                <span className="flex items-center gap-1">
                                  <Activity className="w-3.5 h-3.5 text-amber-500" />
                                  Fatigue: {act.fatigue_level}/5
                                </span>
                              </div>
                            </div>

                            <div className="flex-shrink-0 font-orbitron font-black text-sm text-teal-400 flex items-center gap-0.5 bg-teal-500/5 px-3 py-1.5 rounded-lg border border-teal-500/15">
                              <DollarSign className="w-3.5 h-3.5" />
                              {act.estimated_cost.toFixed(0)} INR
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ));
              })()}
            </div>
          </div>
        </div>

        {/* Budget ledger, Warnings & Suggestions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Budget Analysis Ledger */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
            <h3 className="font-orbitron font-extrabold text-sm text-slate-300 tracking-wider flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-teal-400" />
              BUDGET LEDGER
            </h3>

            <div className="space-y-3">
              {[
                { label: 'Lodging Allocation', val: crewResult.budget_analysis.accommodation_cost },
                { label: 'Activities Allocation', val: crewResult.budget_analysis.activities_cost },
                { label: 'Emergency Buffer (10%)', val: crewResult.budget_analysis.buffer_amount },
                { label: 'Remaining Balance', val: crewResult.budget_analysis.remaining_balance }
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs border-b border-white/5 pb-2">
                  <span className="text-slate-400 font-medium">{item.label}</span>
                  <span className="font-orbitron font-bold text-slate-200">₹{item.val.toLocaleString()}</span>
                </div>
              ))}
            </div>

            <p className="text-xs text-slate-400 leading-relaxed font-sans pt-1">
              {crewResult.budget_analysis.explanation}
            </p>
          </div>

          {/* Safety & Environment Alerts */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
            <h3 className="font-orbitron font-extrabold text-sm text-slate-300 tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              SAFETY & CLIMATE
            </h3>

            <div className="p-3 bg-slate-900 border border-white/5 rounded-xl space-y-1">
              <span className="text-[9px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400">
                General Condition
              </span>
              <p className="text-xs text-slate-300 font-semibold">{crewResult.weather_health_safety.general_condition}</p>
            </div>

            <div className="space-y-2">
              {crewResult.weather_health_safety.health_warnings.map((w, i) => (
                <WarningBadge key={i} warning={w} />
              ))}
            </div>

            {crewResult.weather_health_safety.alternative_indoor_activities.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[9px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400">
                  Alternative Backup Activities
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {crewResult.weather_health_safety.alternative_indoor_activities.map((act, i) => (
                    <span key={i} className="text-[10px] bg-slate-950/80 border border-white/5 px-2.5 py-1 rounded text-slate-300">
                      {act}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Smart budget extensions (Upsell tips) */}
        {crewResult.smart_budget_expansions.length > 0 && (
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-3">
            <h3 className="font-orbitron font-extrabold text-sm text-slate-300 tracking-wider flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              SMART BUDGET EXPANSIOM RECOMMENDATIONS
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {crewResult.smart_budget_expansions.map((tip, i) => (
                <div key={i} className="bg-indigo-500/5 border border-indigo-500/15 p-3 rounded-lg text-xs text-slate-300 leading-relaxed">
                  {tip}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
};
