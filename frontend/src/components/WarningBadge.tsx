import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle, HelpCircle, Flame } from 'lucide-react';

interface WarningBadgeProps {
  warning: string;
}

export const WarningBadge: React.FC<WarningBadgeProps> = ({ warning }) => {
  // Determine warning type
  const isSafe = warning.toLowerCase().includes('no specific') || warning.toLowerCase().includes('no major');
  const isAsthma = warning.toLowerCase().includes('asthma') || warning.toLowerCase().includes('respiratory');
  const isHeart = warning.toLowerCase().includes('hypertension') || warning.toLowerCase().includes('heart') || warning.toLowerCase().includes('medical alert');
  const isMobility = warning.toLowerCase().includes('mobility') || warning.toLowerCase().includes('joint') || warning.toLowerCase().includes('knee') || warning.toLowerCase().includes('elderly') || warning.toLowerCase().includes('senior');
  const isBudget = warning.toLowerCase().includes('budget');

  let config = {
    title: 'Alert',
    icon: AlertTriangle,
    bgClass: 'bg-amber-500/10 border-amber-500/30 text-amber-300 shadow-[0_0_15px_rgba(245,158,11,0.08)]',
    iconClass: 'text-amber-400'
  };

  if (isSafe) {
    config = {
      title: 'System Clear',
      icon: CheckCircle,
      bgClass: 'bg-teal-500/10 border-teal-500/30 text-teal-300 shadow-[0_0_15px_rgba(20,184,166,0.08)]',
      iconClass: 'text-teal-400'
    };
  } else if (isHeart) {
    config = {
      title: 'Critical Medical',
      icon: ShieldAlert,
      bgClass: 'bg-rose-500/10 border-rose-500/30 text-rose-300 shadow-[0_0_15px_rgba(244,63,94,0.08)]',
      iconClass: 'text-rose-400'
    };
  } else if (isAsthma) {
    config = {
      title: 'Climate Risk',
      icon: Flame,
      bgClass: 'bg-purple-500/10 border-purple-500/30 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.08)]',
      iconClass: 'text-purple-400'
    };
  } else if (isMobility) {
    config = {
      title: 'Mobility Constraint',
      icon: AlertTriangle,
      bgClass: 'bg-amber-500/10 border-amber-500/30 text-amber-300 shadow-[0_0_15px_rgba(245,158,11,0.08)]',
      iconClass: 'text-amber-400'
    };
  } else if (isBudget) {
    config = {
      title: 'Budget Mismatch',
      icon: HelpCircle,
      bgClass: 'bg-sky-500/10 border-sky-500/30 text-sky-300 shadow-[0_0_15px_rgba(14,165,233,0.08)]',
      iconClass: 'text-sky-400'
    };
  }

  const Icon = config.icon;

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border text-sm font-sans leading-relaxed transition-all duration-300 ${config.bgClass}`}>
      <div className="flex-shrink-0 mt-0.5">
        <Icon className={`w-4 h-4 ${config.iconClass}`} />
      </div>
      <div className="flex-grow">
        <span className="font-orbitron font-extrabold uppercase text-[10px] tracking-widest block mb-1">
          {config.title}
        </span>
        <span className="text-slate-300 text-xs md:text-sm font-medium">{warning}</span>
      </div>
    </div>
  );
};
