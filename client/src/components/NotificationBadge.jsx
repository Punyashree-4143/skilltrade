import React from 'react';

const NotificationBadge = ({ count = 0 }) => {
  if (count === 0) return null;

  return (
    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center animate-pulse">
      {count > 99 ? '99+' : count}
    </span>
  );
};

export default NotificationBadge;
