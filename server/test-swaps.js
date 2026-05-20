// Simple test script to verify swap system works
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

// Test user credentials (you'll need to create these first)
const testUser = {
  email: 'test@example.com',
  password: 'Test123'
};

const testSwap = async () => {
  try {
    console.log('🧪 Testing Swap System...');
    
    // 1. Login to get token
    console.log('\n1. Logging in...');
    const loginResponse = await axios.post(`${API_BASE}/auth/login`, testUser);
    const token = loginResponse.data.token;
    console.log('✅ Login successful');
    
    // Set auth header
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    // 2. Get current user
    console.log('\n2. Getting current user...');
    const userResponse = await axios.get(`${API_BASE}/users/profile`);
    const currentUser = userResponse.data.user;
    console.log('✅ Current user:', currentUser.name);
    
    // 3. Get users to find someone to swap with
    console.log('\n3. Getting available users...');
    const usersResponse = await axios.get(`${API_BASE}/users`);
    const otherUsers = usersResponse.data.filter(u => u._id !== currentUser._id);
    
    if (otherUsers.length === 0) {
      console.log('❌ No other users found');
      return;
    }
    
    const targetUser = otherUsers[0];
    console.log('✅ Found target user:', targetUser.name);
    
    // 4. Create swap request
    console.log('\n4. Creating swap request...');
    const swapData = {
      receiver: targetUser._id,
      offeredSkill: {
        skill: 'JavaScript',
        category: 'technology',
        description: 'Advanced JavaScript programming'
      },
      requestedSkill: {
        skill: 'Python',
        category: 'technology', 
        description: 'Python basics'
      },
      message: 'I would love to learn Python in exchange for JavaScript lessons!',
      proposedDuration: 60
    };
    
    const swapResponse = await axios.post(`${API_BASE}/swaps`, swapData);
    console.log('✅ Swap request created:', swapResponse.data.swapRequest._id);
    
    // 5. Get sent requests
    console.log('\n5. Getting sent requests...');
    const sentResponse = await axios.get(`${API_BASE}/swaps?type=sent`);
    console.log('✅ Sent requests:', sentResponse.data.swapRequests.length);
    
    // 6. Get received requests
    console.log('\n6. Getting received requests...');
    const receivedResponse = await axios.get(`${API_BASE}/swaps?type=received`);
    console.log('✅ Received requests:', receivedResponse.data.swapRequests.length);
    
    console.log('\n🎉 All tests passed! Swap system is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
};

// Run the test
testSwap();
