import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowRight, ArrowLeft, Users, Settings, Plus, Sparkles, CheckCircle2, AlertCircle 
} from 'lucide-react';
import { TravelerFormVal, TravelerCard } from './TravelerCard';
import { GroupTripRequest, TravelGroupRequest } from '../services/api';

interface TripFormProps {
  onSubmit: (data: { mode: 'fast' | 'crew'; fastData: GroupTripRequest; crewData: TravelGroupRequest }) => void;
  loading: boolean;
}

const initialTraveler = (): TravelerFormVal => ({
  name: '',
  age: 25,
  food_preference: 'veg',
  mood: 'excited',
  travel_purpose: 'leisure',
  medical_conditions: [],
  activity_level: 'medium',
  budget_preference: 'standard',
  accommodation_preference: 'standard',
  travel_style: 'relaxation',
});

const prioritiesOptions = ['relaxation', 'sightseeing', 'party', 'food', 'adventure', 'culture', 'nature'];
const vibesOptions = ['beaches', 'mountains', 'nightlife', 'heritage', 'cafes', 'spirituality', 'nature'];

export const TripForm: React.FC<TripFormProps> = ({ onSubmit, loading }) => {
  const [step, setStep] = useState<number>(1);
  const [mode, setMode] = useState<'fast' | 'crew'>('fast');
  
  // Group Constraints State
  const [budget, setBudget] = useState<number>(50000);
  const [days, setDays] = useState<number>(4);
  const [preferredVibe, setPreferredVibe] = useState<string>('beaches');
  const [priorities, setPriorities] = useState<string[]>(['relaxation', 'sightseeing']);
  const [expectations, setExpectations] = useState<string>('I want a relaxing beach getaway with beautiful sunset views.');
  const [destPref, setDestPref] = useState<string>('');

  // Travelers State
  const [travelers, setTravelers] = useState<TravelerFormVal[]>([initialTraveler()]);

  // Priority toggler
  const togglePriority = (prio: string) => {
    if (priorities.includes(prio)) {
      setPriorities(priorities.filter((p) => p !== prio));
    } else {
      setPriorities([...priorities, prio]);
    }
  };

  // Add Traveler
  const addTraveler = () => {
    setTravelers([...travelers, initialTraveler()]);
  };

  // Remove Traveler
  const removeTraveler = (index: number) => {
    setTravelers(travelers.filter((_, idx) => idx !== index));
  };

  // Update single Traveler
  const handleTravelerChange = (index: number, updated: TravelerFormVal) => {
    const list = [...travelers];
    list[index] = updated;
    setTravelers(list);
  };

  // Validation
  const validateStep = (currentStep: number): boolean => {
    if (currentStep === 1) {
      if (budget <= 0) return false;
      if (days <= 0) return false;
      if (!preferredVibe) return false;
      if (priorities.length === 0) return false;
      return true;
    }
    if (currentStep === 2) {
      // Ensure all travelers have non-empty names and valid ages
      return travelers.every((t) => t.name.trim().length > 0 && t.age >= 0 && t.age <= 120);
    }
    return true;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep((prev) => prev + 1);
    } else {
      alert('Please fill out all required fields before proceeding.');
    }
  };

  const handlePrev = () => {
    setStep((prev) => Math.max(1, prev - 1));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateStep(1) || !validateStep(2)) {
      alert('Form is invalid. Please double check inputs.');
      return;
    }

    // Format requests
    const fastRequest: GroupTripRequest = {
      travelers: travelers.map((t) => ({
        name: t.name,
        age: t.age,
        food_preference: t.food_preference,
        mood: t.mood,
        travel_purpose: t.travel_purpose,
        medical_conditions: t.medical_conditions,
        activity_level: t.activity_level,
        budget_preference: t.budget_preference,
      })),
      budget: budget,
      days: days,
      preferred_vibe: preferredVibe,
      priorities: priorities,
      destination_preference: destPref || null,
      expectations: expectations,
    };

    const crewRequest: TravelGroupRequest = {
      travelers: travelers.map((t) => ({
        name: t.name,
        age: t.age,
        medical_conditions: t.medical_conditions,
        vibe_preference: preferredVibe,
        accommodation_preference: t.accommodation_preference,
        travel_style: t.travel_style,
        travel_purpose: t.travel_purpose,
      })),
      total_budget: budget,
      num_days: days,
      expectations: expectations,
      destination_preference: destPref || null,
    };

    onSubmit({
      mode,
      fastData: fastRequest,
      crewData: crewRequest,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mx-auto px-4 pb-16">
      {/* Stepper Header */}
      <div className="flex items-center justify-between mb-8 max-w-md mx-auto">
        {[
          { num: 1, label: 'Constraints', icon: Settings },
          { num: 2, label: 'Travelers', icon: Users },
          { num: 3, label: 'Engage AI', icon: Sparkles }
        ].map((s) => {
          const Icon = s.icon;
          const isCompleted = step > s.num;
          const isActive = step === s.num;
          return (
            <div key={s.num} className="flex flex-col items-center gap-1.5 relative flex-1">
              <div className={`relative z-10 w-9 h-9 rounded-full flex items-center justify-center border font-orbitron font-extrabold text-xs transition-all duration-500 ${
                isCompleted
                  ? 'bg-teal-500/20 border-teal-500 text-teal-400 shadow-[0_0_15px_rgba(20,184,166,0.25)]'
                  : isActive
                  ? 'bg-indigo-500/20 border-indigo-500 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.25)]'
                  : 'bg-slate-900 border-white/5 text-slate-500'
              }`}>
                {isCompleted ? <CheckCircle2 className="w-5 h-5 text-teal-400" /> : <Icon className="w-4 h-4" />}
              </div>
              <span className={`text-[10px] font-orbitron font-extrabold uppercase tracking-wider text-center ${
                isActive ? 'text-indigo-400' : isCompleted ? 'text-teal-400' : 'text-slate-500'
              }`}>
                {s.label}
              </span>
              {/* Connector line */}
              {s.num < 3 && (
                <div className={`absolute top-4.5 left-[calc(50%+18px)] right-[calc(-50%+18px)] h-[1px] -z-0 transition-colors duration-500 ${
                  step > s.num ? 'bg-teal-500/50' : 'bg-white/5'
                }`}></div>
              )}
            </div>
          );
        })}
      </div>

      {/* Steps Content */}
      <div className="min-h-[350px]">
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step-1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="glass-panel p-6 rounded-xl border border-white/5 space-y-6">
                <h2 className="font-orbitron font-extrabold text-lg tracking-wider text-slate-200 border-b border-white/5 pb-3">
                  GROUP TRIP PARAMETERS
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Budget */}
                  <div>
                    <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
                      Total Combined Budget (INR)
                    </label>
                    <input
                      type="number"
                      required
                      min="1"
                      value={budget}
                      onChange={(e) => setBudget(parseFloat(e.target.value) || 0)}
                      placeholder="e.g. 50000"
                      className="w-full bg-slate-950/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50 focus:shadow-[0_0_10px_rgba(99,102,241,0.15)] transition-all duration-300"
                    />
                    <span className="text-[10px] text-slate-500 mt-1 block">
                      Total budget allocated for lodging, travel, food, and activities.
                    </span>
                  </div>

                  {/* Days */}
                  <div>
                    <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
                      Trip Duration (Days)
                    </label>
                    <input
                      type="number"
                      required
                      min="1"
                      max="30"
                      value={days}
                      onChange={(e) => setDays(parseInt(e.target.value) || 0)}
                      placeholder="e.g. 4"
                      className="w-full bg-slate-950/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50 focus:shadow-[0_0_10px_rgba(99,102,241,0.15)] transition-all duration-300"
                    />
                  </div>

                  {/* Preferred Vibe */}
                  <div>
                    <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
                      Primary Destination Vibe
                    </label>
                    <select
                      value={preferredVibe}
                      onChange={(e) => setPreferredVibe(e.target.value)}
                      className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50 transition-all duration-300 capitalize"
                    >
                      {vibesOptions.map((v) => (
                        <option key={v} value={v}>
                          {v}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Optional Destination Preference */}
                  <div>
                    <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
                      Specific Destination Preference (Optional)
                    </label>
                    <select
                      value={destPref}
                      onChange={(e) => setDestPref(e.target.value)}
                      className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50 transition-all duration-300"
                    >
                      <option value="">Decide for me (Auto-analyze all hubs)</option>
                      <option value="Goa">Goa (Beaches & Nightlife)</option>
                      <option value="Srinagar">Srinagar (Scenic Mountains & Cold Climate)</option>
                      <option value="Jaipur">Jaipur (Royal Heritage & Temples)</option>
                      <option value="Bangalore">Bangalore (Tech, Cafes & Urban Nightlife)</option>
                    </select>
                  </div>
                </div>

                {/* Group Priorities */}
                <div>
                  <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-2">
                    Group Priorities (Select at least one)
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {prioritiesOptions.map((prio) => {
                      const selected = priorities.includes(prio);
                      return (
                        <button
                          key={prio}
                          type="button"
                          onClick={() => togglePriority(prio)}
                          className={`px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider transition-all duration-300 ${
                            selected
                              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-[0_0_10px_rgba(99,102,241,0.15)]'
                              : 'bg-slate-950/60 text-slate-400 border border-white/5 hover:border-white/15'
                          }`}
                        >
                          {prio}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Expectations Textarea */}
                <div>
                  <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
                    Written Desires & Expectations
                  </label>
                  <textarea
                    rows={3}
                    value={expectations}
                    onChange={(e) => setExpectations(e.target.value)}
                    placeholder="e.g. I want a peaceful trip near lakes with scenic sunset views. Avoid heavily crowded weekend paths if possible..."
                    className="w-full bg-slate-950/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/50 focus:shadow-[0_0_10px_rgba(99,102,241,0.15)] transition-all duration-300 placeholder:text-slate-600 resize-none"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step-2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-orbitron font-extrabold text-lg text-slate-200 tracking-wider">
                    TRAVELER PROFILES
                  </h2>
                  <p className="text-xs text-slate-400">Configure parameters for each traveler to run compatibility checks.</p>
                </div>
                <button
                  type="button"
                  onClick={addTraveler}
                  className="flex items-center gap-1.5 px-4 py-2 bg-teal-500/10 border border-teal-500/20 text-teal-400 rounded-lg text-xs font-orbitron font-bold uppercase tracking-wider hover:bg-teal-500/20 transition-all duration-300 shadow-[0_0_15px_rgba(20,184,166,0.08)]"
                >
                  <Plus className="w-4 h-4" />
                  Add Traveler
                </button>
              </div>

              {/* Dynamic Traveler list */}
              <div className="space-y-6">
                <AnimatePresence initial={false}>
                  {travelers.map((traveler, idx) => (
                    <TravelerCard
                      key={idx}
                      index={idx}
                      traveler={traveler}
                      onChange={handleTravelerChange}
                      onRemove={removeTraveler}
                      canRemove={travelers.length > 1}
                    />
                  ))}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step-3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="glass-panel p-6 rounded-xl border border-white/5 text-center space-y-6 max-w-xl mx-auto">
                <div className="w-16 h-16 rounded-full bg-teal-500/10 border border-teal-500/30 flex items-center justify-center mx-auto text-teal-400 shadow-[0_0_20px_rgba(20,184,166,0.15)] animate-bounce">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="font-orbitron font-extrabold text-xl text-slate-200 tracking-wider mb-2">
                    ENGAGE AI ORCHESTRATOR
                  </h2>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                    Select your AI planning routing configuration and launch the agents to compile travel profiles.
                  </p>
                </div>

                {/* Mode Select Tabs */}
                <div className="grid grid-cols-2 gap-3 p-1 bg-slate-950 border border-white/5 rounded-xl">
                  {/* Mode Fast */}
                  <button
                    type="button"
                    onClick={() => setMode('fast')}
                    className={`p-4 rounded-lg flex flex-col items-center justify-center gap-1.5 transition-all duration-300 border text-center ${
                      mode === 'fast'
                        ? 'bg-teal-500/10 border-teal-500/40 text-teal-300 shadow-[0_0_15px_rgba(20,184,166,0.15)]'
                        : 'bg-transparent border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <span className="font-orbitron font-bold text-xs tracking-wider uppercase">
                      Fast Rank Engine
                    </span>
                    <span className="text-[10px] text-slate-500 leading-normal max-w-[150px]">
                      Runs instant matrix analysis of 8 compatibility vectors across all hubs.
                    </span>
                  </button>

                  {/* Mode CrewAI */}
                  <button
                    type="button"
                    onClick={() => setMode('crew')}
                    className={`p-4 rounded-lg flex flex-col items-center justify-center gap-1.5 transition-all duration-300 border text-center ${
                      mode === 'crew'
                        ? 'bg-indigo-500/10 border-indigo-500/40 text-indigo-300 shadow-[0_0_15px_rgba(99,102,241,0.15)]'
                        : 'bg-transparent border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <span className="font-orbitron font-bold text-xs tracking-wider uppercase">
                      CrewAI Deep Planner
                    </span>
                    <span className="text-[10px] text-slate-500 leading-normal max-w-[150px]">
                      Orchestrates a sequential multi-agent simulation crew. Creates group & solo itineraries.
                    </span>
                  </button>
                </div>

                <div className="flex items-center gap-2 p-3.5 bg-slate-900/60 rounded-lg border border-white/5 text-left text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                  <AlertCircle className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                  <span>
                    Note: Deep CrewAI planning can take up to 30-45 seconds to synthesize agents' reasoning chains.
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Stepper Navigation Buttons */}
      <div className="flex items-center justify-between border-t border-white/5 pt-6 mt-8 max-w-xl mx-auto">
        <button
          type="button"
          onClick={handlePrev}
          disabled={step === 1 || loading}
          className={`flex items-center gap-2 px-4 py-2 border rounded-lg text-xs font-orbitron font-bold uppercase tracking-wider transition-all duration-300 ${
            step === 1 || loading
              ? 'border-white/5 text-slate-600 cursor-not-allowed'
              : 'border-white/10 hover:border-white/20 text-slate-300'
          }`}
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        {step < 3 ? (
          <button
            type="button"
            onClick={handleNext}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 border border-indigo-500 text-indigo-100 rounded-lg text-xs font-orbitron font-bold uppercase tracking-wider hover:bg-indigo-500 transition-all duration-300 shadow-[0_0_15px_rgba(99,102,241,0.2)]"
          >
            Continue
            <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-teal-500 to-indigo-600 text-white rounded-lg text-xs font-orbitron font-extrabold uppercase tracking-widest hover:from-teal-400 hover:to-indigo-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-wait shadow-[0_0_20px_rgba(20,184,166,0.25)] border-t border-white/20"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/35 border-t-white rounded-full animate-spin"></span>
                Synthesizing Plans...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 animate-pulse" />
                Engage Routing Crew
              </>
            )}
          </button>
        )}
      </div>
    </form>
  );
};
