import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const Profile = () => {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="glass-morphism p-8 rounded-2xl border border-gray-700">
        <h1 className="text-3xl font-bold text-white mb-6">My Profile</h1>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <div className="text-center">
              <div className="w-32 h-32 bg-gray-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                {user?.avatar ? (
                  <img src={user.avatar} alt={user.name} className="w-full h-full rounded-full object-cover" />
                ) : (
                  <span className="text-4xl text-white">{user?.name?.charAt(0)}</span>
                )}
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">{user?.name}</h2>
              <p className="text-gray-400">{user?.email}</p>
            </div>
          </div>
          
          <div className="md:col-span-2">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Bio</h3>
                <p className="text-gray-300">
                  {user?.bio || 'No bio added yet. Tell others about yourself!'}
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Skills I Can Offer</h3>
                <div className="flex flex-wrap gap-2">
                  {user?.offers?.map((offer, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm"
                    >
                      {offer.skill}
                    </span>
                  ))}
                  {(!user?.offers || user.offers.length === 0) && (
                    <p className="text-gray-400">No skills added yet</p>
                  )}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Skills I Want to Learn</h3>
                <div className="flex flex-wrap gap-2">
                  {user?.wants?.map((want, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-secondary/20 text-secondary rounded-full text-sm"
                    >
                      {want.skill}
                    </span>
                  ))}
                  {(!user?.wants || user.wants.length === 0) && (
                    <p className="text-gray-400">No skills added yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Profile;
