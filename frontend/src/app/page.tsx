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
  Info,
  ChevronUp,
  ChevronDown,
  ArrowUp,
  ArrowDown
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

export default function TripMindAI() {
  // Core States
  const [mainTab, setMainTab] = useState<"planned" | "autopilot">("planned");
  const [numPeople, setNumPeople] = useState<number>(2);
  const [travelers, setTravelers] = useState<Traveler[]>([
    {
      name: "Alice",
      age: 28,
      food_preference: "veg",
      mood: "excited",
      travel_purpose: "relaxation",
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

  const [specifyBudget, setSpecifyBudget] = useState<boolean>(true);
  const [totalBudget, setTotalBudget] = useState<number>(50000);
  const [specifyDays, setSpecifyDays] = useState<boolean>(true);
  const [numDays, setNumDays] = useState<number>(4);
  
  const [expectations, setExpectations] = useState<string>(
    "I want a relaxing beach getaway with beautiful sunset views and good vegetarian food."
  );
  const [preferredVibe, setPreferredVibe] = useState<string>("beaches");
  const [destinationPreference, setDestinationPreference] = useState<string>("Goa");
  const [hotelCount, setHotelCount] = useState<number>(3);
  
  // Custom rearranged priorities
  const [priorities, setPriorities] = useState<string[]>(["vibe", "budget", "travel_mode", "accommodation"]);
  
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

  // Resize travelers array when numPeople changes
  useEffect(() => {
    if (numPeople > travelers.length) {
      const diff = numPeople - travelers.length;
      const newTravelers = [...travelers];
      const names = ["Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia"];
      for (let i = 0; i < diff; i++) {
        const idx = travelers.length + i;
        const name = names[idx % names.length] + " " + (Math.floor(idx / names.length) + 1);
        newTravelers.push({
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
        });
      }
      setTravelers(newTravelers);
    } else if (numPeople < travelers.length) {
      setTravelers(travelers.slice(0, numPeople));
    }
  }, [numPeople]);

  // Priorities list rearranging helper
  const movePriority = (index: number, direction: "up" | "down") => {
    if (direction === "up" && index === 0) return;
    if (direction === "down" && index === priorities.length - 1) return;
    
    const nextIndex = direction === "up" ? index - 1 : index + 1;
    const newPriorities = [...priorities];
    const temp = newPriorities[index];
    newPriorities[index] = newPriorities[nextIndex];
    newPriorities[nextIndex] = temp;
    setPriorities(newPriorities);
  };

  // Parser helper to add extra budget expansion when clicking smart suggestions
  const handleExpansionClick = (suggestionText: string) => {
    const match = suggestionText.match(/(\d+)\s*INR/i) || suggestionText.match(/extra\s*(\d+)/i) || suggestionText.match(/₹\s*(\d+)/i);
    if (match && match[1]) {
      const extraAmount = parseInt(match[1]);
      setSpecifyBudget(true);
      setTotalBudget(prev => prev + extraAmount);
    }
  };

  // Helper function to dynamically slice or pad itinerary list based on Trip Duration slider
  const getDynamicItinerary = (itineraryList: any[], type: "group" | "solo" | "reunion", travelerName?: string) => {
    if (!itineraryList || itineraryList.length === 0) return [];
    
    // If specifyDays is false, use the full list as is
    const targetDays = specifyDays ? numDays : itineraryList.length;
    
    // If we have enough or more days in the list, slice it
    if (itineraryList.length >= targetDays) {
      return itineraryList.slice(0, targetDays);
    }
    
    // If we need more days, start with the existing list
    const result = [...itineraryList];
    const lastDayNum = itineraryList.length;
    
    // Generate additional days up to targetDays
    for (let i = lastDayNum + 1; i <= targetDays; i++) {
      const dayActivities = [];
      const destName = (destinationPreference || "Goa").toLowerCase();
      
      let activityName = "Explore Local Sights";
      let desc = "Enjoy self-guided leisure sightseeing and local food trail.";
      let cost = 400;
      
      if (destName === "goa") {
        activityName = i % 2 === 0 ? "Baga Beach Water Sports" : "Basilica of Bom Jesus Visit";
        desc = i % 2 === 0 ? "Enjoy jet ski rides, parasailing, and beach shacks." : "Explore historical Portuguese churches and local heritage.";
        cost = i % 2 === 0 ? 1200 : 200;
      } else if (destName === "jaipur") {
        activityName = i % 2 === 0 ? "Amer Fort Elephant/Jeep Ride" : "Johari Bazaar Shopping Tour";
        desc = i % 2 === 0 ? "Visit the majestic fort and experience local royal views." : "Shop for traditional gems, textiles, and authentic local street food.";
        cost = i % 2 === 0 ? 800 : 500;
      } else if (destName === "srinagar") {
        activityName = i % 2 === 0 ? "Shalimar Bagh Mughal Garden Walk" : "Dal Lake floating market cruise";
        desc = i % 2 === 0 ? "Stroll through royal gardens overlooking the lake." : "Take a serene Shikara ride and explore floating craft markets.";
        cost = i % 2 === 0 ? 150 : 400;
      } else { // bangalore
        activityName = i % 2 === 0 ? "Cubbon Park morning stroll & filter coffee" : "Visvesvaraya Museum & local pub hop";
        desc = i % 2 === 0 ? "Enjoy greenery in the heart of the city followed by traditional South Indian breakfast." : "Interactive science exhibits followed by exploring the microbrewery hub.";
        cost = i % 2 === 0 ? 250 : 900;
      }
      
      if (type === "group" || type === "reunion") {
        dayActivities.push({
          time: "Morning (10:00 AM - 1:00 PM)",
          activity_name: activityName,
          description: desc,
          estimated_cost: cost,
          fatigue_level: 2,
          assigned_to: ["All"]
        });
        dayActivities.push({
          time: "Evening (6:00 PM - 9:00 PM)",
          activity_name: type === "reunion" ? "Group Dinner & Stories sharing" : "Leisure local market exploration",
          description: type === "reunion" ? "The group gathers together at a popular local restaurant for bonding." : "Explore nearby streets and street food stalls.",
          estimated_cost: 300,
          fatigue_level: 1,
          assigned_to: ["All"]
        });
      } else { // solo
        dayActivities.push({
          time: "Afternoon (2:30 PM - 5:30 PM)",
          activity_name: `${activityName} (Individual Track)`,
          description: `Conflict Resolver: Custom track planned for ${travelerName} to match their ${travelerName ? travelers.find(t => t.name === travelerName)?.vibe_preference : 'nature'} vibe preference.`,
          estimated_cost: cost,
          fatigue_level: 2,
          assigned_to: [travelerName || "All"]
        });
      }
      
      result.push({
        day: i,
        activities: dayActivities
      });
    }
    return result;
  };
  
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

  // Handle Budget/Days variation via simulation sliders and expectations
  useEffect(() => {
    if (serverStatus === "online" && destinations.length > 0) {
      triggerSimulationUpdate();
    }
  }, [totalBudget, numDays, travelers, specifyBudget, specifyDays, expectations, preferredVibe, destinationPreference]);

  // Trigger real-time simulation slider update
  const triggerSimulationUpdate = async () => {
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
          budget_preference: t.budget_preference,
          vibe_preference: t.vibe_preference,
          accommodation_preference: t.accommodation_preference,
          travel_style: t.travel_style
        })),
        budget: specifyBudget ? totalBudget : 100000, // send standard placeholder if ignored
        days: specifyDays ? numDays : 3,
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

      // Update crewAIResult values dynamically using simulate endpoint
      if (crewAIResult) {
        const simPayload = travelers.map(t => ({
          name: t.name,
          age: t.age,
          medical_conditions: t.medical_conditions,
          vibe_preference: t.vibe_preference || preferredVibe,
          accommodation_preference: t.accommodation_preference,
          travel_style: t.travel_style,
          travel_purpose: t.travel_purpose,
          food_preference: t.food_preference
        }));

        const simUrl = `http://127.0.0.1:8000/recommendation/simulate?destination=${encodeURIComponent(destinationPreference)}&target_budget=${specifyBudget ? totalBudget : 100000}&num_days=${specifyDays ? numDays : 3}`;
        const simRes = await fetch(simUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(simPayload)
        });
        if (simRes.ok) {
          const simData = await simRes.json();
          setCrewAIResult((prev: any) => {
            if (!prev) return prev;
            return {
              ...prev,
              budget_analysis: simData.updated_budget_allocation,
              group_compatibility_score: simData.compatibility_score,
              smart_budget_expansions: simData.suggested_upgrades,
            };
          });
        }
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
        budget: specifyBudget ? totalBudget : 100000,
        days: specifyDays ? numDays : 3,
        preferred_vibe: preferredVibe,
        priorities: priorities,
        destination_preference: mainTab === "planned" ? destinationPreference : null,
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
          travel_purpose: t.travel_purpose,
          food_preference: t.food_preference
        })),
        total_budget: specifyBudget ? totalBudget : null,
        num_days: specifyDays ? numDays : null,
        expectations: expectations,
        destination_preference: mainTab === "planned" ? destinationPreference : null,
        hotel_count: hotelCount,
        priorities: priorities
      };

      const crewRes = await fetch("http://127.0.0.1:8000/recommendation/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(crewPayload)
      });

      if (crewRes.ok) {
        const crewData = await crewRes.json();
        setCrewAIResult(crewData);
        // Sync tab view to group
        setActiveTab("group");
        if (travelers.length > 0) {
          setSelectedSoloTraveler(travelers[0].name);
        }
        // If in autopilot mode, set the auto-detected destination preference
        if (mainTab === "autopilot" && crewData && crewData.destination_name) {
          const matchedDest = crewData.destination_name;
          setDestinationPreference(matchedDest.charAt(0).toUpperCase() + matchedDest.slice(1).toLowerCase());
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
    
    setTimeout(() => {
      triggerSimulationUpdate();
    }, 100);
  };

  return (
    <div className="min-h-screen p-4 md:p-8 flex flex-col gap-6 select-none animate-lazy-fade bg-[#FAFAF8]">
      
      {/* HEADER BAR */}
      <header className="glass-card-blue p-4 md:p-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <Plane className="w-8 h-8" style={{ color: 'var(--primary)' }} />
          <div>
            <h1 className="text-2xl font-bold text-[#1A1A2E]">
              TripMind AI
            </h1>
            <p className="text-sm text-[#4A4A68]">Plan group trips, manage conflicts, explore destinations</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full border" style={{ borderColor: 'var(--card-border)', backgroundColor: 'var(--card-bg)' }}>
            <span className={`h-2.5 w-2.5 rounded-full ${serverStatus === "online" ? "bg-green-500" : "bg-red-500"}`}></span>
            <span className="text-sm font-medium text-[#4A4A68]">
              {serverStatus === "online" ? "Engine Online" : "Engine Offline"}
            </span>
          </div>
          {serverStatus === "offline" && (
            <button
              onClick={checkServerStatus}
              className="px-4 py-2 rounded-lg border-2" 
              style={{ borderColor: 'var(--primary)', color: 'var(--primary)', backgroundColor: 'transparent' }}
            >
              Connect
            </button>
          )}
        </div>
      </header>

      {/* MODE TOGGLE: Plan a Trip / Vibe Autopilot */}
      <div className="flex gap-2 p-2 rounded-lg max-w-md mx-auto w-full" style={{ backgroundColor: 'var(--background)' }}>
        <button
          onClick={() => setMainTab("planned")}
          className={`flex-1 py-3 px-4 font-semibold rounded-lg transition-all text-sm ${mainTab === "planned" 
            ? "text-white" 
            : "text-[#4A4A68]"}`}
          style={{ 
            backgroundColor: mainTab === "planned" ? 'var(--primary)' : 'transparent',
            color: mainTab === "planned" ? 'white' : 'var(--muted)',
          }}
        >
          Plan a Trip
        </button>
        <button
          onClick={() => setMainTab("autopilot")}
          className={`flex-1 py-3 px-4 font-semibold rounded-lg transition-all text-sm ${mainTab === "autopilot" 
            ? "text-white" 
            : "text-[#4A4A68]"}`}
          style={{ 
            backgroundColor: mainTab === "autopilot" ? 'var(--primary)' : 'transparent',
            color: mainTab === "autopilot" ? 'white' : 'var(--muted)',
          }}
        >
          Vibe Autopilot
        </button>
      </div>

      {/* MAIN DASHBOARD CONTAINER */}
      <main className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        
        {/* LEFT PANEL: TRAVELER PROFILES & JOURNEY SPECS */}
        <section className="xl:col-span-4 flex flex-col gap-6">
          <div className="glass-card-blue p-6 flex flex-col gap-5">
            <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
              <User size={20} style={{ color: 'var(--primary)' }} />
              <h2 className="text-lg font-bold text-[#1A1A2E]">Traveler Profiles</h2>
            </div>

            {/* Number of People Slider */}
            <div className="flex flex-col gap-3 p-4 rounded-lg" style={{ backgroundColor: 'var(--background)' }}>
              <div className="flex justify-between items-center text-sm">
                <label className="font-semibold text-[#1A1A2E]">Number of People</label>
                <span className="font-bold text-[#FF6B35]">{numPeople} travelers</span>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="1"
                  max="8"
                  step="1"
                  value={numPeople}
                  onChange={(e) => setNumPeople(parseInt(e.target.value))}
                  className="w-full h-1.5 rounded-lg accent-[#006CE4] cursor-pointer"
                />
                <input
                  type="number"
                  min="1"
                  max="8"
                  value={numPeople}
                  onChange={(e) => setNumPeople(Math.max(1, Math.min(8, parseInt(e.target.value) || 1)))}
                  className="neu-input-inset w-16 px-2 py-2 text-center text-sm"
                />
              </div>
            </div>

            {/* Travelers List */}
            <div className="flex flex-col gap-3 max-h-[350px] overflow-y-auto pr-1">
              {travelers.map((traveler, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-lg border-l-4 transition-all" 
                  style={{ borderColor: 'var(--primary)', backgroundColor: '#EEF4FF' }}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <input
                        type="text"
                        value={traveler.name}
                        onChange={(e) => updateTraveler(idx, "name", e.target.value)}
                        className="neu-input-inset w-full px-3 py-2 text-sm font-semibold text-[#1A1A2E] mb-2"
                        placeholder="Traveler name"
                      />
                    </div>
                    {travelers.length > 1 && (
                      <button
                        onClick={() => removeTraveler(idx)}
                        className="text-red-500 hover:text-red-700 text-sm font-medium ml-2 flex-shrink-0"
                      >
                        Remove
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {/* Age */}
                    <div>
                      <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Age</label>
                      <input
                        type="number"
                        value={traveler.age}
                        onChange={(e) => updateTraveler(idx, "age", parseInt(e.target.value) || 0)}
                        className="neu-input-inset w-full px-2 py-2 text-xs"
                      />
                    </div>
                    {/* Food Preference */}
                    <div>
                      <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Diet</label>
                      <select
                        value={traveler.food_preference}
                        onChange={(e) => updateTraveler(idx, "food_preference", e.target.value)}
                        className="neu-input-inset w-full px-2 py-2 text-xs"
                      >
                        <option value="veg">Vegetarian</option>
                        <option value="non-veg">Non-Vegetarian</option>
                        <option value="vegan">Vegan</option>
                      </select>
                    </div>
                    {/* Vibe */}
                    <div>
                      <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Vibe</label>
                      <select
                        value={traveler.vibe_preference}
                        onChange={(e) => updateTraveler(idx, "vibe_preference", e.target.value)}
                        className="neu-input-inset w-full px-2 py-2 text-xs"
                      >
                        <option value="beaches">Beaches</option>
                        <option value="nightlife">Nightlife</option>
                        <option value="heritage">Heritage</option>
                        <option value="spirituality">Spirituality</option>
                        <option value="nature">Nature</option>
                        <option value="cafes">Cafes</option>
                      </select>
                    </div>
                    {/* Travel Purpose */}
                    <div>
                      <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Purpose</label>
                      <select
                        value={traveler.travel_purpose}
                        onChange={(e) => updateTraveler(idx, "travel_purpose", e.target.value)}
                        className="neu-input-inset w-full px-2 py-2 text-xs"
                      >
                        <option value="relaxation">Relaxation</option>
                        <option value="adventure">Adventure</option>
                        <option value="spirituality">Spirituality</option>
                        <option value="luxury">Luxury</option>
                        <option value="family bonding">Family Bonding</option>
                        <option value="workcation">Workcation</option>
                        <option value="photography">Photography</option>
                        <option value="honeymoon">Honeymoon</option>
                      </select>
                    </div>
                    {/* Activity Level */}
                    <div>
                      <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Activity Level</label>
                      <select
                        value={traveler.activity_level}
                        onChange={(e) => updateTraveler(idx, "activity_level", e.target.value)}
                        className="neu-input-inset w-full px-2 py-2 text-xs"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>
                    {/* Budget */}
                    <div>
                      <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Budget Tier</label>
                      <select
                        value={traveler.budget_preference}
                        onChange={(e) => {
                          updateTraveler(idx, "budget_preference", e.target.value);
                          updateTraveler(idx, "accommodation_preference", e.target.value);
                        }}
                        className="neu-input-inset w-full px-2 py-2 text-xs"
                      >
                        <option value="budget">Budget</option>
                        <option value="standard">Standard</option>
                        <option value="luxury">Luxury</option>
                      </select>
                    </div>
                    {/* Travel Style */}
                    <div>
                      <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Travel Style</label>
                      <select
                        value={traveler.travel_style}
                        onChange={(e) => updateTraveler(idx, "travel_style", e.target.value)}
                        className="neu-input-inset w-full px-2 py-2 text-xs"
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
                  <div className="mt-2">
                    <label className="text-xs font-semibold text-[#4A4A68] block mb-1">Health Concerns</label>
                    <input
                      type="text"
                      placeholder="e.g., asthma, hypertension"
                      value={traveler.medical_conditions.join(", ")}
                      onChange={(e) => updateTravelerMedical(idx, e.target.value)}
                      className="neu-input-inset w-full px-2 py-2 text-xs"
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Add Traveler Button */}
            <button
              onClick={addTraveler}
              className="flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium text-sm"
              style={{ backgroundColor: 'var(--background)', color: 'var(--primary)', border: `2px solid var(--primary)` }}
            >
              <Plus size={16} /> Add Traveler
            </button>
          </div>

          {/* JOURNEY SPECIFICATIONS PANEL */}
          <div className="glass-card-blue p-6 flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
              <Compass size={20} style={{ color: 'var(--primary)' }} />
              <h2 className="text-lg font-bold text-[#1A1A2E]">Journey Specs</h2>
            </div>

            {mainTab === "planned" ? (
              <>
                {/* Destination */}
                <div>
                  <label className="text-sm font-semibold text-[#1A1A2E] block mb-2">Where would you like to go?</label>
                  <select
                    value={destinationPreference}
                    onChange={(e) => setDestinationPreference(e.target.value)}
                    className="neu-input-inset w-full px-3 py-2.5 text-sm"
                  >
                    <option value="Goa">Goa - Beaches & Nightlife</option>
                    <option value="Bangalore">Bangalore - Cafe Culture</option>
                    <option value="Srinagar">Srinagar - Scenic Mountains</option>
                    <option value="Jaipur">Jaipur - Royal Heritage</option>
                  </select>
                </div>

                {/* Expectations */}
                <div>
                  <label className="text-sm font-semibold text-[#1A1A2E] block mb-2">Your Vibe & Expectations</label>
                  <textarea
                    rows={3}
                    value={expectations}
                    onChange={(e) => setExpectations(e.target.value)}
                    placeholder="Describe what you're looking for..."
                    className="neu-input-inset w-full px-3 py-2 text-sm resize-none"
                  />
                </div>
              </>
            ) : (
              <>
                {/* Autopilot Mood */}
                <div>
                  <label className="text-sm font-semibold text-[#1A1A2E] block mb-2">What's your mood?</label>
                  <select
                    value={unsureMood}
                    onChange={(e) => setUnsureMood(e.target.value)}
                    className="neu-input-inset w-full px-3 py-2.5 text-sm"
                  >
                    <option value="peaceful weekend">Peaceful Weekend</option>
                    <option value="adventure rush">Adventure Rush</option>
                    <option value="burnout recovery">Burnout Recovery</option>
                    <option value="luxury escape">Luxury Escape</option>
                    <option value="family bonding">Family Bonding</option>
                  </select>
                </div>

                {/* Extra Details */}
                <div>
                  <label className="text-sm font-semibold text-[#1A1A2E] block mb-2">Any other preferences?</label>
                  <textarea
                    rows={3}
                    value={unsureDetails}
                    onChange={(e) => setUnsureDetails(e.target.value)}
                    placeholder="Special requests, constraints, etc..."
                    className="neu-input-inset w-full px-3 py-2 text-sm resize-none"
                  />
                </div>

                <button
                  onClick={handleUnsureRecommend}
                  className="neu-button-outset w-full py-2.5 text-sm font-semibold"
                >
                  Set Up My Itinerary
                </button>
              </>
            )}

            {/* Priorities */}
            <div className="flex flex-col gap-2 pt-2 mt-2 border-t" style={{ borderColor: 'var(--card-border)' }}>
              <span className="text-sm font-semibold text-[#1A1A2E]">What matters most?</span>
              <div className="flex flex-col gap-2">
                {priorities.map((prio, pIdx) => (
                  <div
                    key={prio}
                    className="flex justify-between items-center p-2 rounded text-sm"
                    style={{ backgroundColor: 'var(--background)' }}
                  >
                    <span className="font-medium text-[#4A4A68]">
                      {pIdx + 1}. {prio === "vibe" ? "Destination Vibe" : prio === "budget" ? "Budget Fit" : prio === "travel_mode" ? "Travel Mode" : "Accommodation"}
                    </span>
                    <div className="flex gap-1">
                      <button
                        onClick={() => movePriority(pIdx, "up")}
                        disabled={pIdx === 0}
                        className="p-1 rounded hover:bg-white disabled:opacity-30 disabled:cursor-not-allowed"
                        style={{ backgroundColor: 'var(--card-bg)', color: 'var(--primary)' }}
                        title="Move Up"
                      >
                        <ChevronUp size={14} />
                      </button>
                      <button
                        onClick={() => movePriority(pIdx, "down")}
                        disabled={pIdx === priorities.length - 1}
                        className="p-1 rounded hover:bg-white disabled:opacity-30 disabled:cursor-not-allowed"
                        style={{ backgroundColor: 'var(--card-bg)', color: 'var(--primary)' }}
                        title="Move Down"
                      >
                        <ChevronDown size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Hotel Count */}
            <div className="flex items-center justify-between text-sm pt-2">
              <span className="font-semibold text-[#1A1A2E]">Hotel Suggestions</span>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min="3"
                  max="10"
                  step="1"
                  value={hotelCount}
                  onChange={(e) => setHotelCount(parseInt(e.target.value))}
                  className="w-24 accent-[#006CE4]"
                />
                <span className="font-bold text-[#FF6B35] w-4 text-right">{hotelCount}</span>
              </div>
            </div>

            {/* Execute Button */}
            <button
              onClick={runOrchestrator}
              disabled={isLoading || serverStatus === "offline"}
              className="neu-button-outset w-full py-3 text-base font-bold flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" /> Building Your Trip...
                </>
              ) : (
                <>
                  <Sparkles size={18} /> Build My Trip
                </>
              )}
            </button>
          </div>
        </section>


{/* CENTER PANEL: DESTINATION & VALIDATION */}
        <section className="xl:col-span-4 flex flex-col gap-6">
          <div className="glass-card-blue p-6 flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
              <Compass size={20} style={{ color: 'var(--primary)' }} />
              <h2 className="text-lg font-bold text-[#1A1A2E]">Destination Match</h2>
            </div>

            {/* Destinations List */}
            <div className="flex flex-col gap-3">
              {destinations.map((dest, idx) => {
                const score = dest.compatibility_score || 70.0;
                const isSelected = dest.name.toLowerCase() === destinationPreference.toLowerCase();
                
                return (
                  <div
                    key={idx}
                    onClick={() => {
                      setDestinationPreference(dest.name);
                      triggerSimulationUpdate();
                    }}
                    className={`p-4 rounded-lg border-2 transition-all cursor-pointer ${isSelected 
                      ? "border-[#006CE4] bg-[#EEF4FF]" 
                      : "border-[#EEEEEE] bg-white hover:border-[#006CE4]/50"}`}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-bold text-lg text-[#1A1A2E]">
                        {dest.name}
                      </span>
                      <span className="text-sm font-bold px-3 py-1 rounded-full" 
                        style={{ backgroundColor: '#EEF4FF', color: 'var(--primary)' }}>
                        {score.toFixed(0)}% match
                      </span>
                    </div>

                    <p className="text-sm text-[#4A4A68] mb-2">
                      {dest.best_for || "A great travel destination for you."}
                    </p>

                    {/* Factor scores bars */}
                    {dest.factor_scores && (
                      <div className="grid grid-cols-4 gap-2 text-xs">
                        {Object.entries(dest.factor_scores).slice(0, 4).map(([key, val]: any) => (
                          <div key={key}>
                            <div className="text-[#4A4A68] text-[10px] font-semibold truncate mb-1">{key.replace("_", " ")}</div>
                            <div className="w-full bg-[#EEEEEE] h-1.5 rounded-full overflow-hidden">
                              <div className="bg-[#006CE4] h-full rounded-full" style={{ width: `${val}%` }}></div>
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

          {/* Expectation Validation */}
          {tripValidation && (
            <div className="glass-card-blue p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
                <Info size={20} style={{ color: 'var(--primary)' }} />
                <h2 className="text-lg font-bold text-[#1A1A2E]">Compatibility Check</h2>
              </div>

              <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--background)' }}>
                <div className="text-sm text-[#4A4A68] mb-2">Experience Overlap</div>
                <div className="text-3xl font-bold text-[#006CE4]">
                  {tripValidation.compatibility_score}%
                </div>
              </div>

              {/* Reasons */}
              <div className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#1A1A2E]">Why this destination?</span>
                <ul className="flex flex-col gap-2">
                  {tripValidation.reasons?.map((reason: string, idx: number) => (
                    <li key={idx} className="text-sm text-[#4A4A68] flex items-start gap-2">
                      <Check size={16} style={{ color: 'var(--primary)', marginTop: '2px', flexShrink: 0 }} />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Upgrade Recommendation */}
              <div className="p-3 rounded-lg" style={{ backgroundColor: '#FFF4E6' }}>
                <p className="text-sm text-[#FF6B35]">
                  <strong>💡 Pro Tip:</strong> Increasing your budget by ₹2,000 can unlock premium activities in {destinationPreference}.
                </p>
              </div>
            </div>
          )}

          {/* Group Compatibility */}
          {crewAIResult && (
            <div className="glass-card-blue p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
                <Heart size={20} style={{ color: 'var(--primary)' }} />
                <h2 className="text-lg font-bold text-[#1A1A2E]">Group Harmony</h2>
              </div>

              <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--background)' }}>
                <div className="text-sm text-[#4A4A68] mb-2">Group Compatibility</div>
                <div className="text-3xl font-bold text-[#006CE4]">
                  {crewAIResult.group_compatibility_score?.toFixed(1)}%
                </div>
              </div>

              {/* AI Insights */}
              <div className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#1A1A2E]">Our Analysis</span>
                <ul className="flex flex-col gap-2">
                  {crewAIResult.explainable_ai_reasons?.map((reason: string, idx: number) => (
                    <li key={idx} className="text-sm text-[#4A4A68] flex items-start gap-2">
                      <Smile size={16} style={{ color: 'var(--primary)', marginTop: '2px', flexShrink: 0 }} />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Budget Upgrades */}
              {crewAIResult.smart_budget_expansions && crewAIResult.smart_budget_expansions.length > 0 && (
                <div className="flex flex-col gap-2 pt-2 border-t" style={{ borderColor: 'var(--card-border)' }}>
                  <span className="text-sm font-semibold text-[#1A1A2E]">Enhancement Options</span>
                  {crewAIResult.smart_budget_expansions.map((exp: string, idx: number) => (
                    <div
                      key={idx}
                      onClick={() => handleExpansionClick(exp)}
                      className="p-3 rounded-lg border-2 cursor-pointer transition-all hover:border-[#006CE4]"
                      style={{ borderColor: 'var(--card-border)', backgroundColor: 'var(--background)' }}
                    >
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-[#4A4A68]">{exp}</p>
                        <ArrowUpRight size={16} style={{ color: 'var(--primary)' }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
        
        {/* RIGHT PANEL: ITINERARY & DETAILS */}
        <section className="xl:col-span-4 flex flex-col gap-6">
          
          {/* WEATHER & HEALTH ALERTS */}
          {tripValidation && (
            <div className="glass-card-blue p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
                <ShieldAlert size={20} style={{ color: '#FF6B35' }} />
                <h2 className="text-lg font-bold text-[#1A1A2E]">Important Info</h2>
              </div>

              <div className="flex flex-col gap-3">
                {tripValidation.warnings?.map((warning: string, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg border-l-4 text-sm"
                    style={{ borderColor: '#FF6B35', backgroundColor: '#FFF4E6' }}
                  >
                    <p className="text-[#FF6B35] font-medium">{warning}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ITINERARY TABS */}
          <div className="glass-card-blue p-6 flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
              <Calendar size={20} style={{ color: 'var(--primary)' }} />
              <h2 className="text-lg font-bold text-[#1A1A2E]">Itinerary</h2>
            </div>

            {/* Tab Selector */}
            <div className="flex gap-2 p-1 rounded-lg" style={{ backgroundColor: 'var(--background)' }}>
              {(["group", "solo", "reunion"] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 py-2 px-3 text-sm font-semibold rounded transition-all ${activeTab === tab 
                    ? "text-white" 
                    : "text-[#4A4A68]"}`}
                  style={{ 
                    backgroundColor: activeTab === tab ? 'var(--primary)' : 'transparent',
                    color: activeTab === tab ? 'white' : 'var(--muted)',
                  }}
                >
                  {tab === "group" ? "Group" : tab === "solo" ? "Solo" : "Reunion"}
                </button>
              ))}
            </div>

            {/* Solo Traveler Selector */}
            {activeTab === "solo" && (
              <select
                value={selectedSoloTraveler}
                onChange={(e) => setSelectedSoloTraveler(e.target.value)}
                className="neu-input-inset px-3 py-2 text-sm"
              >
                {travelers.map(t => (
                  <option key={t.name} value={t.name}>{t.name}</option>
                ))}
              </select>
            )}

            {/* Itinerary List */}
            <div className="flex flex-col gap-3 max-h-[350px] overflow-y-auto pr-1">
              {crewAIResult ? (
                <>
                  {activeTab === "group" && (
                    getDynamicItinerary(crewAIResult.group_itinerary || [], "group").map((day: any, dIdx: number) => (
                      <div key={dIdx} className="p-3 rounded-lg border" style={{ borderColor: 'var(--card-border)', backgroundColor: 'var(--background)' }}>
                        <span className="text-sm font-bold text-[#006CE4] block mb-2">Day {day.day}</span>
                        {day.activities?.map((act: any, aIdx: number) => (
                          <div key={aIdx} className="text-xs mb-2">
                            <div className="flex justify-between items-start mb-1">
                              <span className="font-semibold text-[#1A1A2E]">{act.activity_name}</span>
                              <span className="text-[#FF6B35] font-bold">₹{act.estimated_cost}</span>
                            </div>
                            <p className="text-[#4A4A68] text-[11px]">{act.description}</p>
                            <span className="text-[#9494AA] text-[10px]">{act.time}</span>
                          </div>
                        ))}
                      </div>
                    ))
                  )}

                  {activeTab === "solo" && (
                    getDynamicItinerary(crewAIResult.solo_itineraries?.[selectedSoloTraveler] || [], "solo", selectedSoloTraveler).map((day: any, dIdx: number) => (
                      <div key={dIdx} className="p-3 rounded-lg border" style={{ borderColor: 'var(--card-border)', backgroundColor: 'var(--background)' }}>
                        <span className="text-sm font-bold text-[#006CE4] block mb-2">Day {day.day}</span>
                        {day.activities?.map((act: any, aIdx: number) => (
                          <div key={aIdx} className="text-xs mb-2">
                            <div className="flex justify-between items-start mb-1">
                              <span className="font-semibold text-[#1A1A2E]">{act.activity_name}</span>
                              <span className="text-[#FF6B35] font-bold">₹{act.estimated_cost}</span>
                            </div>
                            <p className="text-[#4A4A68] text-[11px]">{act.description}</p>
                            <span className="text-[#9494AA] text-[10px]">{act.time}</span>
                          </div>
                        ))}
                      </div>
                    ))
                  )}

                  {activeTab === "reunion" && (
                    getDynamicItinerary(crewAIResult.reunion_schedule || [], "reunion").map((day: any, dIdx: number) => (
                      <div key={dIdx} className="p-3 rounded-lg border" style={{ borderColor: 'var(--card-border)', backgroundColor: 'var(--background)' }}>
                        <span className="text-sm font-bold text-[#006CE4] block mb-2">Day {day.day} - Group</span>
                        {day.activities?.map((act: any, aIdx: number) => (
                          <div key={aIdx} className="text-xs mb-2">
                            <div className="flex justify-between items-start mb-1">
                              <span className="font-semibold text-[#1A1A2E]">{act.activity_name}</span>
                              <span className="text-[#FF6B35] font-bold">₹{act.estimated_cost}</span>
                            </div>
                            <p className="text-[#4A4A68] text-[11px]">{act.description}</p>
                            <span className="text-[#9494AA] text-[10px]">{act.time}</span>
                          </div>
                        ))}
                      </div>
                    ))
                  )}

                  {crewAIResult.conflict_resolution_summary && (
                    <div className="p-3 rounded-lg border text-xs" style={{ borderColor: 'var(--card-border)', backgroundColor: '#EEF4FF' }}>
                      <strong className="text-[#006CE4]">Conflict Resolution:</strong>
                      <p className="text-[#4A4A68] mt-1">{crewAIResult.conflict_resolution_summary}</p>
                    </div>
                  )}
                </>
              ) : (
                <div className="p-4 rounded-lg text-center text-sm text-[#4A4A68]" style={{ backgroundColor: 'var(--background)' }}>
                  Build your trip to see the itinerary
                </div>
              )}
            </div>
          </div>

          {/* HOTELS */}
          {crewAIResult?.hotels && crewAIResult.hotels.length > 0 && (
            <div className="glass-card-blue p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
                <Heart size={20} style={{ color: 'var(--primary)' }} />
                <h2 className="text-lg font-bold text-[#1A1A2E]">Accommodations</h2>
              </div>

              <div className="flex flex-col gap-3 max-h-[320px] overflow-y-auto pr-1">
                {(() => {
                  const accomCost = (specifyBudget ? totalBudget : 100000) * 0.45;
                  const nightlyAllowance = accomCost / Math.max(1, numDays);
                  return crewAIResult.hotels.map((hotel: any, hIdx: number) => {
                    const fitsBudget = hotel.price_per_night <= nightlyAllowance;
                    return (
                      <div key={hIdx} className="p-3 rounded-lg border text-sm" 
                        style={{ 
                          borderColor: fitsBudget ? 'var(--card-border)' : '#FF6B35',
                          backgroundColor: fitsBudget ? 'white' : '#FFF4E6'
                        }}>
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-bold text-[#1A1A2E]">{hotel.name}</div>
                            <div className="text-xs text-[#4A4A68] mt-1">
                              ₹{hotel.price_per_night.toLocaleString()}/night • ★ {hotel.rating}
                            </div>
                          </div>
                          <span className="text-xs font-bold px-2 py-1 rounded" 
                            style={{ 
                              backgroundColor: fitsBudget ? '#EEF4FF' : '#FFE8E0',
                              color: fitsBudget ? 'var(--primary)' : '#FF6B35'
                            }}>
                            {fitsBudget ? "In Budget" : `+₹${Math.round(hotel.price_per_night - nightlyAllowance)}`}
                          </span>
                        </div>
                        
                        {hotel.amenities && hotel.amenities.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {hotel.amenities.slice(0, 3).map((am: string, aIdx: number) => (
                              <span key={aIdx} className="text-[10px] px-2 py-0.5 rounded" 
                                style={{ backgroundColor: 'var(--background)', color: 'var(--muted)' }}>
                                {am}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  });
                })()}
              </div>
            </div>
          )}

          {/* BUDGET BREAKDOWN */}
          {crewAIResult?.budget_analysis && (
            <div className="glass-card-blue p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
                <DollarSign size={20} style={{ color: 'var(--primary)' }} />
                <h2 className="text-lg font-bold text-[#1A1A2E]">Budget Plan</h2>
              </div>

              <div className="flex flex-col gap-3 text-sm">
                <div className="flex justify-between items-center py-2 border-b" style={{ borderColor: 'var(--card-border)' }}>
                  <span className="text-[#4A4A68]">Accommodation</span>
                  <span className="font-bold text-[#FF6B35]">₹{crewAIResult.budget_analysis.accommodation_cost.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b" style={{ borderColor: 'var(--card-border)' }}>
                  <span className="text-[#4A4A68]">Activities</span>
                  <span className="font-bold text-[#FF6B35]">₹{crewAIResult.budget_analysis.activities_cost.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-[#4A4A68]">Contingency</span>
                  <span className="font-bold text-[#FF6B35]">₹{crewAIResult.budget_analysis.buffer_amount.toLocaleString()}</span>
                </div>
                <p className="text-xs text-[#4A4A68] mt-2">
                  {crewAIResult.budget_analysis.explanation}
                </p>
              </div>
            </div>
          )}

        </section>

      </main>

      {/* SIMULATION PANEL */}
      <section className="glass-card-blue p-6 flex flex-col gap-4">
        <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
          <Compass size={20} style={{ color: 'var(--primary)' }} />
          <h2 className="text-lg font-bold text-[#1A1A2E]">Trip Simulator</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Budget Simulator */}
          <div className="flex flex-col gap-3 p-4 rounded-lg" style={{ backgroundColor: 'var(--background)' }}>
            <label className="flex items-center gap-2 text-sm font-semibold text-[#1A1A2E] cursor-pointer">
              <input
                type="checkbox"
                checked={specifyBudget}
                onChange={(e) => setSpecifyBudget(e.target.checked)}
                className="w-4 h-4 rounded accent-[#006CE4]"
              />
              Specify Budget
            </label>
            {specifyBudget && (
              <>
                <input
                  type="range"
                  min="5000"
                  max="200000"
                  step="2000"
                  value={totalBudget}
                  onChange={(e) => setTotalBudget(parseInt(e.target.value))}
                  className="w-full accent-[#006CE4]"
                />
                <div className="text-right text-lg font-bold text-[#FF6B35]">
                  ₹{totalBudget.toLocaleString()}
                </div>
              </>
            )}
          </div>

          {/* Days Simulator */}
          <div className="flex flex-col gap-3 p-4 rounded-lg" style={{ backgroundColor: 'var(--background)' }}>
            <label className="flex items-center gap-2 text-sm font-semibold text-[#1A1A2E] cursor-pointer">
              <input
                type="checkbox"
                checked={specifyDays}
                onChange={(e) => setSpecifyDays(e.target.checked)}
                className="w-4 h-4 rounded accent-[#006CE4]"
              />
              Specify Duration
            </label>
            {specifyDays && (
              <>
                <input
                  type="range"
                  min="1"
                  max="15"
                  step="1"
                  value={numDays}
                  onChange={(e) => setNumDays(parseInt(e.target.value))}
                  className="w-full accent-[#006CE4]"
                />
                <div className="text-right text-lg font-bold text-[#006CE4]">
                  {numDays} days
                </div>
              </>
            )}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="text-center text-sm text-[#4A4A68] py-4">
        TripMind AI • Powered by CrewAI • Multi-Agent Trip Planning
      </footer>
    </div>
  );
}
