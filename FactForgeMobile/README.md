# FactForge Mobile - Expo React Native App

A comprehensive mobile-first application for AI-powered fact-checking and community-driven scam alerts, built with Expo and React Native. Now featuring Tamil language support alongside English and Hindi.

## 🚀 Quick Start with Expo Go

### Prerequisites
- Install [Expo Go](https://expo.dev/client) on your mobile device
- Install [Node.js](https://nodejs.org/) (v16 or later)
- Install Expo CLI: `npm install -g @expo/cli`

### Running the App

1. **Navigate to the mobile app directory:**
   ```bash
   cd FactForgeMobile
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npx expo start
   ```

4. **Open on your device:**
   - **iOS**: Open Camera app and scan the QR code
   - **Android**: Open Expo Go app and scan the QR code
   - **Simulator**: Press `i` for iOS simulator or `a` for Android emulator

## 📱 Features

### Core Functionality
- **Social Feed**: Browse community scam alerts and fact-checks
- **AI Fact Checker**: Analyze text, URLs, and images for credibility
- **Communities**: Join public and private groups for targeted discussions
- **User Profiles**: Track contributions, badges, and activity

### Mobile-Specific Features
- **Camera Integration**: Take photos for fact-checking
- **Image Picker**: Select images from gallery
- **Haptic Feedback**: Tactile responses for interactions
- **Native Sharing**: Share results using device share sheet
- **Offline Support**: Basic caching for improved performance
- **Push Notifications**: Real-time alerts (configured but not active in demo)
- **Multi-language Support**: English, Hindi, and Tamil with i18n integration

### UI/UX Highlights
- **Responsive Design**: Optimized for all screen sizes
- **Native Navigation**: Tab-based navigation with stack screens
- **Smooth Animations**: Native performance with React Native Reanimated
- **Accessibility**: Screen reader support and proper contrast ratios
- **Touch-Friendly**: 44px minimum touch targets
- **Mobile-First Design**: Completely redesigned for mobile-first experience

## 🏗️ App Structure

```
FactForgeMobile/
├── app/                    # Expo Router pages
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── index.tsx      # Feed screen
│   │   ├── check.tsx      # Fact-check screen
│   │   ├── communities.tsx # Communities screen
│   │   └── profile.tsx    # Profile screen
│   ├── check-result.tsx   # Modal result screen
│   └── _layout.tsx        # Root layout
├── components/            # Reusable components
│   ├── TrustMeter.tsx    # Circular trust score widget
│   └── FeedCard.tsx      # Social post card
├── i18n/                 # Internationalization
│   ├── index.ts          # i18n configuration
│   └── locales/          # Language files (en, hi, ta)
├── services/             # API and data services
│   └── api.ts           # Mock API implementation
├── types/               # TypeScript definitions
│   └── index.ts        # Shared type definitions
└── assets/             # Images and static files
```

## 🎯 Demo Scenarios

### 1. Fact-Check a Scam Message
1. Go to **Check** tab
2. Paste: "Send ₹1000 to UPI abc@upi to claim lottery prize!"
3. Tap **Check Content**
4. View trust score and evidence
5. Tap **Publish as Alert** to share with community

### 2. Browse Community Feed
1. Go to **Feed** tab
2. Scroll through scam alerts
3. Tap heart to upvote posts
4. View trust scores and evidence counts

### 3. Join Communities
1. Go to **Communities** tab
2. Browse available communities
3. Tap **Join Community** for public groups
4. View community stats and member counts

### 4. Camera Integration
1. Go to **Check** tab
2. Tap **Camera** button
3. Take photo of suspicious message
4. Process for fact-checking

## 🔧 Development

### Available Scripts
- `npm start` - Start Expo development server
### 5. Language Support
1. Go to **Profile** tab
2. Tap **Language** in menu
3. Choose from English, Hindi, or Tamil
4. App interface updates immediately
- `npm run android` - Open on Android device/emulator
- `npm run ios` - Open on iOS device/simulator
- `npm run web` - Open in web browser

### Key Dependencies
- **Expo SDK 51** - Development platform
- **React Native 0.74** - Mobile framework
- **Expo Router** - File-based navigation
- **React Native SVG** - Vector graphics for TrustMeter
- **Expo Image Picker** - Camera and gallery access
- **Expo Haptics** - Tactile feedback
- **Expo Sharing** - Native sharing capabilities
- **i18next** - Internationalization framework
- **react-i18next** - React integration for i18n

### Mock Data
The app includes comprehensive mock data:
- Sample users with avatars and verification status
- Demo posts with various trust scores and categories
- Community examples with different privacy levels
- Realistic API response simulation with delays

## 📊 Performance Optimizations

- **Lazy Loading**: Components load on demand
- **Image Optimization**: Expo Image with caching
- **Memory Management**: Proper cleanup of listeners
- **Bundle Splitting**: Optimized for fast startup
- **Native Performance**: Leverages platform-specific optimizations
- **Mobile-First Rendering**: Optimized component rendering for mobile

## 🔒 Security & Privacy

- **No Real Data**: All demo data is mock/simulated
- **Permission Handling**: Proper camera/gallery permissions
- **Secure Storage**: AsyncStorage for local data
- **API Security**: Prepared for JWT authentication
- **Privacy Compliance**: GDPR-ready data handling

## 🌐 Deployment Options

### Expo Go (Current)
- Instant testing on device
- No app store required
- Perfect for demos and development

### Standalone Builds
```bash
# Build for app stores
npx eas build --platform all

# Create development build
npx eas build --profile development
```

### Web Version
```bash
# Run as web app
npx expo start --web
```

## 🎨 Customization

### Theming
Colors and styles are centralized in component StyleSheets:
- Primary: `#0d9488` (Teal)
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Orange)
- Error: `#ef4444` (Red)

### Language Support
Add new languages by:
1. Creating new JSON file in `i18n/locales/`
2. Adding language to `i18n/index.ts`
3. Updating language selector in profile
### Adding Features
1. Create new screen in `app/` directory
2. Add components in `components/`
3. Update navigation in `_layout.tsx`
4. Add API endpoints in `services/api.ts`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test on device
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-name`
6. Submit Pull Request

## 📞 Support

For issues or questions:
- Check Expo documentation: https://docs.expo.dev/
- React Native guides: https://reactnative.dev/
- File issues in the repository

---

**Built with ❤️ for transparent, trustworthy fact-checking on mobile devices. Now supporting English, Hindi, and Tamil languages.**