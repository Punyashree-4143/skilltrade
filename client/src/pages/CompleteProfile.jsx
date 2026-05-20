import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, User, MapPin, Plus, X, Check, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const CompleteProfile = () => {
  const [formData, setFormData] = useState({
    bio: '',
    location: {
      city: '',
      country: ''
    },
    skills_offered: [],
    skills_wanted: []
  });
  const [currentOfferedSkill, setCurrentOfferedSkill] = useState('');
  const [currentWantedSkill, setCurrentWantedSkill] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { user, updateProfile } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Debug log to check if handler is being called
    console.log('CompleteProfile input change:', { name, value });
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    if (error) {
      setError('');
    }
  };

  const addOfferedSkill = () => {
    if (currentOfferedSkill.trim() && !formData.skills_offered.includes(currentOfferedSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills_offered: [...prev.skills_offered, currentOfferedSkill.trim()]
      }));
      setCurrentOfferedSkill('');
    }
  };

  const removeOfferedSkill = (skillToRemove) => {
    setFormData(prev => ({
      ...prev,
      skills_offered: prev.skills_offered.filter(skill => skill !== skillToRemove)
    }));
  };

  const addWantedSkill = () => {
    if (currentWantedSkill.trim() && !formData.skills_wanted.includes(currentWantedSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills_wanted: [...prev.skills_wanted, currentWantedSkill.trim()]
      }));
      setCurrentWantedSkill('');
    }
  };

  const removeWantedSkill = (skillToRemove) => {
    setFormData(prev => ({
      ...prev,
      skills_wanted: prev.skills_wanted.filter(skill => skill !== skillToRemove)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.skills_offered.length === 0) {
      setError('Please add at least one skill you can offer');
      return;
    }
    
    if (formData.skills_wanted.length === 0) {
      setError('Please add at least one skill you want to learn');
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('=== COMPLETE PROFILE SUBMIT ===');
      console.log('Form data:', formData);
      
      const result = await updateProfile(formData);
      
      if (result.success) {
        console.log('=== PROFILE COMPLETED SUCCESSFULLY ===');
        navigate('/explore');
      } else {
        console.log('=== PROFILE COMPLETION FAILED ===');
        console.log('Error:', result.error);
        setError(result.error || 'Failed to complete profile');
      }
    } catch (error) {
      console.error('=== PROFILE COMPLETION ERROR ===');
      console.error('Error:', error);
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        <div className="glass-morphism p-8 rounded-2xl border border-gray-700 shadow-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <h1 className="text-3xl font-bold text-white mb-2">Complete Your Profile</h1>
              <p className="text-gray-400">Tell others about your skills and what you want to learn</p>
            </motion.div>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-900/20 border border-red-600 rounded-lg"
            >
              <p className="text-red-400 text-sm">{error}</p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Bio */}
            <div>
              <label htmlFor="bio" className="block text-sm font-medium text-gray-300 mb-2">
                About You
              </label>
              <textarea
                id="bio"
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                placeholder="Tell others about yourself, your experience, and what you're passionate about..."
                autoComplete="off"
              />
            </div>

            {/* Location */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="location.city" className="block text-sm font-medium text-gray-300 mb-2">
                  <MapPin className="w-4 h-4 inline mr-2" />
                  City
                </label>
                <input
                  id="location.city"
                  name="location.city"
                  type="text"
                  value={formData.location.city}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Your city"
                  autoComplete="address-level2"
                />
              </div>
              <div>
                <label htmlFor="location.country" className="block text-sm font-medium text-gray-300 mb-2">
                  Country
                </label>
                <input
                  id="location.country"
                  name="location.country"
                  type="text"
                  value={formData.location.country}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Your country"
                  autoComplete="country"
                />
              </div>
            </div>

            {/* Skills You Can Offer */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Skills You Can Offer
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={currentOfferedSkill}
                  onChange={(e) => setCurrentOfferedSkill(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addOfferedSkill();
                    }
                  }}
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Add a skill you can teach..."
                />
                <button
                  type="button"
                  onClick={addOfferedSkill}
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/80 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.skills_offered.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-primary/20 text-primary rounded-full text-sm"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeOfferedSkill(skill)}
                      className="hover:text-red-400 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
              {formData.skills_offered.length === 0 && (
                <p className="text-gray-500 text-sm mt-2">Add at least one skill you can offer</p>
              )}
            </div>

            {/* Skills You Want to Learn */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Skills You Want to Learn
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={currentWantedSkill}
                  onChange={(e) => setCurrentWantedSkill(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addWantedSkill();
                    }
                  }}
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Add a skill you want to learn..."
                />
                <button
                  type="button"
                  onClick={addWantedSkill}
                  className="px-4 py-2 bg-secondary text-white rounded-lg hover:bg-secondary/80 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.skills_wanted.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-secondary/20 text-secondary rounded-full text-sm"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeWantedSkill(skill)}
                      className="hover:text-red-400 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
              {formData.skills_wanted.length === 0 && (
                <p className="text-gray-500 text-sm mt-2">Add at least one skill you want to learn</p>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary to-secondary hover:shadow-lg text-white py-3 px-4 rounded-lg transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-t-white border-r-transparent animate-spin rounded-full"></div>
                  <span>Completing profile...</span>
                </>
              ) : (
                <>
                  <span>Complete Profile</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </form>

          {/* Skip for now */}
          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => navigate('/explore')}
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              Skip for now →
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default CompleteProfile;
