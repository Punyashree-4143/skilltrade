import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  MapPin,
  X,
  Plus,
  Upload,
  Save
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const EditProfile = () => {
  const { user, updateProfile } = useAuth();

  const [loading, setLoading] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const [profile, setProfile] = useState({
    name: '',
    email: '',
    bio: '',
    skillsOffered: [],
    skillsWanted: [],
    location: '',
    availability: '',
    experienceLevel: 'intermediate'
  });

  const [customOfferedSkill, setCustomOfferedSkill] = useState('');
  const [customWantedSkill, setCustomWantedSkill] = useState('');

  const skills = [
    'React',
    'JavaScript',
    'Python',
    'Node.js',
    'MongoDB',
    'Express',
    'UI Design',
    'UX Design',
    'Figma',
    'Photoshop',
    'Illustrator',
    'Machine Learning',
    'Data Science',
    'TensorFlow',
    'PyTorch',
    'Web Development',
    'Mobile Development',
    'DevOps',
    'AWS',
    'Docker',
    'GraphQL',
    'REST API',
    'TypeScript',
    'Vue.js',
    'Angular',
    'Digital Marketing',
    'SEO',
    'Content Writing',
    'Copywriting',
    'Photography',
    'Video Editing',
    'Animation',
    '3D Modeling'
  ];

  const experienceLevels = [
    { value: 'beginner', label: 'Beginner', color: 'text-green-400' },
    { value: 'intermediate', label: 'Intermediate', color: 'text-blue-400' },
    { value: 'advanced', label: 'Advanced', color: 'text-purple-400' },
    { value: 'expert', label: 'Expert', color: 'text-yellow-400' }
  ];

  const availabilityOptions = [
    'Weekdays',
    'Weekends',
    'Evenings',
    'Flexible',
    'Full-time',
    'Part-time'
  ];

  useEffect(() => {
    if (user) {
      setProfile({
        name: user?.name || '',
        email: user?.email || '',
        bio: user?.bio || '',
        skillsOffered: user?.skills_offered || [],
        skillsWanted: user?.skills_wanted || [],
        location: user?.location?.city || '',
        availability: user?.availability || '',
        experienceLevel: user?.experience_level || 'intermediate'
      });

      setAvatarPreview(user?.avatar || '');
    }
  }, [user]);

  const handleAvatarUpload = (e) => {
    const file = e.target.files[0];

    if (file) {
      const reader = new FileReader();

      reader.onloadend = () => {
        setAvatarPreview(reader.result);
      };

      reader.readAsDataURL(file);
    }
  };

  const addSkill = (skill, type) => {
    if (type === 'offered') {
      if (!profile.skillsOffered.includes(skill)) {
        setProfile((prev) => ({
          ...prev,
          skillsOffered: [...prev.skillsOffered, skill]
        }));
      }
    } else {
      if (!profile.skillsWanted.includes(skill)) {
        setProfile((prev) => ({
          ...prev,
          skillsWanted: [...prev.skillsWanted, skill]
        }));
      }
    }
  };

  const normalizeSkill = (skill) => {
    return skill.trim().replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const addCustomOfferedSkill = () => {
    const normalized = normalizeSkill(customOfferedSkill);
    if (!normalized) return;

    const isDuplicate = profile.skillsOffered.some(
      (skill) => skill.toLowerCase() === normalized.toLowerCase()
    );

    if (!isDuplicate) {
      setProfile((prev) => ({
        ...prev,
        skillsOffered: [...prev.skillsOffered, normalized]
      }));
    }

    setCustomOfferedSkill('');
  };

  const addCustomWantedSkill = () => {
    const normalized = normalizeSkill(customWantedSkill);
    if (!normalized) return;

    const isDuplicate = profile.skillsWanted.some(
      (skill) => skill.toLowerCase() === normalized.toLowerCase()
    );

    if (!isDuplicate) {
      setProfile((prev) => ({
        ...prev,
        skillsWanted: [...prev.skillsWanted, normalized]
      }));
    }

    setCustomWantedSkill('');
  };

  const handleOfferedKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addCustomOfferedSkill();
    }
  };

  const handleWantedKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addCustomWantedSkill();
    }
  };

  const removeSkill = (skill, type) => {
    if (type === 'offered') {
      setProfile((prev) => ({
        ...prev,
        skillsOffered: prev.skillsOffered.filter((s) => s !== skill)
      }));
    } else {
      setProfile((prev) => ({
        ...prev,
        skillsWanted: prev.skillsWanted.filter((s) => s !== skill)
      }));
    }
  };

  const saveProfile = async () => {
    setLoading(true);

    try {
      // Convert frontend camelCase -> backend snake_case
      const updates = {
        name: profile.name,
        email: profile.email,
        bio: profile.bio,

        skills_offered: profile.skillsOffered || [],
        skills_wanted: profile.skillsWanted || [],

        location: {
          city: profile.location || ''
        },

        availability: profile.availability,

        experience_level: profile.experienceLevel,

        avatar: avatarPreview || user?.avatar
      };

      console.log('=== PROFILE UPDATE PAYLOAD ===');
      console.log(updates);

      await updateProfile(updates);

      setMessage('Profile updated successfully!');
      setMessageType('success');

      setTimeout(() => {
        setMessage('');
        setMessageType('');
      }, 3000);

    } catch (error) {
      console.log('=== PROFILE UPDATE ERROR ===');
      console.log(error.response?.data);

      setMessage(
        error.response?.data?.detail?.[0]?.msg ||
        'Error updating profile. Please try again.'
      );

      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">
          Edit Profile
        </h1>

        <div className="flex items-center space-x-4">
          {message && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`px-4 py-2 rounded-lg ${
                messageType === 'success'
                  ? 'bg-green-900 text-green-400'
                  : 'bg-red-900 text-red-400'
              }`}
            >
              {message}
            </motion.div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Basic Info */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-morphism p-6 rounded-xl border border-gray-700"
        >
          <h2 className="text-xl font-semibold text-white mb-6">
            Basic Information
          </h2>

          <div className="space-y-4">

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <User className="w-4 h-4 inline mr-2" />
                Full Name
              </label>

              <input
                type="text"
                value={profile.name}
                onChange={(e) =>
                  setProfile((prev) => ({
                    ...prev,
                    name: e.target.value
                  }))
                }
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>

              <input
                type="email"
                value={profile.email}
                onChange={(e) =>
                  setProfile((prev) => ({
                    ...prev,
                    email: e.target.value
                  }))
                }
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Bio
              </label>

              <textarea
                rows={4}
                value={profile.bio}
                onChange={(e) =>
                  setProfile((prev) => ({
                    ...prev,
                    bio: e.target.value
                  }))
                }
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white resize-none"
              />
            </div>

          </div>
        </motion.div>

        {/* Skills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-morphism p-6 rounded-xl border border-gray-700"
        >
          <h2 className="text-xl font-semibold text-white mb-6">
            Skills
          </h2>

          {/* Offered */}
          <div className="mb-6">
            <h3 className="text-gray-300 mb-3">
              Skills You Can Teach
            </h3>

            <div className="flex flex-wrap gap-2 mb-4">
              {profile.skillsOffered.map((skill) => (
                <span
                  key={skill}
                  className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm flex items-center gap-2"
                >
                  {skill}

                  <button onClick={() => removeSkill(skill, 'offered')}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-2">
              {skills.slice(0, 8).map((skill) => (
                <button
                  key={skill}
                  onClick={() => addSkill(skill, 'offered')}
                  className="px-3 py-2 bg-gray-700 rounded-lg text-gray-300 hover:bg-gray-600"
                >
                  <Plus className="w-3 h-3 inline mr-1" />
                  {skill}
                </button>
              ))}
            </div>

            <div className="mt-4 flex gap-2">
              <input
                type="text"
                placeholder="Add custom skill"
                value={customOfferedSkill}
                onChange={(e) => setCustomOfferedSkill(e.target.value)}
                onKeyDown={handleOfferedKeyDown}
                className="flex-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm"
              />
              <button
                onClick={addCustomOfferedSkill}
                className="px-4 py-2 bg-primary text-white rounded-lg text-sm hover:bg-primary/80"
              >
                Add
              </button>
            </div>
          </div>

          {/* Wanted */}
          <div>
            <h3 className="text-gray-300 mb-3">
              Skills You Want To Learn
            </h3>

            <div className="flex flex-wrap gap-2 mb-4">
              {profile.skillsWanted.map((skill) => (
                <span
                  key={skill}
                  className="px-3 py-1 bg-secondary/20 text-secondary rounded-full text-sm flex items-center gap-2"
                >
                  {skill}

                  <button onClick={() => removeSkill(skill, 'wanted')}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-2">
              {skills.slice(8, 16).map((skill) => (
                <button
                  key={skill}
                  onClick={() => addSkill(skill, 'wanted')}
                  className="px-3 py-2 bg-gray-700 rounded-lg text-gray-300 hover:bg-gray-600"
                >
                  <Plus className="w-3 h-3 inline mr-1" />
                  {skill}
                </button>
              ))}
            </div>

            <div className="mt-4 flex gap-2">
              <input
                type="text"
                placeholder="Add custom skill"
                value={customWantedSkill}
                onChange={(e) => setCustomWantedSkill(e.target.value)}
                onKeyDown={handleWantedKeyDown}
                className="flex-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm"
              />
              <button
                onClick={addCustomWantedSkill}
                className="px-4 py-2 bg-secondary text-white rounded-lg text-sm hover:bg-secondary/80"
              >
                Add
              </button>
            </div>
          </div>
        </motion.div>

        {/* Location & Photo */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-morphism p-6 rounded-xl border border-gray-700"
        >
          <h2 className="text-xl font-semibold text-white mb-6">
            Location & Photo
          </h2>

          <div className="space-y-4">

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <MapPin className="w-4 h-4 inline mr-2" />
                Location
              </label>

              <input
                type="text"
                value={profile.location}
                onChange={(e) =>
                  setProfile((prev) => ({
                    ...prev,
                    location: e.target.value
                  }))
                }
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Availability
              </label>

              <div className="grid grid-cols-2 gap-2">
                {availabilityOptions.map((option) => (
                  <button
                    key={option}
                    onClick={() =>
                      setProfile((prev) => ({
                        ...prev,
                        availability: option
                      }))
                    }
                    className={`p-3 rounded-lg border ${
                      profile.availability === option
                        ? 'border-primary bg-primary/20 text-white'
                        : 'border-gray-600 text-gray-400'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col items-center space-y-4">
              <div className="relative">

                <div className="w-24 h-24 rounded-full bg-gray-700 overflow-hidden flex items-center justify-center">
                  {avatarPreview ? (
                    <img
                      src={avatarPreview}
                      alt="Avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="w-12 h-12 text-gray-500" />
                  )}
                </div>

                <label
                  htmlFor="avatar-upload"
                  className="absolute bottom-0 right-0 bg-primary p-2 rounded-full cursor-pointer"
                >
                  <Upload className="w-4 h-4 text-white" />
                </label>

                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarUpload}
                  className="hidden"
                />
              </div>

              <p className="text-sm text-gray-500">
                JPG, PNG or GIF
              </p>
            </div>

          </div>
        </motion.div>
      </div>

      {/* Save Button */}
      <div className="flex justify-center">
        <button
          onClick={saveProfile}
          disabled={loading}
          className="bg-gradient-to-r from-primary to-secondary px-8 py-3 rounded-lg text-white flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <>
              <LoadingSpinner size="small" />
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default EditProfile;