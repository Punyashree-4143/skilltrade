import React from 'react';
import { motion } from 'framer-motion';

const About = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="glass-morphism p-8 rounded-2xl border border-gray-700">
        <h1 className="text-3xl font-bold text-white mb-6">About SkillTrade</h1>
        <p className="text-gray-400">About page content coming soon...</p>
      </div>
    </motion.div>
  );
};

export default About;
