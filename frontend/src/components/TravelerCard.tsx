import React from 'react';
import { motion } from 'framer-motion';
import { Trash2, User, HeartPulse } from 'lucide-react';
import { Traveler } from '../services/api';

// Extends Traveler type with optional fields for CrewAI mode
export interface TravelerFormVal extends Traveler {
  accommodation_preference: 'budget' | 'standard' | 'luxury';
  travel_style: string;
}

interface TravelerCardProps {
  index: number;
  traveler: TravelerFormVal;
  onChange: (index: number, updatedTraveler: TravelerFormVal) => void;
  onRemove: (index: number) => void;
  canRemove: boolean;
}

const moods = ['excited', 'relaxed', 'chill', 'adventurous'];
const foodPreferences = ['veg', 'non-veg', 'vegan', 'halal', 'kosher'];
const travelStyles = ['relaxation', 'adventure', 'photography', 'workcation', 'digital detox'];
const travelPurposes = [
  'leisure',
  'relaxation',
  'adventure',
  'spirituality',
  'nature exploration',
  'workcation',
  'luxury',
  'photography',
  'family bonding',
  'business',
];

export const TravelerCard: React.FC<TravelerCardProps> = ({
  index,
  traveler,
  onChange,
  onRemove,
  canRemove,
}) => {
  const handleChange = (field: keyof TravelerFormVal, value: any) => {
    onChange(index, { ...traveler, [field]: value });
  };

  const handleMedicalChange = (val: string) => {
    // Split by comma and filter empty entries
    const list = val.split(',').map((item) => item.trim()).filter((item) => item.length > 0);
    handleChange('medical_conditions', list);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className="glass-panel p-6 rounded-xl border border-white/5 shadow-xl relative overflow-hidden group hover:border-teal-500/20 transition-all duration-300"
    >
      {/* Background glow tint */}
      <div className="absolute -top-10 -left-10 w-24 h-24 bg-teal-500/5 blur-xl pointer-events-none rounded-full"></div>

      {/* Header section */}
      <div className="flex items-center justify-between border-b border-white/5 pb-4 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-md bg-teal-500/10 border border-teal-500/20 text-teal-400">
            <User className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-orbitron font-extrabold text-sm tracking-wide text-slate-200">
              TRAVELER #{index + 1}
            </h3>
            <p className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">
              {traveler.name || 'UNNAMED PROFILE'}
            </p>
          </div>
        </div>

        {canRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="p-2 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-400 hover:bg-rose-500/20 hover:text-rose-300 transition-all duration-300"
            title="Remove traveler"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Inputs grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Name */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Full Name
          </label>
          <input
            type="text"
            required
            value={traveler.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g. Alice"
            className="w-full bg-slate-950/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 focus:shadow-[0_0_10px_rgba(20,184,166,0.15)] transition-all duration-300 placeholder:text-slate-600"
          />
        </div>

        {/* Age */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Age (Years)
          </label>
          <input
            type="number"
            required
            min="0"
            max="120"
            value={traveler.age || ''}
            onChange={(e) => handleChange('age', parseInt(e.target.value) || 0)}
            placeholder="e.g. 28"
            className="w-full bg-slate-950/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 focus:shadow-[0_0_10px_rgba(20,184,166,0.15)] transition-all duration-300 placeholder:text-slate-600"
          />
        </div>

        {/* Mood */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Current Mood
          </label>
          <select
            value={traveler.mood}
            onChange={(e) => handleChange('mood', e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300 capitalize"
          >
            {moods.map((m) => (
              <option key={m} value={m} className="bg-slate-950">
                {m}
              </option>
            ))}
          </select>
        </div>

        {/* Travel Purpose */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Travel Purpose
          </label>
          <select
            value={traveler.travel_purpose}
            onChange={(e) => handleChange('travel_purpose', e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300 capitalize"
          >
            {travelPurposes.map((tp) => (
              <option key={tp} value={tp} className="bg-slate-950">
                {tp}
              </option>
            ))}
          </select>
        </div>

        {/* Food Preference */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Food Preference
          </label>
          <select
            value={traveler.food_preference}
            onChange={(e) => handleChange('food_preference', e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300 capitalize"
          >
            {foodPreferences.map((fp) => (
              <option key={fp} value={fp} className="bg-slate-950">
                {fp}
              </option>
            ))}
          </select>
        </div>

        {/* Activity Level */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Activity Intensity
          </label>
          <select
            value={traveler.activity_level}
            onChange={(e) => handleChange('activity_level', e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300 capitalize"
          >
            {['low', 'medium', 'high'].map((al) => (
              <option key={al} value={al} className="bg-slate-950">
                {al} intensity
              </option>
            ))}
          </select>
        </div>

        {/* Budget Preference */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Budget Tier Pref
          </label>
          <select
            value={traveler.budget_preference}
            onChange={(e) => handleChange('budget_preference', e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300 capitalize"
          >
            {['budget', 'standard', 'luxury'].map((bp) => (
              <option key={bp} value={bp} className="bg-slate-950">
                {bp} tier
              </option>
            ))}
          </select>
        </div>

        {/* Travel Style */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Travel Style
          </label>
          <select
            value={traveler.travel_style}
            onChange={(e) => handleChange('travel_style', e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300 capitalize"
          >
            {travelStyles.map((ts) => (
              <option key={ts} value={ts} className="bg-slate-950">
                {ts}
              </option>
            ))}
          </select>
        </div>

        {/* Accommodation Preference */}
        <div>
          <label className="block text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            Accommodation
          </label>
          <select
            value={traveler.accommodation_preference}
            onChange={(e) => handleChange('accommodation_preference', e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 transition-all duration-300 capitalize"
          >
            {['budget', 'standard', 'luxury'].map((ap) => (
              <option key={ap} value={ap} className="bg-slate-950">
                {ap} stay
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Medical Conditions */}
      <div className="mt-4 pt-4 border-t border-white/5 flex flex-col md:flex-row md:items-center gap-4">
        <div className="flex-grow">
          <label className="flex items-center gap-1.5 text-[10px] font-orbitron font-extrabold uppercase tracking-widest text-slate-400 mb-1.5">
            <HeartPulse className="w-3.5 h-3.5 text-rose-500" />
            Medical Conditions (Comma-separated)
          </label>
          <input
            type="text"
            value={traveler.medical_conditions.join(', ')}
            onChange={(e) => handleMedicalChange(e.target.value)}
            placeholder="e.g. asthma, knee pain, hypertension (leave blank if none)"
            className="w-full bg-slate-950/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500/50 focus:shadow-[0_0_10px_rgba(20,184,166,0.15)] transition-all duration-300 placeholder:text-slate-700"
          />
        </div>
      </div>
    </motion.div>
  );
};
