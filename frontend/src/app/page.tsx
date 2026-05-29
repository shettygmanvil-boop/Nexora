"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  ShieldAlert,
  Thermometer,
  User,
  Compass,
  Calendar,
  DollarSign,
  Plus,
  Trash,
  Check,
  HelpCircle,
  ArrowUpRight,
  Loader2,
  Heart,
  Plane,
  ChevronRight,
  Smile,
  Moon,
  Info
} from "lucide-react";

interface Traveler {
  name: string;
  age: number;
  food_preference: string;
  mood: string;
  travel_purpose: string;
  medical_conditions: string[];
  activity_level: string;
  budget_preference: string;
  vibe_preference: string;
  accommodation_preference: string;
  travel_style: string;
}

export default function CyberpunkTravelTerminal() {
  // Core States
  const [travelers, setTravelers] = useState<Traveler[]>([
    {
      name: "Alice",
      age: 28,
      food_preference: "veg",
      mood: "excited",
      travel_purpose: "leisure",
      medical_conditions: [],
      activity_level: "medium",
      budget_preference: "standard",
      vibe_preference: "beaches",
      accommodation_preference: "standard",
      travel_style: "relaxation"
    },
    {
      name: "Bob",
      age: 65,
      food_preference: "non-veg",
      mood: "relaxed",
      travel_purpose: "relaxation",
      medical_conditions: ["hypertension"],
      activity_level: "low",
      budget_preference: "luxury",
      vibe_preference: "nature",
      accommodation_preference: "luxury",
      travel_style: "relaxation"
    }
  ]);

  const [totalBudget, setTotalBudget] = useState<number>(50000);
  const [numDays, setNumDays] = useState<number>(4);
  const [expectations, setExpectations] = useState<string>(
    "I want a relaxing beach getaway with beautiful sunset views and good vegetarian food."
  );
  const [preferredVibe, setPreferredVibe] = useState<string>("beaches");
  const [destinationPreference, setDestinationPreference] = useState<string>("Goa");
  const [hotelCount, setHotelCount] = useState<number>(3);
  
  // Advanced priorities
  const [priorities, setPriorities] = useState<string[]>(["relaxation", "sightseeing"]);
  
  // Unsure user helpers
  const [unsureMood, setUnsureMood] = useState<string>("peaceful weekend");
  const [unsureDetails, setUnsureDetails] = useState<string>("");

  // Result States
  const [destinations, setDestinations] = useState<any[]>([]);
  const [tripValidation, setTripValidation] = useState<any>(null);
  const [crewAIResult, setCrewAIResult] = useState<any>(null);
  
  // UI states
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"group" | "solo" | "reunion">("group");
  const [selectedSoloTraveler, setSelectedSoloTraveler] = useState<string>("Alice");
  const [serverStatus, setServerStatus] = useState<"online" | "offline">("offline");
  
  // Fetch Destinations and Health Status on mount
  useEffect(() => {
    checkServerStatus();
    loadDestinations();
  }, []);

  // Check if server is running
  const checkServerStatus = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/health");
      if (res.ok) {
        setServerStatus("online");
      } else {
        setServerStatus("offline");
      }
    } catch {
      setServerStatus("offline");
    }
  };

  // Load available destinations
  const loadDestinations = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/destinations");
      if (res.ok) {
        const data = await res.json();
        setDestinations(data);
      }
    } catch (e) {
      console.error("Failed to load destinations", e);
    }
  };

  // Add a traveler profile
  const addTraveler = () => {
    const names = ["Charlie", "Diana", "Ethan", "Fiona"];
    const name = names[travelers.length % names.length] + " " + (Math.floor(travelers.length / 4) + 1);
    setTravelers([
      ...travelers,
      {
        name,
        age: 30,
        food_preference: "veg",
        mood: "chill",
        travel_purpose: "relaxation",
        medical_conditions: [],
        activity_level: "medium",
        budget_preference: "standard",
        vibe_preference: "nature",
        accommodation_preference: "standard",
        travel_style: "relaxation"
      }
    ]);
  };

  // Remove a traveler
  const removeTraveler = (index: number) => {
    if (travelers.length <= 1) return;
    const list = [...travelers];
    list.splice(index, 1);
    setTravelers(list);
  };

  // Update traveler details
  const updateTraveler = (index: number, key: keyof Traveler, value: any) => {
    setTravelers((prev) => {
      const list = [...prev];
      list[index] = { ...list[index], [key]: value };
      return list;
    });
  };

  // Update traveler medical condition list
  const updateTravelerMedical = (index: number, conditionText: string) => {
    const conditions = conditionText.split(",").map(c => c.trim()).filter(c => c.length > 0);
    updateTraveler(index, "medical_conditions", conditions);
  };

  // Handle Budget/Days variation via simulation sliders
  useEffect(() => {
    if (serverStatus === "online" && destinations.length > 0) {
      triggerSimulationUpdate();
    }
  }, [totalBudget, numDays, travelers]);

  // Trigger real-time simulation slider update
  const triggerSimulationUpdate = async () => {
    // Quick validation endpoint update
    try {
      const payload = {
        travelers: travelers.map(t => ({
          name: t.name,
          age: t.age,
          food_preference: t.food_preference,
          mood: t.mood,
          travel_purpose: t.travel_purpose,
          medical_conditions: t.medical_conditions,
          activity_level: t.activity_level,
          budget_preference: t.budget_preference
        })),
        budget: totalBudget,
        days: numDays,
        preferred_vibe: preferredVibe,
        priorities: priorities,
        destination_preference: destinationPreference,
        expectations: expectations
      };

      const res = await fetch("http://127.0.0.1:8000/validate-trip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        setTripValidation(data);
      }
    } catch (e) {
      console.error("Simulation query failure", e);
    }
  };

  // Trigger complete multi-agent orchestration crew
  const runOrchestrator = async () => {
    setIsLoading(true);
    checkServerStatus();
    try {
      // 1. Run ranked recommendation scores list
      const rankingPayload = {
        travelers: travelers.map(t => ({
          name: t.name,
          age: t.age,
          food_preference: t.food_preference,
          mood: t.mood,
          travel_purpose: t.travel_purpose,
          medical_conditions: t.medical_conditions,
          activity_level: t.activity_level,
          budget_preference: t.budget_preference
        })),
        budget: totalBudget,
        days: numDays,
        preferred_vibe: preferredVibe,
        priorities: priorities,
        destination_preference: destinationPreference,
        expectations: expectations
      };

      const rankRes = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rankingPayload)
      });
      
      let ranksData = [];
      if (rankRes.ok) {
        ranksData = await rankRes.json();
        // Update loaded destinations order
        if (ranksData.length > 0) {
          setDestinations(ranksData.map((r: any) => {
            const found = destinations.find(d => d.name.toLowerCase() === r.destination.toLowerCase());
            return found ? { ...found, ...r } : r;
          }));
        }
      }

      // 2. Run CrewAI group itinerary agent orchestrator
      const crewPayload = {
        travelers: travelers.map(t => ({
          name: t.name,
          age: t.age,
          medical_conditions: t.medical_conditions,
          vibe_preference: t.vibe_preference || preferredVibe,
          accommodation_preference: t.accommodation_preference,
          travel_style: t.travel_style,
          travel_purpose: t.travel_purpose
        })),
        total_budget: totalBudget,
        num_days: numDays,
        expectations: expectations,
        destination_preference: destinationPreference
      };

      const crewRes = await fetch("http://127.0.0.1:8000/recommendation/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(crewPayload)
      });

      if (crewRes.ok) {
        const crewData = await crewRes.ok ? await crewRes.json() : null;
        setCrewAIResult(crewData);
        // Sync tab view to group
        setActiveTab("group");
        if (travelers.length > 0) {
          setSelectedSoloTraveler(travelers[0].name);
        }
      }
    } catch (e) {
      console.error("Orchestrator error", e);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function for unsure users to select a destination
  const handleUnsureRecommend = () => {
    // Map mood to parameters
    if (unsureMood === "burnout recovery") {
      setPreferredVibe("scenic");
      setExpectations("I want a peaceful quiet sanctuary, away from crowd, scenic view and digital detox " + unsureDetails);
      setDestinationPreference("Srinagar");
    } else if (unsureMood === "adventure rush") {
      setPreferredVibe("adventure");
      setExpectations("Looking for exciting high energy activities, sports, beaches, water sports " + unsureDetails);
      setDestinationPreference("Goa");
    } else if (unsureMood === "peaceful weekend") {
      setPreferredVibe("peaceful");
      setExpectations("A relaxing chill escape, nice cafes, gardens, beautiful weather, pleasant walks " + unsureDetails);
      setDestinationPreference("Bangalore");
    } else if (unsureMood === "luxury escape") {
      setPreferredVibe("luxury");
      setExpectations("Royal treatment, historic hotels, luxury stay, palaces, fine food " + unsureDetails);
      setDestinationPreference("Jaipur");
    } else {
      setPreferredVibe("heritage");
      setExpectations("Family friendly, cultural heritage walk, temple visit, local shopping " + unsureDetails);
      setDestinationPreference("Jaipur");
    }
    
    // Auto trigger updates
    setTimeout(() => {
      triggerSimulationUpdate();
    }, 100);
  };

  return (
    <div className="min-h-screen relative p-4 md:p-8 flex flex-col gap-6 select-none animate-lazy-fade">
      {/* Scanner line overlay */}
      <div className="scan-line"></div>

      {/* ── HEADER TERMINAL ────────────────────────────────────────────────── */}
      <header className="glass-card-blue p-4 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="relative flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${serverStatus === "online" ? "bg-cyan-400" : "bg-rose-500"}`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${serverStatus === "online" ? "bg-cyan-500" : "bg-rose-500"}`}></span>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 text-glow-blue">
              MAPROOM // TRAVEL_ORCHESTRATOR
            </h1>
            <p className="text-xs text-cyan-500 font-mono tracking-wider">SYSTEM_PORT: 8000 // HACKATHON_DEMO_v1.0</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="glass-card-purple px-3 py-1 text-xs text-purple-400 font-mono border-purple-500/30">
            ENGINE_STATUS: <span className="text-glow-purple font-bold">{serverStatus.toUpperCase()}</span>
          </div>
          {serverStatus === "offline" && (
            <button
              onClick={checkServerStatus}
              className="neu-button-outset px-3 py-1 text-xs text-cyan-400 font-mono border-cyan-500/20 cursor-pointer"
            >
              PING_CONNECT
            </button>
          )}
        </div>
      </header>

      {/* ── MAIN DASHBOARD CONTAINER ────────────────────────────────────────── */}
      <main className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        
        {/* PANEL 1: USER INPUTS & PREFERENCES (xl:col-span-4) */}
        <section className="xl:col-span-4 flex flex-col gap-6">
          <div className="glass-card-blue p-5 flex flex-col gap-5">
            <div className="flex justify-between items-center border-b border-cyan-500/20 pb-2">
              <h2 className="text-sm font-bold tracking-widest text-cyan-400 uppercase font-mono flex items-center gap-2">
                <User size={16} /> [01] Traveler Profiles
              </h2>
              <button
                onClick={addTraveler}
                className="neu-button-outset px-2 py-1 text-xs text-cyan-400 font-mono flex items-center gap-1 cursor-pointer"
              >
                <Plus size={12} /> ADD_USER
              </button>
            </div>

            {/* Travelers fields list */}
            <div className="flex flex-col gap-4 max-h-[300px] overflow-y-auto pr-1">
              {travelers.map((traveler, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg border border-purple-500/20 bg-purple-950/10 flex flex-col gap-3 relative"
                >
                  <button
                    onClick={() => removeTraveler(idx)}
                    className="absolute top-2 right-2 text-rose-500 hover:text-rose-400 cursor-pointer"
                    title="Delete Traveler"
                  >
                    <Trash size={14} />
                  </button>

                  <div className="grid grid-cols-12 gap-2">
                    {/* Name */}
                    <div className="col-span-8">
                      <label className="text-[10px] text-purple-400 font-mono uppercase tracking-wider block">Traveler Name</label>
                      <input
                        type="text"
                        value={traveler.name}
                        onChange={(e) => updateTraveler(idx, "name", e.target.value)}
                        className="neu-input-inset w-full px-2 py-1 text-xs"
                      />
                    </div>
                    {/* Age */}
                    <div className="col-span-4">
                      <label className="text-[10px] text-purple-400 font-mono uppercase tracking-wider block">Age</label>
                      <input
                        type="number"
                        value={traveler.age}
                        onChange={(e) => updateTraveler(idx, "age", parseInt(e.target.value) || 0)}
                        className="neu-input-inset w-full px-2 py-1 text-xs text-center"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    {/* Food Preference */}
                    <div>
                      <label className="text-[10px] text-purple-400 font-mono uppercase block">Food Taste</label>
                      <select
                        value={traveler.food_preference}
                        onChange={(e) => updateTraveler(idx, "food_preference", e.target.value)}
                        className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                      >
                        <option value="veg">Vegetarian</option>
                        <option value="non-veg">Non-Vegetarian</option>
                        <option value="vegan">Vegan</option>
                      </select>
                    </div>

                    {/* Vibe Preference */}
                    <div>
                      <label className="text-[10px] text-purple-400 font-mono uppercase block">Personal Vibe</label>
                      <select
                        value={traveler.vibe_preference}
                        onChange={(e) => updateTraveler(idx, "vibe_preference", e.target.value)}
                        className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                      >
                        <option value="beaches">Beaches</option>
                        <option value="nightlife">Nightlife</option>
                        <option value="heritage">Heritage</option>
                        <option value="spirituality">Spirituality</option>
                        <option value="nature">Nature / Quiet</option>
                        <option value="cafes">Cafes</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    {/* Travel Purpose */}
                    <div>
                      <label className="text-[10px] text-purple-400 font-mono uppercase block">Travel Purpose</label>
                      <select
                        value={traveler.travel_purpose}
                        onChange={(e) => updateTraveler(idx, "travel_purpose", e.target.value)}
                        className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                      >
                        <option value="relaxation">Relaxation</option>
                        <option value="adventure">Adventure</option>
                        <option value="spirituality">Spirituality</option>
                        <option value="luxury">Luxury</option>
                        <option value="family bonding">Family Bonding</option>
                        <option value="workcation">Workcation</option>
                        <option value="photography">Photography</option>
                        <option value="digital detox">Digital Detox</option>
                      </select>
                    </div>

                    {/* Activity Level */}
                    <div>
                      <label className="text-[10px] text-purple-400 font-mono uppercase block">Activity Intensity</label>
                      <select
                        value={traveler.activity_level}
                        onChange={(e) => updateTraveler(idx, "activity_level", e.target.value)}
                        className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                      >
                        <option value="low">Low (Relaxed)</option>
                        <option value="medium">Medium (Moderate)</option>
                        <option value="high">High (Active)</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    {/* Budget & Hotel Tier */}
                    <div>
                      <label className="text-[10px] text-purple-400 font-mono uppercase block">Budget / Hotel Tier</label>
                      <select
                        value={traveler.budget_preference}
                        onChange={(e) => {
                          updateTraveler(idx, "budget_preference", e.target.value);
                          updateTraveler(idx, "accommodation_preference", e.target.value);
                        }}
                        className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                      >
                        <option value="budget">Budget</option>
                        <option value="standard">Standard</option>
                        <option value="luxury">Luxury</option>
                      </select>
                    </div>

                    {/* Travel Style */}
                    <div>
                      <label className="text-[10px] text-purple-400 font-mono uppercase block">Travel Style</label>
                      <select
                        value={traveler.travel_style}
                        onChange={(e) => updateTraveler(idx, "travel_style", e.target.value)}
                        className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                      >
                        <option value="relaxation">Relaxation</option>
                        <option value="adventure">Adventure</option>
                        <option value="photography">Photography</option>
                        <option value="workcation">Workcation</option>
                        <option value="digital detox">Digital Detox</option>
                      </select>
                    </div>
                  </div>

                  {/* Medical Conditions */}
                  <div>
                    <label className="text-[10px] text-purple-400 font-mono uppercase block">
                      Medical / Health Concerns (comma-separated)
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. asthma, knee pain, hypertension"
                      value={traveler.medical_conditions.join(", ")}
                      onChange={(e) => updateTravelerMedical(idx, e.target.value)}
                      className="neu-input-inset w-full px-2 py-1 text-xs"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* SIMULATION SLIDERS */}
          <div className="glass-card-purple p-5 flex flex-col gap-4">
            <h2 className="text-sm font-bold tracking-widest text-purple-400 uppercase font-mono border-b border-purple-500/20 pb-2 flex items-center gap-2">
              <Compass size={16} /> [02] Simulation Controls
            </h2>

            {/* Slider 1: Budget */}
            <div className="flex flex-col gap-1">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-purple-300 uppercase">Simulated Budget</span>
                <span className="text-cyan-400 font-bold text-glow-blue">₹{totalBudget.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="5000"
                max="200000"
                step="2000"
                value={totalBudget}
                onChange={(e) => setTotalBudget(parseInt(e.target.value))}
                className="w-full h-1.5 bg-[#06040d] rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
            </div>

            {/* Slider 2: Number of Days */}
            <div className="flex flex-col gap-1">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-purple-300 uppercase">Trip Duration</span>
                <span className="text-purple-400 font-bold text-glow-purple">{numDays} DAYS</span>
              </div>
              <input
                type="range"
                min="1"
                max="15"
                step="1"
                value={numDays}
                onChange={(e) => setNumDays(parseInt(e.target.value))}
                className="w-full h-1.5 bg-[#06040d] rounded-lg appearance-none cursor-pointer accent-purple-500"
              />
            </div>

            {/* Text Input: Expectations */}
            <div>
              <label className="text-xs text-purple-300 font-mono uppercase block mb-1">
                Written Expectations / Vibe Request
              </label>
              <textarea
                rows={2}
                value={expectations}
                onChange={(e) => setExpectations(e.target.value)}
                placeholder="Describe your ideal vibe... e.g. peaceful sunset lake, active nightlife, etc."
                className="neu-input-inset w-full px-2 py-1 text-xs"
              />
            </div>

            {/* Vibe selection & Target destination preference */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-purple-400 font-mono uppercase block mb-1">Preferred Vibe</label>
                <select
                  value={preferredVibe}
                  onChange={(e) => setPreferredVibe(e.target.value)}
                  className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                >
                  <option value="beaches">Beaches</option>
                  <option value="mountains">Mountains</option>
                  <option value="nightlife">Nightlife</option>
                  <option value="heritage">Heritage</option>
                  <option value="cafes">Cafes</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] text-purple-400 font-mono uppercase block mb-1">Target Location</label>
                <select
                  value={destinationPreference}
                  onChange={(e) => setDestinationPreference(e.target.value)}
                  className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                >
                  <option value="Goa">Goa</option>
                  <option value="Bangalore">Bangalore</option>
                  <option value="Srinagar">Srinagar</option>
                  <option value="Jaipur">Jaipur</option>
                </select>
              </div>
            </div>

            {/* Pick hotel count */}
            <div className="flex items-center justify-between text-xs font-mono mt-1">
              <span className="text-purple-300 uppercase">View Hotel Options</span>
              <div className="flex gap-2">
                {[3, 5, 10].map(count => (
                  <button
                    key={count}
                    onClick={() => setHotelCount(count)}
                    className={`px-2 py-1 text-xs border rounded transition-all cursor-pointer ${hotelCount === count ? "border-cyan-400 bg-cyan-950/20 text-cyan-400" : "border-purple-500/20 text-purple-400"}`}
                  >
                    {count}
                  </button>
                ))}
              </div>
            </div>

            {/* EXECUTE BUTTON */}
            <button
              onClick={runOrchestrator}
              disabled={isLoading || serverStatus === "offline"}
              className="neu-button-outset w-full py-3 text-sm font-bold font-mono tracking-widest text-glow-blue border-cyan-400/30 text-cyan-400 hover:text-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2 mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> ORCHESTRATING_CREW...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> TRIGGER_AGENT_ORCHESTRATION
                </>
              )}
            </button>
          </div>
        </section>

        {/* PANEL 2: MATCH SCORES & DESTINATION SELECTION (xl:col-span-4) */}
        <section className="xl:col-span-4 flex flex-col gap-6">
          <div className="glass-card-blue p-5 flex flex-col gap-4">
            <h2 className="text-sm font-bold tracking-widest text-cyan-400 uppercase font-mono border-b border-cyan-500/20 pb-2 flex items-center gap-2">
              <Sparkles size={16} /> [03] Destination Compatibility
            </h2>

            {/* Ranked candidate destinations list */}
            <div className="flex flex-col gap-3">
              {destinations.map((dest, idx) => {
                const score = dest.compatibility_score || 70.0;
                const isSelected = dest.name === destinationPreference;
                
                return (
                  <div
                    key={idx}
                    onClick={() => {
                      setDestinationPreference(dest.name);
                      triggerSimulationUpdate();
                    }}
                    className={`p-3 rounded-lg border transition-all cursor-pointer flex flex-col gap-2 ${isSelected ? "border-cyan-400 bg-cyan-950/15" : "border-purple-500/10 bg-purple-950/5 hover:border-cyan-500/30"}`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-bold font-mono text-sm tracking-wide text-glow-blue text-cyan-300">
                        #{idx + 1} {dest.name.toUpperCase()}
                      </span>
                      <span className="text-xs font-mono font-bold px-2 py-0.5 rounded border border-cyan-500/30 bg-cyan-950/30 text-cyan-400">
                        {score.toFixed(1)}% MATCH
                      </span>
                    </div>

                    <p className="text-[11px] text-purple-300/80 leading-relaxed font-mono">
                      {dest.best_for || "Climate-optimized travel destination package."}
                    </p>

                    {/* Displays mini factor bars */}
                    {dest.factor_scores && (
                      <div className="grid grid-cols-4 gap-1.5 mt-1">
                        {Object.entries(dest.factor_scores).slice(0, 4).map(([key, val]: any) => (
                          <div key={key} className="flex flex-col">
                            <span className="text-[8px] text-purple-400 uppercase tracking-tighter truncate">{key.replace("_", " ")}</span>
                            <div className="w-full bg-[#06040d] h-1 rounded-full overflow-hidden">
                              <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${val}%` }}></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* EXPECTATION VS REALITY */}
          {tripValidation && (
            <div className="glass-card-purple p-5 flex flex-col gap-4">
              <h2 className="text-sm font-bold tracking-widest text-purple-400 uppercase font-mono border-b border-purple-500/20 pb-2 flex items-center gap-2">
                <Info size={16} /> [04] Expectation Matcher
              </h2>

              <div className="flex items-center justify-between border border-cyan-500/20 bg-cyan-950/10 p-3 rounded-lg">
                <span className="text-xs font-mono text-purple-300">Experience overlap score</span>
                <span className="text-lg font-bold font-mono text-cyan-400 text-glow-blue">
                  {tripValidation.compatibility_score}%
                </span>
              </div>

              {/* Explainable AI reasons snippet */}
              <div className="flex flex-col gap-2">
                <span className="text-[10px] text-purple-400 font-mono uppercase tracking-wider block">Decision Reasons</span>
                <ul className="flex flex-col gap-1.5">
                  {tripValidation.reasons?.map((reason: string, idx: number) => (
                    <li key={idx} className="text-xs leading-relaxed text-purple-300 flex items-start gap-1.5 font-mono">
                      <ChevronRight size={12} className="text-cyan-400 shrink-0 mt-0.5" />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Dynamic Upgrades Alert */}
              <div className="border border-purple-500/20 bg-purple-950/10 p-3 rounded-lg flex flex-col gap-1">
                <span className="text-[10px] text-cyan-400 font-mono tracking-wider font-bold">UPGRADE_RECOMMENDATION</span>
                <p className="text-xs text-purple-200 leading-relaxed font-mono">
                  If you expand budget by ₹2,000, you can unlock premium activities and upgrade hotel tier in {destinationPreference}.
                </p>
              </div>
            </div>
          )}

          {/* UNSURE USERS PORTAL */}
          <div className="glass-card-blue p-5 flex flex-col gap-3">
            <h2 className="text-sm font-bold tracking-widest text-cyan-400 uppercase font-mono border-b border-cyan-500/20 pb-2 flex items-center gap-2">
              <HelpCircle size={16} /> [05] Unsure Users Portal
            </h2>
            <p className="text-xs text-purple-300 font-mono">
              Unsure of where to travel? Choose your current mood and let the engine solve it.
            </p>

            <div className="flex flex-col gap-3 mt-1">
              <div>
                <label className="text-[10px] text-purple-400 font-mono uppercase block mb-1">Target Mood</label>
                <select
                  value={unsureMood}
                  onChange={(e) => setUnsureMood(e.target.value)}
                  className="neu-input-inset w-full px-2 py-1 text-xs bg-[#06040d]"
                >
                  <option value="peaceful weekend">Peaceful Weekend (Bangalore)</option>
                  <option value="adventure rush">Adventure Rush (Goa)</option>
                  <option value="burnout recovery">Burnout Recovery (Srinagar)</option>
                  <option value="luxury escape">Luxury Escape (Jaipur)</option>
                  <option value="family bonding">Family Bonding (Jaipur/Goa)</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] text-purple-400 font-mono uppercase block mb-1">Extra Details (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. sunset lake views, cafe hopping"
                  value={unsureDetails}
                  onChange={(e) => setUnsureDetails(e.target.value)}
                  className="neu-input-inset w-full px-2 py-1 text-xs"
                />
              </div>

              <button
                onClick={handleUnsureRecommend}
                className="neu-button-outset py-2 text-xs font-bold font-mono tracking-widest text-glow-blue border-cyan-400/20 text-cyan-400 cursor-pointer"
              >
                AUTOPILOT_SETUP
              </button>
            </div>
          </div>
        </section>

        {/* PANEL 3: DYNAMIC ITINERARY & INTEL (xl:col-span-4) */}
        <section className="xl:col-span-4 flex flex-col gap-6">
          
          {/* WEATHER WARNINGS CARDS */}
          {tripValidation && (
            <div className="glass-card-blue p-5 flex flex-col gap-3">
              <h2 className="text-sm font-bold tracking-widest text-rose-500 uppercase font-mono border-b border-rose-500/20 pb-2 flex items-center gap-2">
                <ShieldAlert size={16} /> [06] Climate & Health warnings
              </h2>

              <div className="flex flex-col gap-2">
                {tripValidation.warnings?.map((warning: string, idx: number) => (
                  <div
                    key={idx}
                    className="p-2 border border-rose-500/20 bg-rose-950/10 rounded flex gap-2 items-start"
                  >
                    <Thermometer size={16} className="text-rose-500 shrink-0 mt-0.5" />
                    <p className="text-[11px] font-mono leading-relaxed text-rose-300">{warning}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* DYNAMIC ITINERARY VISUALIZER */}
          <div className="glass-card-purple p-5 flex flex-col gap-4">
            <h2 className="text-sm font-bold tracking-widest text-purple-400 uppercase font-mono border-b border-purple-500/20 pb-2 flex items-center gap-2">
              <Calendar size={16} /> [07] Intelligently Split Itineraries
            </h2>

            {/* TAB SELECTOR FOR ITINERARY */}
            <div className="grid grid-cols-3 gap-1 p-1 bg-[#06040d] border border-purple-500/20 rounded-lg">
              {(["group", "solo", "reunion"] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-1.5 text-[10px] font-mono uppercase tracking-wider rounded transition-all cursor-pointer ${activeTab === tab ? "bg-purple-900/30 text-purple-300 font-bold border border-purple-500/30" : "text-purple-400 hover:text-purple-300"}`}
                >
                  {tab} ITINERARY
                </button>
              ))}
            </div>

            {/* For Solo Tab, show traveler dropdown */}
            {activeTab === "solo" && (
              <div className="flex items-center justify-between text-[11px] font-mono border-b border-purple-500/10 pb-2">
                <span className="text-purple-400 uppercase">Select Traveler:</span>
                <select
                  value={selectedSoloTraveler}
                  onChange={(e) => setSelectedSoloTraveler(e.target.value)}
                  className="neu-input-inset px-2 py-0.5 text-xs bg-[#06040d] border-purple-500/30 text-purple-300"
                >
                  {travelers.map(t => (
                    <option key={t.name} value={t.name}>{t.name}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Render Itinerary list */}
            <div className="flex flex-col gap-4 max-h-[350px] overflow-y-auto pr-1 font-mono">
              {crewAIResult ? (
                <>
                  {/* Load itinerary from CrewAI response */}
                  {activeTab === "group" && (
                    crewAIResult.group_itinerary?.map((day: any, dIdx: number) => (
                      <div key={dIdx} className="flex flex-col gap-2">
                        <span className="text-xs font-bold text-cyan-400 tracking-wider">DAY {day.day} // GROUP ACTIVITIES</span>
                        {day.activities?.map((act: any, aIdx: number) => (
                          <div key={aIdx} className="p-2 border border-cyan-500/20 bg-cyan-950/5 rounded flex flex-col gap-1 text-[11px]">
                            <div className="flex justify-between items-center text-cyan-300">
                              <span className="font-bold">{act.activity_name} ({act.time})</span>
                              <span>₹{act.estimated_cost}</span>
                            </div>
                            <p className="text-purple-300/80 text-[10px] leading-relaxed">{act.description}</p>
                            <span className="text-[8px] text-cyan-500 uppercase">Fatigue level: {act.fatigue_level}/5</span>
                          </div>
                        ))}
                      </div>
                    ))
                  )}

                  {activeTab === "solo" && (
                    crewAIResult.solo_itineraries?.[selectedSoloTraveler]?.map((day: any, dIdx: number) => (
                      <div key={dIdx} className="flex flex-col gap-2">
                        <span className="text-xs font-bold text-purple-400 tracking-wider">DAY {day.day} // SOLO ACTIVITIES ({selectedSoloTraveler})</span>
                        {day.activities?.map((act: any, aIdx: number) => (
                          <div key={aIdx} className="p-2 border border-purple-500/20 bg-purple-950/5 rounded flex flex-col gap-1 text-[11px]">
                            <div className="flex justify-between items-center text-purple-300">
                              <span className="font-bold">{act.activity_name} ({act.time})</span>
                              <span>₹{act.estimated_cost}</span>
                            </div>
                            <p className="text-purple-300/80 text-[10px] leading-relaxed">{act.description}</p>
                            <span className="text-[8px] text-purple-500 uppercase font-bold">Custom tracking for {selectedSoloTraveler}</span>
                          </div>
                        ))}
                      </div>
                    ))
                  )}

                  {activeTab === "reunion" && (
                    crewAIResult.reunion_schedule?.map((day: any, dIdx: number) => (
                      <div key={dIdx} className="flex flex-col gap-2">
                        <span className="text-xs font-bold text-cyan-400 tracking-wider">DAY {day.day} // REUNION meal SCHEDULE</span>
                        {day.activities?.map((act: any, aIdx: number) => (
                          <div key={aIdx} className="p-2 border border-cyan-500/20 bg-cyan-950/5 rounded flex flex-col gap-1 text-[11px]">
                            <div className="flex justify-between items-center text-cyan-300">
                              <span className="font-bold">{act.activity_name} ({act.time})</span>
                              <span>₹{act.estimated_cost}</span>
                            </div>
                            <p className="text-purple-300/80 text-[10px] leading-relaxed">{act.description}</p>
                            <span className="text-[8px] text-cyan-500 uppercase tracking-widest font-bold">ALL MEMBERS GATHER</span>
                          </div>
                        ))}
                      </div>
                    ))
                  )}
                </>
              ) : (
                <div className="p-4 border border-purple-500/10 bg-purple-950/5 rounded text-center text-xs text-purple-400">
                  Execute the Orchestrator to compile group/solo itineraries.
                </div>
              )}
            </div>
          </div>

          {/* DYNAMIC HOTEL HIGHLIGHTS */}
          {crewAIResult?.budget_analysis && (
            <div className="glass-card-blue p-5 flex flex-col gap-3">
              <h2 className="text-sm font-bold tracking-widest text-cyan-400 uppercase font-mono border-b border-cyan-500/20 pb-2 flex items-center gap-2">
                <DollarSign size={16} /> [08] Hotel Sentiment & Budget Analysis
              </h2>

              <div className="flex flex-col gap-2 font-mono text-[11px]">
                <div className="flex justify-between py-1 border-b border-purple-500/10 text-purple-300">
                  <span>Hotel Budget Allocation:</span>
                  <span className="text-cyan-400">₹{crewAIResult.budget_analysis.accommodation_cost}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-purple-500/10 text-purple-300">
                  <span>Sightseeing/Activities:</span>
                  <span className="text-cyan-400">₹{crewAIResult.budget_analysis.activities_cost}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-purple-500/10 text-purple-300">
                  <span>Emergency Contingency:</span>
                  <span className="text-cyan-400">₹{crewAIResult.budget_analysis.buffer_amount}</span>
                </div>
                <p className="text-[10px] text-purple-300/80 leading-relaxed mt-1">
                  {crewAIResult.budget_analysis.explanation}
                </p>
                
                {/* Sentiment Highlight Keyword */}
                <div className="mt-2 p-2 border border-cyan-500/20 bg-cyan-950/15 rounded flex items-center justify-between">
                  <span className="text-[10px] uppercase text-cyan-400">Sentiment highlight:</span>
                  <span className="text-xs font-bold text-glow-blue text-cyan-300 uppercase tracking-widest">
                    {totalBudget > 80000 ? "Hospitality services" : "Value for Money"}
                  </span>
                </div>
              </div>
            </div>
          )}

        </section>

      </main>

      {/* FOOTER TERMINAL */}
      <footer className="glass-card-purple p-4 text-center text-xs text-purple-400 font-mono tracking-wider border-purple-500/10">
        MAPROOM // POWERED_BY_CREWAI // DEVELOPED_FOR_AGENTIC_AI_HACKATHON
      </footer>
    </div>
  );
}
