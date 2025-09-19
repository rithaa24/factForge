# Frontend-Backend Connection Setup

This guide explains how to properly connect the FactForge React Native frontend with the FastAPI backend.

## 🔍 Current Status

### ✅ **What's Working:**
- Backend API is properly structured and running on port 8000
- CORS is configured to allow frontend requests
- API endpoints match frontend expectations
- Frontend has fallback to mock data when backend is unavailable

### ❌ **What Was Missing:**
- Frontend was using relative API paths (`/api`) instead of full backend URL
- No proper HTTP client for API communication
- No connection status monitoring
- No environment configuration for different deployment scenarios

## 🛠️ **What I've Fixed:**

### 1. **Created Configuration System**
- `FactForgeMobile/services/config.ts` - Centralized configuration
- Environment-based API URL selection
- Debug logging configuration
- Error message constants

### 2. **Created HTTP Client**
- `FactForgeMobile/services/httpClient.ts` - Robust HTTP client
- Retry logic with exponential backoff
- Proper error handling
- Request/response logging

### 3. **Updated API Service**
- `FactForgeMobile/services/api.ts` - Updated to use real API
- Fallback to mock data when backend is unavailable
- Proper error handling and logging

### 4. **Added Connection Monitoring**
- `FactForgeMobile/services/connectionStatus.ts` - Real-time connection monitoring
- Status change listeners
- Periodic health checks
- UI status indicators

## 🚀 **How to Use:**

### **Step 1: Start the Backend**
```bash
cd factforge-backend
cp infra/env.sample .env
docker-compose -f infra/docker-compose.yml up --build
```

### **Step 2: Start the Frontend**
```bash
cd FactForgeMobile
npm install
npm start
```

### **Step 3: Verify Connection**
The frontend will automatically:
1. Try to connect to the backend at `http://localhost:8000`
2. Fall back to mock data if backend is unavailable
3. Show connection status in the UI
4. Log connection attempts in the console

## 🔧 **Configuration Options:**

### **Development Mode (Default)**
```typescript
// FactForgeMobile/services/config.ts
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api',  // Local backend
  WS_URL: 'ws://localhost:8000/ws/events',
  // ...
};
```

### **Production Mode**
```typescript
// FactForgeMobile/services/config.ts
export const API_CONFIG = {
  BASE_URL: 'https://your-backend-domain.com/api',  // Production backend
  WS_URL: 'wss://your-backend-domain.com/ws/events',
  // ...
};
```

## 📱 **Frontend Features:**

### **Automatic Fallback**
- If backend is unavailable, frontend uses mock data
- Users can still use the app in offline mode
- Connection status is shown in the UI

### **Real-time Monitoring**
- Connection status updates automatically
- Health checks every 30 seconds in development
- Visual indicators for connection status

### **Error Handling**
- Network errors are handled gracefully
- User-friendly error messages
- Automatic retry with exponential backoff

## 🧪 **Testing the Connection:**

### **Test 1: Backend Running**
```bash
# Start backend
cd factforge-backend
docker-compose -f infra/docker-compose.yml up --build

# Start frontend
cd FactForgeMobile
npm start

# Check console logs - should see:
# ✅ Real API response received for fact-check
```

### **Test 2: Backend Stopped**
```bash
# Stop backend
docker-compose -f infra/docker-compose.yml down

# Check console logs - should see:
# ⚠️ Real API failed, falling back to mock data
```

### **Test 3: API Health Check**
```bash
# Test backend health
curl http://localhost:8000/health

# Test fact-check API
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"claim_text": "Test claim", "language": "en"}'
```

## 🔍 **Debugging:**

### **Enable Debug Logging**
```typescript
// FactForgeMobile/services/config.ts
export const DEBUG_CONFIG = {
  ENABLE_LOGGING: true,
  LOG_API_CALLS: true,
  LOG_WEBSOCKET_EVENTS: true,
};
```

### **Check Connection Status**
```typescript
import { connectionStatusService } from './services/connectionStatus';

// Get current status
const status = connectionStatusService.getStatus();
console.log('Connection status:', status);

// Listen for status changes
const unsubscribe = connectionStatusService.addListener((status) => {
  console.log('Status changed:', status);
});
```

## 🌐 **Network Configuration:**

### **Local Development**
- Frontend: `http://localhost:8081` (Expo default)
- Backend: `http://localhost:8000`
- CORS: Configured to allow all origins

### **Production Deployment**
- Frontend: Deployed to app stores
- Backend: Deployed to cloud (AWS, GCP, etc.)
- CORS: Configured for specific domains

## 📊 **Connection Status Indicators:**

| Status | Color | Message | Description |
|--------|-------|---------|-------------|
| ✅ Connected & Healthy | Green | "Connected to backend" | Backend is running and healthy |
| ⚠️ Connected but Unhealthy | Orange | "Backend connected but not healthy" | Backend is reachable but has issues |
| ❌ Not Connected | Red | "Backend not connected - using offline mode" | Backend is not reachable |

## 🚨 **Troubleshooting:**

### **Common Issues:**

1. **"Network error" messages**
   - Check if backend is running: `docker-compose ps`
   - Check backend logs: `docker-compose logs api`
   - Verify port 8000 is not blocked

2. **CORS errors**
   - Backend CORS is configured for all origins
   - Check if backend is actually running on port 8000

3. **Mock data always used**
   - Check console logs for connection errors
   - Verify backend health endpoint: `curl http://localhost:8000/health`
   - Check network connectivity

4. **Slow responses**
   - Backend might be starting up (first request is slower)
   - Check backend logs for processing time
   - Consider using mock data for development

### **Debug Commands:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check API endpoints
curl http://localhost:8000/docs

# Check backend logs
docker-compose -f factforge-backend/infra/docker-compose.yml logs api

# Check frontend logs
# Look in Expo console or browser developer tools
```

## ✅ **Summary:**

The frontend and backend are now properly connected with:

1. **✅ Proper API Configuration** - Frontend knows where to find the backend
2. **✅ Robust HTTP Client** - Handles errors and retries gracefully
3. **✅ Automatic Fallback** - Works offline with mock data
4. **✅ Connection Monitoring** - Real-time status updates
5. **✅ Debug Logging** - Easy troubleshooting
6. **✅ Error Handling** - User-friendly error messages

**The connection is now fully configured and ready to use!** 🎉
