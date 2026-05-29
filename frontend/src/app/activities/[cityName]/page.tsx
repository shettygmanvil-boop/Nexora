'use client';

import * as React from 'react';
import { use, useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, Compass, Search, Heart, Sparkles, Filter, 
  CheckCircle2, X, Star, Clock, MapPin, AlertCircle, Share2
} from 'lucide-react';
import { ActivityCard } from '../../../components/ActivityCard';
import { activitiesData, Activity } from '../activityData';

interface PageProps {
  params: Promise<{ cityName: string }>;
}

const CATEGORIES: ('All' | Activity['category'])[] = [
  'All',
  'Recommended',
  'Adventure',
  'Food & Workshops',
  'Family',
  'Hidden Gems',
  'Nightlife'
];

export default function ActivitiesPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const rawCityName = resolvedParams.cityName;
  const decodedCityName = decodeURIComponent(rawCityName);

  // Match case-insensitively or fallback
  const cityKey = Object.keys(activitiesData).find(
    (key) => key.toLowerCase() === decodedCityName.toLowerCase()
  ) || 'Goa';

  const activities = activitiesData[cityKey] || [];

  // Local State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<'All' | Activity['category']>('All');
  const [wishlist, setWishlist] = useState<string[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [bookingSuccess, setBookingSuccess] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string>('');

  // Hydrate Wishlist from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('maproom_activities_wishlist');
      if (saved) {
        setWishlist(JSON.parse(saved));
      }
    } catch (e) {
      console.error('Failed to load wishlist:', e);
    }
  }, []);

  const handleWishlistToggle = (activityId: string) => {
    let updated: string[];
    if (wishlist.includes(activityId)) {
      updated = wishlist.filter(id => id !== activityId);
      showToast('Removed from wishlist');
    } else {
      updated = [...wishlist, activityId];
      showToast('Added to wishlist!');
    }
    setWishlist(updated);
    try {
      localStorage.setItem('maproom_activities_wishlist', JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to save wishlist:', e);
    }
  };

  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => {
      setToastMessage('');
    }, 2500);
  };

  const handleBookDemo = () => {
    setBookingSuccess(true);
    setTimeout(() => {
      setBookingSuccess(false);
      setSelectedActivity(null);
      showToast('Booking simulated successfully!');
    }, 1800);
  };

  // Filtering Logic
  const filteredActivities = activities.filter((act) => {
    const matchesSearch = 
      act.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      act.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      act.location.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = 
      selectedCategory === 'All' || act.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // Group by category for rendering sections
  const groupedActivities = CATEGORIES.reduce((acc, cat) => {
    if (cat === 'All') return acc;
    const catActs = filteredActivities.filter(act => act.category === cat);
    if (catActs.length > 0) {
      acc[cat] = catActs;
    }
    return acc;
  }, {} as Record<string, Activity[]>);

  return (
    <div className="relative min-h-screen bg-[#030712] text-slate-100 font-sans pb-20 selection:bg-teal-500/30 selection:text-teal-300">
      {/* Background glow effects */}
      <div className="fixed inset-0 cyber-grid opacity-30 pointer-events-none z-0"></div>
      <div className="fixed top-0 left-0 w-full h-[500px] bg-gradient-to-b from-indigo-950/10 via-transparent to-transparent pointer-events-none z-0"></div>
      <div className="fixed top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-teal-500/25 to-transparent animate-scan pointer-events-none z-10"></div>

      {/* Navbar Header */}
      <nav className="fixed top-0 left-0 right-0 z-40 glass-panel border-b border-white/5 px-6 py-4 flex items-center justify-between">
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
              Explore Experiences
            </span>
          </div>
        </div>

        <Link
          href="/"
          className="flex items-center gap-2 px-4 py-2 border border-white/10 hover:border-teal-500/30 bg-slate-900/60 rounded-xl text-xs font-orbitron font-bold uppercase tracking-wider text-slate-300 hover:text-teal-400 transition-all duration-300 shadow-md"
        >
          <ArrowLeft className="w-4 h-4 text-teal-400" />
          Back to Planner
        </Link>
      </nav>

      {/* Main Content Page */}
      <main className="relative z-15 pt-28 max-w-6xl mx-auto px-4 space-y-12">
        {/* Toast Notification */}
        {toastMessage && (
          <div className="fixed bottom-6 right-6 z-50 px-4 py-3 bg-slate-900 border border-teal-500/30 text-teal-300 rounded-xl text-xs font-orbitron font-bold uppercase tracking-wider shadow-lg flex items-center gap-2 animate-bounce">
            <Sparkles className="w-4 h-4 text-teal-400" />
            {toastMessage}
          </div>
        )}

        {/* Hero Section */}
        <div className="flex flex-col items-center text-center space-y-4 max-w-2xl mx-auto">
          <span className="font-orbitron font-extrabold text-xs tracking-widest text-teal-400 bg-teal-500/10 border border-teal-500/20 px-3 py-1 rounded-full">
            Curated Local Discovery
          </span>
          <h1 className="font-orbitron font-black text-4xl md:text-5xl text-slate-100 uppercase tracking-wide">
            {cityKey}
          </h1>
          <p className="text-sm text-slate-400 font-medium">
            Unique experiences curated for <span className="text-teal-400 font-semibold">{cityKey}</span>
          </p>

          {/* Search Bar */}
          <div className="w-full relative max-w-md mt-6">
            <Search className="absolute left-4.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search adventures, food, spots..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-slate-900/60 border border-white/5 focus:border-teal-500/40 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none transition-all duration-300 focus:shadow-[0_0_15px_rgba(20,184,166,0.1)]"
            />
          </div>

          {/* Category Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-4 w-full">
            {CATEGORIES.map((cat) => {
              const isActive = selectedCategory === cat;
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-orbitron font-extrabold uppercase tracking-wider transition-all duration-300 border focus:outline-none ${
                    isActive
                      ? 'bg-teal-500/15 border-teal-500 text-teal-300 shadow-[0_0_10px_rgba(20,184,166,0.15)]'
                      : 'bg-slate-900/40 border-white/5 text-slate-400 hover:text-slate-200 hover:border-white/10'
                  }`}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        </div>

        {/* Activity Listing Grid */}
        <div className="space-y-12">
          {filteredActivities.length === 0 ? (
            <div className="text-center py-20 glass-panel rounded-2xl border border-white/5 max-w-md mx-auto space-y-4">
              <AlertCircle className="w-12 h-12 text-indigo-400 mx-auto animate-pulse" />
              <div className="space-y-1">
                <h4 className="font-orbitron font-extrabold text-sm text-slate-300 uppercase tracking-widest">
                  No Activities Found
                </h4>
                <p className="text-xs text-slate-500">
                  Try adjusting your search filters or typing another keyword.
                </p>
              </div>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('All');
                }}
                className="px-4 py-2 border border-white/10 hover:border-teal-500/30 bg-slate-900/60 rounded-xl text-[10px] font-orbitron font-bold uppercase tracking-wider text-slate-300 hover:text-teal-400 transition-all duration-300"
              >
                Reset Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
              {filteredActivities.map((act) => (
                <ActivityCard
                  key={act.id}
                  activity={act}
                  isWishlisted={wishlist.includes(act.id)}
                  onWishlistToggle={() => handleWishlistToggle(act.id)}
                  onViewDetails={() => setSelectedActivity(act)}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* View Details Popup Modal */}
      {selectedActivity && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-lg rounded-2xl border border-teal-500/20 overflow-hidden relative shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            {/* Close Button */}
            <button
              onClick={() => {
                if (!bookingSuccess) setSelectedActivity(null);
              }}
              className="absolute top-4 right-4 p-2 rounded-xl bg-slate-950/60 border border-white/5 text-slate-400 hover:text-slate-200 transition-all duration-300 focus:outline-none z-10"
              disabled={bookingSuccess}
            >
              <X className="w-4 h-4" />
            </button>

            {/* Real Image Header with Dark Overlay */}
            <div className="h-48 relative flex items-end p-6 border-b border-white/5 overflow-hidden">
              <img
                src={selectedActivity.imageUrl}
                alt={selectedActivity.title}
                className="absolute inset-0 w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/50 to-transparent"></div>
              <div className="absolute inset-0 cyber-grid opacity-15 pointer-events-none"></div>
              
              <div className="relative space-y-1 z-10">
                <span className="px-2.5 py-0.5 rounded bg-slate-950/80 border border-white/10 text-[8px] font-orbitron font-extrabold uppercase tracking-widest text-teal-400 inline-block">
                  {selectedActivity.category}
                </span>
                <h3 className="font-orbitron font-black text-xl text-slate-100 uppercase tracking-wide">
                  {selectedActivity.title}
                </h3>
              </div>
            </div>

            {/* Details Content */}
            <div className="p-6 space-y-6">
              {/* Metagrid info */}
              <div className="grid grid-cols-3 gap-2">
                <div className="p-3 bg-slate-900 border border-white/5 rounded-xl text-center space-y-1">
                  <MapPin className="w-4 h-4 text-teal-400 mx-auto" />
                  <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-widest block">Location</span>
                  <span className="text-xs text-slate-200 font-semibold truncate block">{selectedActivity.location}</span>
                </div>
                <div className="p-3 bg-slate-900 border border-white/5 rounded-xl text-center space-y-1">
                  <Clock className="w-4 h-4 text-indigo-400 mx-auto" />
                  <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-widest block">Duration</span>
                  <span className="text-xs text-slate-200 font-semibold truncate block">{selectedActivity.duration}</span>
                </div>
                <div className="p-3 bg-slate-900 border border-white/5 rounded-xl text-center space-y-1">
                  <Star className="w-4 h-4 text-amber-400 mx-auto fill-amber-400/20" />
                  <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-widest block">Rating</span>
                  <span className="text-xs text-slate-200 font-semibold truncate block">★ {selectedActivity.rating}</span>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-1">
                <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-widest block">About Experience</span>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  {selectedActivity.description}
                </p>
              </div>

              {/* Demo Highlight Checklist */}
              <div className="space-y-2">
                <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-widest block font-orbitron">Highlights included</span>
                <div className="grid grid-cols-1 gap-1.5 text-xs text-slate-400">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
                    <span>Certified guides and safety gear included</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
                    <span>Traditional meals/refreshments provided where applicable</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
                    <span>Free cancellation up to 24 hours in advance</span>
                  </div>
                </div>
              </div>

              {/* Price & Action Row */}
              <div className="flex items-center justify-between border-t border-white/5 pt-4">
                <div className="flex flex-col">
                  <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-widest">Estimated cost</span>
                  <span className="font-orbitron font-black text-xl text-teal-400 text-glow-teal">₹{selectedActivity.price.toLocaleString()}</span>
                </div>

                <button
                  type="button"
                  onClick={handleBookDemo}
                  className="px-6 py-2.5 bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 text-slate-950 font-orbitron font-black text-xs uppercase tracking-widest rounded-xl transition-all duration-300 shadow-[0_0_15px_rgba(20,184,166,0.2)] disabled:opacity-50 flex items-center gap-2"
                  disabled={bookingSuccess}
                >
                  {bookingSuccess ? (
                    <>
                      <Compass className="w-4 h-4 text-slate-950 animate-spin" />
                      Reserving...
                    </>
                  ) : (
                    <>
                      Reserve Spot
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
