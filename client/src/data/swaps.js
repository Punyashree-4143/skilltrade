// Mock swaps data for SkillTrade demo
export const mockSwaps = {
  pending: [
    {
      id: 'swap-1',
      requesterId: 'user-2',
      requesterName: 'Mike Rodriguez',
      requesterAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'demo-user',
      requestedFromName: 'You',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'Photography', category: 'creative', level: 'expert' },
      requestedSkill: { name: 'React', category: 'technology', level: 'beginner' },
      message: 'Hi! I\'d love to learn React basics in exchange for photography lessons. I can teach you composition, lighting, and photo editing!',
      proposedSchedule: 'Weekends, 2-hour sessions',
      status: 'pending',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toISOString()
    },
    {
      id: 'swap-2',
      requesterId: 'user-6',
      requesterName: 'David Kim',
      requesterAvatar: 'https://images.unsplash.com/photo-1507591064342-4c6ce005b128?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'demo-user',
      requestedFromName: 'You',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'UI Design', category: 'creative', level: 'expert' },
      requestedSkill: { name: 'Python', category: 'technology', level: 'beginner' },
      message: 'I can help you with UI/UX design principles and Figma prototyping in exchange for Python programming basics!',
      proposedSchedule: 'Flexible, weekday evenings',
      status: 'pending',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
      expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 5).toISOString()
    },
    {
      id: 'swap-3',
      requesterId: 'user-11',
      requesterName: 'Sofia Martinez',
      requesterAvatar: 'https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'demo-user',
      requestedFromName: 'You',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'Graphic Design', category: 'creative', level: 'expert' },
      requestedSkill: { name: 'Node.js', category: 'technology', level: 'intermediate' },
      message: 'Would love to learn backend development! I can teach you Adobe Creative Suite and brand design in return.',
      proposedSchedule: 'Afternoons, 3-hour sessions',
      status: 'pending',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 1).toISOString(),
      expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 6).toISOString()
    }
  ],
  accepted: [
    {
      id: 'swap-4',
      requesterId: 'demo-user',
      requesterName: 'You',
      requesterAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'user-1',
      requestedFromName: 'Sarah Chen',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1494790108755-2616b612c4d7?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'React', category: 'technology', level: 'expert' },
      requestedSkill: { name: 'Guitar', category: 'creative', level: 'intermediate' },
      message: 'Excited to learn guitar from you! I can teach React hooks, state management, and performance optimization.',
      proposedSchedule: 'Saturday mornings, 2-hour sessions',
      status: 'accepted',
      acceptedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
      nextSession: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2).toISOString(),
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 4).toISOString()
    },
    {
      id: 'swap-5',
      requesterId: 'user-3',
      requesterName: 'Emma Thompson',
      requesterAvatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'demo-user',
      requestedFromName: 'You',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'Yoga', category: 'health', level: 'expert' },
      requestedSkill: { name: 'UI/UX Design', category: 'creative', level: 'intermediate' },
      message: 'Perfect! I can teach you vinyasa flow, meditation techniques, and flexibility training.',
      proposedSchedule: 'Weekday evenings, 1-hour sessions',
      status: 'accepted',
      acceptedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
      nextSession: new Date(Date.now() + 1000 * 60 * 60 * 24 * 1).toISOString(),
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 8).toISOString()
    }
  ],
  completed: [
    {
      id: 'swap-6',
      requesterId: 'demo-user',
      requesterName: 'You',
      requesterAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'user-4',
      requestedFromName: 'Alex Johnson',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'Python', category: 'technology', level: 'expert' },
      requestedSkill: { name: 'Machine Learning', category: 'technology', level: 'intermediate' },
      message: 'Great ML sessions! Your music recommendation algorithm project was fascinating.',
      proposedSchedule: 'Completed 8 sessions over 4 weeks',
      status: 'completed',
      completedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
      rating: 5,
      review: 'Excellent teacher! Made complex ML concepts very easy to understand.',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 21).toISOString()
    },
    {
      id: 'swap-7',
      requesterId: 'user-7',
      requesterName: 'Lisa Wang',
      requesterAvatar: 'https://images.unsplash.com/photo-1544005173-1a5b5b5b5b5b?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'demo-user',
      requestedFromName: 'You',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'Data Science', category: 'technology', level: 'expert' },
      requestedSkill: { name: 'React', category: 'technology', level: 'beginner' },
      message: 'Thank you for the React lessons! Your data science expertise was invaluable.',
      proposedSchedule: 'Completed 6 sessions over 3 weeks',
      status: 'completed',
      completedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
      rating: 4,
      review: 'Very knowledgeable and patient. Helped me understand complex data concepts.',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 17).toISOString()
    },
    {
      id: 'swap-8',
      requesterId: 'user-9',
      requesterName: 'Nina Patel',
      requesterAvatar: 'https://images.unsplash.com/photo-1527980965255-d3b416303d12b?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'demo-user',
      requestedFromName: 'You',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'React Native', category: 'technology', level: 'expert' },
      requestedSkill: { name: 'UI/UX Design', category: 'creative', level: 'intermediate' },
      message: 'Amazing mobile development guidance! Your design insights really improved my app.',
      proposedSchedule: 'Completed 10 sessions over 5 weeks',
      status: 'completed',
      completedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString(),
      rating: 5,
      review: 'Fantastic teacher! Very knowledgeable about both mobile dev and design principles.',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString()
    }
  ],
  cancelled: [
    {
      id: 'swap-9',
      requesterId: 'user-8',
      requesterName: 'James Wilson',
      requesterAvatar: 'https://images.unsplash.com/photo-1500648767791-00dc994a4e4e?w=100&h=100&fit=crop&crop=face',
      requestedFromId: 'demo-user',
      requestedFromName: 'You',
      requestedFromAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      offeredSkill: { name: 'Cooking', category: 'health', level: 'expert' },
      requestedSkill: { name: 'Business Development', category: 'business', level: 'intermediate' },
      message: 'Sorry, scheduling conflicts came up. Maybe we can rearrange for next month?',
      status: 'cancelled',
      cancelledAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
      reason: 'Scheduling conflicts',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString()
    }
  ]
};

export const swapStatuses = {
  pending: 'Pending',
  accepted: 'Accepted',
  completed: 'Completed',
  cancelled: 'Cancelled'
};
