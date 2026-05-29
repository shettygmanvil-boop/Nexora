"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Activity } from 'lucide-react';

import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { TripForm } from './components/TripForm';
import { RecommendationCard } from './components/RecommendationCard';

import { 
  ApiService, GroupTripRequest, TravelGroupRequest, 
  RecommendationDetails, CrewRecommendationResponse 
} from './services/api';

const agentsList = [
  { name: 'Group Preference Agent', desc: 'Analyzes individual vibes, foods, and activity constraints to determine optimal group parameters.', type: 'Sequential Core', status: 'Idle' },
  { name: 'Smart Budget Optimizer', desc: 'Splits group budget into lodging (45%), sightseeing/activities (35%), and emergency reserves (10%).', type: 'Numeric Engine', status: 'Idle' },
  { name: 'Weather & Safety Advisor', desc: 'Evaluates destination climate forecasts and flags medical triggers (e.g. asthma in cold, hypertension in heat).', type: 'Alert Scanner', status: 'Idle' },
  { name: 'Accommodation Specialist', desc: 'Matches hotel parameters against group sizes, budget limits, and luxury preferences.', type: 'Parser Core', status: 'Idle' },
  { name: 'Itinerary Orchestrator', desc: 'Designs daily activities, balancing travel fatigue index ratings and local interest tags.', type: 'Planner Core', status: 'Idle' },
  { name: 'Conflict Resolution Guard', desc: 'Resolves clashing styles by dynamically creating split solo itineraries and common evening reunions.', type: 'Heuristic Node', status: 'Idle' },
  { name: 'Expectation Match Inspector', desc: 'Scores verbal user expectations and priorities against destination attributes to calculate reality check sync rates.', type: 'Semantic Analyzer', status: 'Idle' }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [loading, setLoading] = useState<boolean>(false);
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [submitMode, setSubmitMode] = useState<'fast' | 'crew'>('fast');
  const [fastResult, setFastResult] = useState<RecommendationDetails[] | undefined>(undefined);
  const [crewResult, setCrewResult] = useState<CrewRecommendationResponse | undefined>(undefined);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleFormSubmit = async (data: {
    mode: 'fast' | 'crew';
    fastData: GroupTripRequest;
    crewData: TravelGroupRequest;
  }) => {
    setLoading(true);
    setErrorMessage('');
    setSubmitMode(data.mode);

    try {
      if (data.mode === 'fast') {
        const response = await ApiService.getFastRecommendations(data.fastData);
        setFastResult(response);
      } else {
        const response = await ApiService.getCrewRecommendations(data.crewData);
        setCrewResult(response);
      }
      setSubmitted(true);
    } catch (e: any) {
      console.error(e);
      const detail = e.response?.data?.detail || e.message || 'API request failed';
      setErrorMessage(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSubmitted(false);
    setFastResult(undefined);
    setCrewResult(undefined);
    setErrorMessage('');
  };

  return (
    <div className="relative min-h-screen bg-[#030712] text-slate-100 font-sans pb-10 selection:bg-teal-500/30 selection:text-teal-300">
      {/* Glow Backdrops */}
      <div className="fixed inset-0 cyber-grid opacity-30 pointer-events-none z-0"></div>
      <div className="fixed top-0 left-0 w-full h-[500px] bg-gradient-to-b from-indigo-950/10 via-transparent to-transparent pointer-events-none z-0"></div>
      
      {/* Scanner Scan Beam Effect */}
      <div className="fixed top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-teal-500/25 to-transparent animate-scan pointer-events-none z-10"></div>

      {/* Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="relative z-10">
        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard-view"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.4 }}
            >
              {!submitted ? (
                <>
                  <HeroSection />
                  
                  {/* API Connection Error Message */}
                  {errorMessage && (
                    <div className="max-w-2xl mx-auto px-4 mb-6">
                      <div className="p-4 bg-rose-500/10 border border-rose-500/35 text-rose-300 rounded-xl flex items-center gap-3 text-sm">
                        <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping"></span>
                        <div className="flex-grow">
                          <span className="font-orbitron font-extrabold uppercase text-[10px] tracking-wider block mb-0.5">
                            Routing Error
                          </span>
                          <span className="font-medium text-xs md:text-sm">{errorMessage}</span>
                        </div>
                        <button 
                          onClick={() => setErrorMessage('')}
                          className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-xs font-semibold"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  )}

                  <TripForm onSubmit={handleFormSubmit} loading={loading} />
                </>
              ) : (
                <div className="pt-28">
                  {/* Results Sub-Navbar controls */}
                  <div className="max-w-4xl mx-auto px-4 flex items-center justify-between mb-8">
                    <button
                      onClick={handleReset}
                      className="flex items-center gap-2 px-4 py-2 border border-white/10 hover:border-white/20 bg-slate-900/60 rounded-xl text-xs font-orbitron font-bold uppercase tracking-wider text-slate-300 hover:text-slate-100 transition-all duration-300 shadow-md"
                    >
                      <ArrowLeft className="w-4 h-4 text-teal-400" />
                      Configure Planner
                    </button>

                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950 border border-white/5 text-[10px] font-orbitron font-extrabold text-slate-400 uppercase tracking-widest">
                      <Activity className="w-3.5 h-3.5 text-teal-400" />
                      Mode: {submitMode === 'fast' ? 'Fast Rank Engine' : 'CrewAI Orchestrated'}
                    </div>
                  </div>

                  <RecommendationCard
                    mode={submitMode}
                    fastResult={fastResult}
                    crewResult={crewResult}
                  />
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'agents' && (
            <motion.div
              key="agents-view"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.4 }}
              className="pt-32 max-w-4xl mx-auto px-4"
            >
              <div className="flex flex-col items-center text-center mb-10">
                <span className="font-orbitron font-extrabold text-xs tracking-widest text-teal-400 bg-teal-500/10 border border-teal-500/20 px-3.py-1 rounded-full mb-3 py-1 px-3">
                  System Diagnostics
                </span>
                <h2 className="font-orbitron font-black text-2xl md:text-3xl text-slate-100 uppercase">
                  Maproom Multi-Agent Core
                </h2>
                <p className="text-xs text-slate-400 max-w-sm mt-2 leading-relaxed">
                  Explore the 7 specialized AI Agents that sequentialize parameters to resolve conflict clusters.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agentsList.map((agent, i) => (
                  <div key={i} className="glass-panel p-5 rounded-xl border border-white/5 flex flex-col justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-orbitron font-black text-xs text-slate-200 tracking-wide">
                          {agent.name}
                        </span>
                        <span className="text-[8px] font-extrabold uppercase tracking-widest px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/25 text-indigo-400">
                          {agent.type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed font-sans">
                        {agent.desc}
                      </p>
                    </div>

                    <div className="flex items-center justify-between border-t border-white/5 pt-3 text-[10px]">
                      <span className="text-slate-500 font-semibold uppercase tracking-wider">
                        Diagnostics Status
                      </span>
                      <span className="flex items-center gap-1 text-teal-400 font-bold uppercase tracking-wider">
                        <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-ping"></span>
                        {agent.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'docs' && (
            <motion.div
              key="docs-view"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.4 }}
              className="pt-32 max-w-4xl mx-auto px-4 space-y-6"
            >
              <div className="flex flex-col items-center text-center mb-8">
                <span className="font-orbitron font-extrabold text-xs tracking-widest text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-3.py-1 rounded-full mb-3 py-1 px-3">
                  Developer Specifications
                </span>
                <h2 className="font-orbitron font-black text-2xl md:text-3xl text-slate-100 uppercase">
                  API Routing Framework
                </h2>
                <p className="text-xs text-slate-400 max-w-sm mt-2 leading-relaxed">
                  Review the expected payloads and structures mapping the React frontend to the FastAPI backend.
                </p>
              </div>

              <div className="glass-panel p-6 rounded-xl border border-white/5 space-y-4">
                <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                  <span className="px-2 py-0.5 rounded bg-teal-500 text-slate-950 font-orbitron font-black text-[10px] tracking-wider uppercase">
                    POST
                  </span>
                  <span className="font-mono text-xs text-slate-300 font-semibold">
                    /recommend
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  The Fast Recommendation Engine endpoint analyzes traveler profiles and evaluates compatibility matrix weights across all destinations.
                </p>
                <div className="bg-slate-950 rounded-lg p-4 border border-white/5 font-mono text-xs text-slate-300 overflow-x-auto">
                  <span className="text-indigo-400 font-semibold block mb-2">// GroupTripRequest Payload Structure:</span>
                  {`{
  "travelers": [
    {
      "name": "Jane Doe",
      "age": 29,
      "food_preference": "veg",
      "mood": "adventurous",
      "travel_purpose": "leisure",
      "medical_conditions": ["asthma"],
      "activity_level": "high",
      "budget_preference": "standard"
    }
  ],
  "budget": 50000.0,
  "days": 4,
  "preferred_vibe": "beaches",
  "priorities": ["relaxation", "sightseeing"],
  "destination_preference": null,
  "expectations": "I want a relaxing beach getaway with beautiful sunset views."
}`}
                </div>
              </div>

              <div className="glass-panel p-6 rounded-xl border border-white/5 space-y-4">
                <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                  <span className="px-2 py-0.5 rounded bg-indigo-500 text-indigo-100 border border-indigo-400/20 font-orbitron font-black text-[10px] tracking-wider uppercase">
                    POST
                  </span>
                  <span className="font-mono text-xs text-slate-300 font-semibold">
                    /recommendation/
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  Triggers the CrewAI agent orchestration flow to construct deep group-solo hybrid itineraries.
                </p>
                <div className="bg-slate-950 rounded-lg p-4 border border-white/5 font-mono text-xs text-slate-300 overflow-x-auto">
                  <span className="text-indigo-400 font-semibold block mb-2">// TravelGroupRequest Payload Structure:</span>
                  {`{
  "travelers": [
    {
      "name": "Jane Doe",
      "age": 29,
      "medical_conditions": ["asthma"],
      "vibe_preference": "beaches",
      "accommodation_preference": "standard",
      "travel_style": "relaxation",
      "travel_purpose": "leisure"
    }
  ],
  "total_budget": 50000.0,
  "num_days": 4,
  "expectations": "I want a relaxing beach getaway with beautiful sunset views."
}`}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
