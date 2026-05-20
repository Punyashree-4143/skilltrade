import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

// Initial state
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
  error: null
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
  LOAD_USER_START: 'LOAD_USER_START',
  LOAD_USER_SUCCESS: 'LOAD_USER_SUCCESS',
  LOAD_USER_FAILURE: 'LOAD_USER_FAILURE',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Reducer function
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
    case AUTH_ACTIONS.LOAD_USER_START:
      return {
        ...state,
        loading: true,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
    case AUTH_ACTIONS.REGISTER_SUCCESS:
    case AUTH_ACTIONS.LOAD_USER_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
    case AUTH_ACTIONS.LOAD_USER_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: action.payload
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Set up axios defaults when token changes
  useEffect(() => {
    if (state.token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [state.token]);

  // Load user from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('authUser');
    
    if (token && user) {
      try {
        const parsedUser = JSON.parse(user);
        dispatch({
          type: AUTH_ACTIONS.LOAD_USER_SUCCESS,
          payload: { user: parsedUser, token }
        });
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        // Clear invalid stored data
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
      }
    }
  }, []);

  // Action creators
  const login = async (email, password) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });
      
      console.log('=== AUTH LOGIN ATTEMPT ===');
      console.log('Email:', email);
      
      const response = await axios.post('http://localhost:8000/api/auth/login', {
        email,
        password
      });
      
      console.log('=== LOGIN RESPONSE ===');
      console.log('Response:', response.data);
      
      const { access_token, user } = response.data;
      
      // Store in localStorage
      localStorage.setItem('authToken', access_token);
      localStorage.setItem('authUser', JSON.stringify(user));
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user, token: access_token }
      });
      
      console.log('=== LOGIN SUCCESSFUL ===');
      console.log('User:', user);
      
      return { success: true, user };
      
    } catch (error) {
      console.error('=== LOGIN ERROR ===');
      console.error('Error:', error.response?.data || error.message);
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: error.response?.data?.message || 'Login failed'
      });
      
      return { success: false, error: error.response?.data?.message || 'Login failed' };
    }
  };

  const register = async (name, email, password, passwordConfirm) => {
    try {
      dispatch({ type: AUTH_ACTIONS.REGISTER_START });
      
      console.log('=== AUTH REGISTER ATTEMPT ===');
      console.log('Name:', name);
      console.log('Email:', email);
      const response = await axios.post(
  'http://localhost:8000/api/auth/register',
  {
    name,
    email,
    password,
    password_confirm: passwordConfirm,
  }
);
      
      console.log('=== REGISTER RESPONSE ===');
      console.log('Response:', response.data);
      
      const { access_token, user } = response.data;
      
      // Store in localStorage
      localStorage.setItem('authToken', access_token);
      localStorage.setItem('authUser', JSON.stringify(user));
      
      dispatch({
        type: AUTH_ACTIONS.REGISTER_SUCCESS,
        payload: { user, token: access_token }
      });
      
      console.log('=== REGISTER SUCCESSFUL ===');
      console.log('User:', user);
      
      return { success: true, user };
      
    } catch (error) {
      console.error('=== REGISTER ERROR ===');
      console.error('Error:', error.response?.data || error.message);
      
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: error.response?.data?.message || 'Registration failed'
      });
      
      return { success: false, error: error.response?.data?.message || 'Registration failed' };
    }
  };

  const logout = () => {
    console.log('=== AUTH LOGOUT ===');
    
    // Call backend logout
    const token = localStorage.getItem('authToken');
    if (token) {
      axios.post('http://localhost:8000/api/auth/logout')
        .catch(error => {
          console.error('Backend logout error:', error);
        });
    }
    
    // Clear localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
    
    // Clear axios headers
    delete axios.defaults.headers.common['Authorization'];
    
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
    
    console.log('=== LOGOUT SUCCESSFUL ===');
  };

  const updateProfile = async (profileData) => {
    try {
      console.log('=== AUTH UPDATE PROFILE ATTEMPT ===');
      console.log('Profile data:', profileData);
      
      const response = await axios.put('http://localhost:8000/api/users/profile', profileData);
      
      console.log('=== UPDATE PROFILE RESPONSE ===');
      console.log('Response:', response.data);
      
      const updatedUser = response.data;
      
      // Update localStorage
      localStorage.setItem('authUser', JSON.stringify(updatedUser));
      
      // Update context state
      dispatch({
        type: AUTH_ACTIONS.LOAD_USER_SUCCESS,
        payload: { user: updatedUser, token: state.token }
      });
      
      console.log('=== UPDATE PROFILE SUCCESSFUL ===');
      console.log('Updated user:', updatedUser);
      
      return { success: true, user: updatedUser };
      
    } catch (error) {
      console.error('=== UPDATE PROFILE ERROR ===');
      console.error('Error:', error.response?.data || error.message);
      
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Profile update failed' 
      };
    }
  };

  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    clearError,
    isAuthenticated: state.isAuthenticated,
    user: state.user,
    token: state.token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
