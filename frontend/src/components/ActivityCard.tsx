import React from 'react';
import { motion } from 'framer-motion';
import { Star, Clock, MapPin, Heart, Info } from 'lucide-react';
import { Activity } from '../app/activities/activityData';

interface ActivityCardProps {
  activity: Activity;
  isWishlisted: boolean;
  onWishlistToggle: () => void;
  onViewDetails: () => void;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({
  activity,
  isWishlisted,
  onWishlistToggle,
  onViewDetails,
}) => {
  const { title, category, rating, duration, price, location, description, gradient, imageUrl } = activity;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
      className="glass-panel rounded-2xl border border-white/5 overflow-hidden flex flex-col justify-between hover:border-teal-500/20 transition-all duration-300 shadow-lg relative group w-full h-full min-h-[440px]"
    >
      <div>
        {/* Visual Image Header */}
        <div className="h-44 relative flex items-center justify-center overflow-hidden border-b border-white/5">
          <img
            src={imageUrl}
            alt={title}
            className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            loading="lazy"
          />
          {/* Dark Overlay for readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
          
          {/* Subtle grid pattern overlay */}
          <div className="absolute inset-0 cyber-grid opacity-15 pointer-events-none"></div>
          
          {/* Category Chip */}
          <span className="absolute top-4 left-4 px-2.5 py-1 rounded bg-slate-950/80 border border-white/10 text-[9px] font-orbitron font-extrabold uppercase tracking-widest text-slate-300 z-10">
            {category}
          </span>

          {/* Wishlist Heart Icon */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onWishlistToggle();
            }}
            className="absolute top-3 right-3 p-2 rounded-xl bg-slate-950/80 border border-white/10 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition-all duration-300 focus:outline-none z-10"
            title={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
          >
            <Heart
              className={`w-4 h-4 transition-all duration-300 ${
                isWishlisted ? 'fill-rose-500 text-rose-500 drop-shadow-[0_0_8px_rgba(225,29,72,0.6)] scale-110' : 'text-slate-400'
              }`}
            />
          </button>
        </div>

        {/* Card Content */}
        <div className="p-5 space-y-3">
          {/* Rating and Location Row */}
          <div className="flex items-center justify-between text-[10px] text-slate-400 font-semibold tracking-wide">
            <div className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-teal-400" />
              <span>{location}</span>
            </div>
            <div className="flex items-center gap-1 bg-slate-900 px-2 py-0.5 rounded border border-white/5">
              <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
              <span className="text-slate-200">{rating.toFixed(1)}</span>
            </div>
          </div>

          {/* Title */}
          <h4 className="font-orbitron font-extrabold text-sm md:text-base text-slate-100 line-clamp-1 uppercase tracking-wide group-hover:text-teal-400 transition-colors duration-300">
            {title}
          </h4>

          {/* Description */}
          <p className="text-xs text-slate-400 font-sans leading-relaxed line-clamp-3">
            {description}
          </p>
        </div>
      </div>

      {/* Footer Info & Actions */}
      <div className="p-5 pt-0 space-y-3">
        <div className="flex items-center justify-between border-t border-white/5 pt-3">
          {/* Duration */}
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-semibold">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>{duration}</span>
          </div>

          {/* Price */}
          <div className="font-orbitron font-black text-xs text-teal-400 flex items-center gap-0.5 bg-teal-500/5 px-2.5 py-1 rounded-lg border border-teal-500/15">
            ₹{price.toLocaleString()}
          </div>
        </div>

        {/* View Details Button */}
        <button
          type="button"
          onClick={onViewDetails}
          className="w-full py-2 bg-slate-900/60 border border-white/10 hover:border-teal-500/30 text-slate-300 hover:text-teal-400 rounded-xl text-xs font-orbitron font-extrabold uppercase tracking-wider transition-all duration-300 shadow-md flex items-center justify-center gap-1.5 focus:outline-none"
        >
          <Info className="w-3.5 h-3.5" />
          View Details
        </button>
      </div>
    </motion.div>
  );
};
