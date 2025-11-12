# Venus UMD Schedule API Integration

This document explains how the Mars Scheduler integrates with the Venus UMD Schedule API for generating optimized semester schedules.

## Overview

The Venus UMD Schedule API is used to generate conflict-free semester schedules based on course selections. The API is accessed via the `VenusScheduleService` in the backend.

## API Reference

**Base URL:** `https://venus.umd.edu/api/schedule`

### Parameters

- `termId` - Semester term ID (e.g., "202601" for Spring 2026)
- `requiredCourses` - Comma-separated list of required course codes (e.g., "CMSC131,MATH140,ENGL101")
- `optionalCourses` - Comma-separated list of optional course codes (default: "")
- `requiredSections` - Comma-separated list of section preferences (use "All" for each required course)
- `minCredits` - Minimum credit hours (default: 1)
- `maxCredits` - Maximum credit hours (default: 20)
- `waitlistLimit` - Waitlist seat limit (default: -1 for unlimited)
- `teachingCenter` - Teaching center filter (default: "*" for all)
- `delivery` - Delivery method filter (default: "" for all)

### Example Request

```
GET https://venus.umd.edu/api/schedule?termId=202601&requiredCourses=CMSC131,MATH140,ENGL101,COMM107,CMSC100&optionalCourses=&requiredSections=All,All,All,All,All&optionalSections=&exclusions=&minCredits=1&maxCredits=20&waitlistLimit=-1&dsstate=&teachingCenter=*&delivery=
```

## Response Format

The API returns an array of schedule objects. Each schedule contains:

```typescript
{
  "earliestStartTime": number,      // Earliest class start time in minutes from midnight (e.g., 480 = 8:00 AM)
  "earliestEndTime": number,        // Latest class end time in minutes from midnight
  "credits": number,                // Total credits for the schedule
  "scheduleDays": [                 // Array of days with classes
    {
      "dayOfWeek": string,          // Day name (MONDAY, TUESDAY, etc.)
      "classResults": [             // Array of classes on this day
        {
          "crs": string,            // Course code (e.g., "CMSC131")
          "sections": string[],     // Section numbers (e.g., ["0105"])
          "classType": string,      // Type (Lec, Dis, Lab)
          "startTime": number,      // Class start time in minutes
          "endTime": number         // Class end time in minutes
        }
      ],
      "percentages": [...]          // Visualization data
    }
  ]
}
```

## Usage in Chat Interface

Users can request schedule generation through natural language:

### Example Queries

1. **"Generate a schedule with CMSC131, MATH140, ENGL101, COMM107, and CMSC100"**
2. **"Create my schedule for Spring 2026"**
3. **"I need a schedule for these courses: CMSC131, MATH140"**

### Intent Detection

The AI assistant automatically detects schedule generation intent and extracts:
- Course codes from the message
- Semester (defaults to Spring)
- Year (defaults to 2026)
- Credit limits (optional)

### Backend Flow

1. User sends message → `POST /api/chat`
2. Intent extraction identifies courses and semester
3. `handleScheduleGeneration()` calls `venusScheduleService.generateSchedules()`
4. Venus API returns multiple schedule options
5. Top 5 schedules are returned to frontend
6. Frontend displays schedules in `VenusScheduleView` component

## Term ID Format

Term IDs follow the format: `YYYYMM`
- YYYY = Year
- MM = Semester code

### Semester Codes
- `01` = Spring
- `05` = Summer
- `08` = Fall
- `12` = Winter

### Examples
- Spring 2026 = `202601`
- Fall 2025 = `202508`
- Summer 2026 = `202605`

## Frontend Component

The `VenusScheduleView` component displays schedules in a weekly calendar format with:
- Navigation between multiple schedule options
- Color-coded courses
- Time information for each class
- Section details
- Credit summary

## Time Conversion

Times are stored as minutes from midnight (0-1439):
- 8:00 AM = 480 minutes
- 12:00 PM = 720 minutes
- 5:00 PM = 1020 minutes

The `convertTimeToString()` helper function converts these to readable format (e.g., "9:00 AM").

## Error Handling

The service includes error handling for:
- HTTP errors from Venus API
- Network timeouts
- Invalid course codes
- No available schedules

If schedule generation fails, the user receives a friendly error message.

## Testing

To test the integration:

1. Start the backend server
2. Send a chat message: "Generate a schedule with CMSC131, MATH140, ENGL101"
3. View generated schedules in the Schedule tab
4. Navigate between different schedule options

## Future Enhancements

Potential improvements:
- Filter by professor ratings
- Filter by time preferences (morning/afternoon/evening)
- Exclude specific days
- Optimize for minimal walking distance between buildings
- Save favorite schedules

