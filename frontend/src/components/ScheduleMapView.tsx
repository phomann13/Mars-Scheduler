/**
 * Schedule Map View - Shows walking routes between classes using OpenStreetMap
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  Select,
  MenuItem,
  Card,
  CardContent,
  Stack,
  Chip,
  Divider,
  SelectChangeEvent,
} from '@mui/material';
import MapIcon from '@mui/icons-material/Map';
import DirectionsWalkIcon from '@mui/icons-material/DirectionsWalk';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import dynamic from 'next/dynamic';

// Dynamically import the map component to avoid SSR issues
const MapDisplay = dynamic(() => import('./MapDisplay'), { ssr: false });

interface ClassResult {
  crs: string;
  sections: string[];
  classType: string;
  startTime: number;
  endTime: number;
  location?: [number, number]; // [lat, lng]
  building?: string;
  walkingDistance?: number; // meters
  walkingDuration?: number; // seconds
}

interface ScheduleDay {
  dayOfWeek: string;
  classResults: ClassResult[];
}

interface VenusSchedule {
  earliestStartTime: number;
  earliestEndTime: number;
  credits: number;
  scheduleDays: ScheduleDay[];
  termId?: string;
  courses?: string[];
}

interface ScheduleMapViewProps {
  schedule?: VenusSchedule;
  scheduleIndex?: number;
  totalSchedules?: number;
}

const DAYS_OF_WEEK = [
  'MONDAY',
  'TUESDAY',
  'WEDNESDAY',
  'THURSDAY',
  'FRIDAY',
  'SATURDAY',
  'SUNDAY',
];

const convertTimeToString = (timeInMinutes: number): string => {
  const hours = Math.floor(timeInMinutes / 60);
  const minutes = timeInMinutes % 60;
  const period = hours < 12 ? 'AM' : 'PM';
  const displayHours = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
};

const calculateWalkingTime = (distance: number): number => {
  // Average walking speed: 5 km/h = 83.3 m/min
  // distance in meters
  return Math.ceil(distance / 83.3);
};

export default function ScheduleMapView({
  schedule,
  scheduleIndex = 0,
  totalSchedules = 1,
}: ScheduleMapViewProps) {
  const [selectedDay, setSelectedDay] = useState<string>('');
  const [daySchedule, setDaySchedule] = useState<ScheduleDay | null>(null);

  // Get days that have classes
  const daysWithClasses = schedule?.scheduleDays.map((day) => day.dayOfWeek) || [];

  useEffect(() => {
    // Set default to first day with classes
    if (daysWithClasses.length > 0 && !selectedDay) {
      setSelectedDay(daysWithClasses[0]);
    }
  }, [schedule, daysWithClasses, selectedDay]);

  useEffect(() => {
    // Update day schedule when day changes
    if (selectedDay && schedule) {
      const day = schedule.scheduleDays.find((d) => d.dayOfWeek === selectedDay);
      setDaySchedule(day || null);
    }
  }, [selectedDay, schedule]);

  const handleDayChange = (event: SelectChangeEvent) => {
    setSelectedDay(event.target.value);
  };

  if (!schedule) {
    return (
      <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Route Map
        </Typography>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <MapIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="body1" color="text.secondary">
            No schedule selected. Generate a schedule to see your daily walking routes!
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h5">
            <MapIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            Walking Route Map
          </Typography>
          <Chip
            label={`Schedule ${scheduleIndex + 1} of ${totalSchedules}`}
            color="primary"
            variant="outlined"
          />
        </Stack>

        {/* Day Selector */}
        <FormControl fullWidth>
          <Select
            value={selectedDay}
            onChange={handleDayChange}
            displayEmpty
            disabled={daysWithClasses.length === 0}
          >
            <MenuItem value="" disabled>
              Select a day
            </MenuItem>
            {DAYS_OF_WEEK.map((day) => (
              <MenuItem
                key={day}
                value={day}
                disabled={!daysWithClasses.includes(day)}
              >
                {day.charAt(0) + day.slice(1).toLowerCase()}
                {!daysWithClasses.includes(day) && ' (No classes)'}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {daySchedule && daySchedule.classResults.length > 0 ? (
        <Box>
          {/* Map Display */}
          <Box sx={{ height: 400, mb: 3, borderRadius: 2, overflow: 'hidden' }}>
            <MapDisplay
              classes={daySchedule.classResults}
              day={selectedDay}
            />
          </Box>

          {/* Class List */}
          <Typography variant="h6" gutterBottom>
            {selectedDay.charAt(0) + selectedDay.slice(1).toLowerCase()} Schedule
          </Typography>
          <Stack spacing={2}>
            {daySchedule.classResults.map((classResult, idx) => (
              <Card key={idx} variant="outlined">
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" color="primary">
                        {classResult.crs}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {classResult.classType} • Sections: {classResult.sections.join(', ')}
                      </Typography>
                    </Box>
                    <Chip
                      icon={<AccessTimeIcon />}
                      label={`${convertTimeToString(classResult.startTime)} - ${convertTimeToString(classResult.endTime)}`}
                      size="small"
                    />
                  </Stack>

                  {classResult.building && (
                    <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LocationOnIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {classResult.building}
                      </Typography>
                    </Box>
                  )}

                  {idx < daySchedule.classResults.length - 1 && (
                    <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <DirectionsWalkIcon fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {Math.round(
                            (daySchedule.classResults[idx + 1].startTime - classResult.endTime)
                          )}{' '}
                          minutes until next class
                        </Typography>
                      </Stack>
                    </Box>
                  )}
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>
      ) : (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No classes scheduled for {selectedDay.toLowerCase()}.
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

