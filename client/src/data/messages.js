// Mock messages data for SkillTrade demo
export const mockConversations = [
  {
    id: 'conv-1',
    userId: 'user-1',
    userName: 'Sarah Chen',
    userAvatar: 'https://images.unsplash.com/photo-1494790108755-2616b612c4d7?w=100&h=100&fit=crop&crop=face',
    lastMessage: 'Sounds great! When would you like to start the guitar lessons?',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    unreadCount: 2,
    isOnline: true,
    messages: [
      {
        id: 'msg-1-1',
        senderId: 'user-1',
        senderName: 'Sarah Chen',
        content: 'Hi! I saw you want to learn guitar. I\'ve been playing for 10 years and would love to teach you!',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-1-2',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'That would be amazing! I\'m really excited to learn guitar. What do you recommend for a complete beginner?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 1.5).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-1-3',
        senderId: 'user-1',
        senderName: 'Sarah Chen',
        content: 'Perfect! I\'d recommend starting with basic chords and strumming patterns. Do you have a guitar already?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-1-4',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'Yes, I have an acoustic guitar. I\'ve been trying to learn from YouTube but it\'s not the same as having a teacher!',
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-1-5',
        senderId: 'user-1',
        senderName: 'Sarah Chen',
        content: 'Sounds great! When would you like to start the guitar lessons?',
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        isOwn: false
      }
    ]
  },
  {
    id: 'conv-2',
    userId: 'user-2',
    userName: 'Mike Rodriguez',
    userAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    lastMessage: 'Thanks for the React tips! They really helped with my project.',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    unreadCount: 0,
    isOnline: false,
    messages: [
      {
        id: 'msg-2-1',
        senderId: 'user-2',
        senderName: 'Mike Rodriguez',
        content: 'Hey! I saw you\'re a React expert. I\'m struggling with state management in my project.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-2-2',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'Hey Mike! I\'d be happy to help. What specific issues are you having with state management?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3.5).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-2-3',
        senderId: 'user-2',
        senderName: 'Mike Rodriguez',
        content: 'Mostly with Redux and context API. I\'m building a photo gallery app.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-2-4',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'For a photo gallery, you might not need Redux. React Context and useReducer should be perfect. Let me share some code examples!',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2.5).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-2-5',
        senderId: 'user-2',
        senderName: 'Mike Rodriguez',
        content: 'Thanks for the React tips! They really helped with my project.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
        isOwn: false
      }
    ]
  },
  {
    id: 'conv-3',
    userId: 'user-3',
    userName: 'Emma Thompson',
    userAvatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
    lastMessage: 'The yoga session was amazing! Can\'t wait for next week.',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    unreadCount: 0,
    isOnline: true,
    messages: [
      {
        id: 'msg-3-1',
        senderId: 'user-3',
        senderName: 'Emma Thompson',
        content: 'Hi! I\'d love to learn React from you. I can teach you advanced yoga in exchange!',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-3-2',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'That sounds like a perfect trade! I\'ve been wanting to get into yoga for flexibility.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 47).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-3-3',
        senderId: 'user-3',
        senderName: 'Emma Thompson',
        content: 'Great! How about we start with a beginner session this weekend?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 46).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-3-4',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'Weekend sounds perfect! Saturday morning works best for me.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 45).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-3-5',
        senderId: 'user-3',
        senderName: 'Emma Thompson',
        content: 'The yoga session was amazing! Can\'t wait for next week.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
        isOwn: false
      }
    ]
  },
  {
    id: 'conv-4',
    userId: 'user-4',
    userName: 'Alex Johnson',
    userAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
    lastMessage: 'Sure! Let me know when you\'d like to continue our ML discussion.',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
    unreadCount: 1,
    isOnline: true,
    messages: [
      {
        id: 'msg-4-1',
        senderId: 'user-4',
        senderName: 'Alex Johnson',
        content: 'Hey! I saw your profile and noticed you know machine learning. I\'m working on a music recommendation system.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-4-2',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'That\'s interesting! What kind of algorithms are you using? Collaborative filtering or content-based?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 7).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-4-3',
        senderId: 'user-4',
        senderName: 'Alex Johnson',
        content: 'Starting with collaborative filtering, but having issues with cold start problem.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6.5).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-4-4',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'Cold start is tricky! You could try hybrid approach or use content features for new users.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-4-5',
        senderId: 'user-4',
        senderName: 'Alex Johnson',
        content: 'Sure! Let me know when you\'d like to continue our ML discussion.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
        isOwn: false
      }
    ]
  },
  {
    id: 'conv-5',
    userId: 'user-5',
    userName: 'Maria Garcia',
    userAvatar: 'https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=100&h=100&fit=crop&crop=face',
    lastMessage: '¡Hola! Yes, I can teach you Spanish. ¿Cuándo quieres empezar?',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    unreadCount: 0,
    isOnline: false,
    messages: [
      {
        id: 'msg-5-1',
        senderId: 'user-5',
        senderName: 'Maria Garcia',
        content: 'Hola! I\'d like to learn English from you. Can you teach me?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 14).toISOString(),
        isOwn: false
      },
      {
        id: 'msg-5-2',
        senderId: 'demo-user',
        senderName: 'You',
        content: 'Hi Maria! Yes, I\'d love to help you with English. When are you available?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 13).toISOString(),
        isOwn: true
      },
      {
        id: 'msg-5-3',
        senderId: 'user-5',
        senderName: 'Maria Garcia',
        content: '¡Hola! Yes, I can teach you Spanish. ¿Cuándo quieres empezar?',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
        isOwn: false
      }
    ]
  }
];

export const mockTypingUsers = ['user-1', 'user-4']; // Users currently typing
