# UMD AI Scheduling Assistant - Frontend

Next.js frontend for the UMD AI Scheduling Assistant.

## Structure

```
frontend/
├── src/
│   ├── app/                # Next.js App Router
│   │   ├── layout.tsx      # Root layout
│   │   ├── page.tsx        # Main page
│   │   └── theme.ts        # MUI theme configuration
│   ├── components/         # React components
│   │   ├── ChatInterface.tsx        # Chat UI
│   │   ├── ScheduleView.tsx         # Schedule visualization
│   │   └── FourYearPlanView.tsx     # Plan visualization
│   ├── services/           # API services
│   │   └── api.ts          # Backend API client
│   └── types/              # TypeScript types
│       └── index.ts        # Type definitions
├── package.json
├── tsconfig.json
└── next.config.js
```

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Open http://localhost:3000

## Build

```bash
npm run build
npm start
```

## Features

### Chat Interface
- Real-time messaging with AI assistant
- Message history
- Suggestion chips
- Loading states

### Schedule View
- Weekly calendar visualization
- Course cards with professor ratings
- Schedule summary
- Time conflict detection

### Four-Year Plan View
- Timeline visualization
- Semester breakdowns
- Credit tracking
- Plan summary statistics

## Components

### ChatInterface
Props:
- `userId`: User identifier
- `onScheduleGenerated`: Callback for schedule generation
- `onPlanGenerated`: Callback for plan generation

### ScheduleView
Props:
- `sections`: Array of course sections
- `title`: Optional title

### FourYearPlanView
Props:
- `plan`: Four-year plan object

## API Integration

The frontend communicates with the backend via the API service:

```typescript
import { chatApi, scheduleApi, planApi, courseApi } from '@/services/api';

// Send chat message
const response = await chatApi.sendMessage(userId, message);

// Generate schedule
const schedules = await scheduleApi.generateSchedules(params);

// Generate plan
const plan = await planApi.generatePlan(params);
```

## Styling

Uses Material-UI (MUI) with custom theme:
- Primary color: UMD Red (#E03A3E)
- Secondary color: UMD Gold (#FFD200)
- Custom typography and components

## Environment Variables

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Code Style

Following user-defined rules:
- Use camelCase for variables and functions
- Use TypeScript for type safety
- Use MUI components (no separate CSS files)
- Keep components focused and reusable
- Use arrow functions for simple logic

