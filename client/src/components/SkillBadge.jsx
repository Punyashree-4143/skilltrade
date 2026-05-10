import React from 'react';
import { motion } from 'framer-motion';

const SkillBadge = ({ skill, variant = 'default', size = 'md', onClick, removable = false, onRemove }) => {
  const variants = {
    default: 'bg-gray-700 text-gray-300',
    offered: 'bg-primary/20 text-primary border border-primary/30',
    wanted: 'bg-secondary/20 text-secondary border border-secondary/30',
    technology: 'bg-blue-600/20 text-blue-400 border border-blue-600/30',
    creative: 'bg-purple-600/20 text-purple-400 border border-purple-600/30',
    business: 'bg-green-600/20 text-green-400 border border-green-600/30',
    education: 'bg-yellow-600/20 text-yellow-400 border border-yellow-600/30',
    health: 'bg-red-600/20 text-red-400 border border-red-600/30',
    lifestyle: 'bg-pink-600/20 text-pink-400 border border-pink-600/30',
    other: 'bg-gray-600/20 text-gray-400 border border-gray-600/30'
  };

  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  const badgeClasses = `
    inline-flex items-center gap-1 rounded-full font-medium transition-all
    ${variants[variant] || variants.default}
    ${sizes[size]}
    ${onClick ? 'cursor-pointer hover:scale-105' : ''}
  `;

  return (
    <motion.span
      whileHover={onClick ? { scale: 1.05 } : {}}
      whileTap={onClick ? { scale: 0.95 } : {}}
      className={badgeClasses}
      onClick={onClick}
    >
      <span>{skill}</span>
      {removable && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-1 hover:text-red-400 transition-colors"
        >
          ×
        </button>
      )}
    </motion.span>
  );
};

export default SkillBadge;
