import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

const Toast = ({ id, type, message, onClose }) => {
  const icons = {
    success: <CheckCircle className="w-5 h-5 text-green-400" />,
    error: <AlertCircle className="w-5 h-5 text-red-400" />,
    warning: <AlertTriangle className="w-5 h-5 text-yellow-400" />,
    info: <Info className="w-5 h-5 text-blue-400" />
  };

  const bgColors = {
    success: 'bg-green-900/80 border-green-700',
    error: 'bg-red-900/80 border-red-700',
    warning: 'bg-yellow-900/80 border-yellow-700',
    info: 'bg-blue-900/80 border-blue-700'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.3 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.3 }}
      transition={{ duration: 0.3 }}
      className={`flex items-center gap-3 p-4 rounded-lg border ${bgColors[type]} backdrop-blur-sm min-w-[300px] max-w-md`}
    >
      {icons[type]}
      <p className="flex-1 text-sm text-white">{message}</p>
      <button
        onClick={() => onClose(id)}
        className="text-white/60 hover:text-white transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
};

const ToastContainer = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handleToast = (event) => {
      const { type, message } = event.detail;
      const id = Date.now().toString();
      
      setToasts(prev => [...prev, { id, type, message }]);
      
      setTimeout(() => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
      }, 5000);
    };

    window.addEventListener('toast', handleToast);
    return () => window.removeEventListener('toast', handleToast);
  }, []);

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={removeToast}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};

export const showToast = (type, message) => {
  window.dispatchEvent(new CustomEvent('toast', { detail: { type, message } }));
};

export default ToastContainer;
