/**
 * Venus Schedule Viewer Component - Displays schedules from Venus UMD API
 */

'use client';

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Stack,
  Divider,
} from '@mui/material';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import EventNoteIcon from '@mui/icons-material/EventNote';

interface ClassResult {
  crs: string;
  sections: string[];
  classType: string;
  startTime: number;
  endTime: number;
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

interface VenusScheduleViewProps {
  schedules?: VenusSchedule[];
  semester?: string;
  year?: number;
  onScheduleIndexChange?: (index: number) => void;
}

const DAYS_ORDER = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'];

const convertTimeToString = (timeInMinutes: number): string => {
  const hours = Math.floor(timeInMinutes / 60);
  const minutes = timeInMinutes % 60;
  const period = hours < 12 ? 'AM' : 'PM';
  const displayHours = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
};

const getColorForCourse = (courseCode: string): string => {
  const colors = [
    '#1976d2', '#2e7d32', '#d32f2f', '#7b1fa2', 
    '#f57c00', '#0288d1', '#c2185b', '#5d4037'
  ];
  const hash = courseCode.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
};

const calculateTimePosition = (
  time: number, 
  earliestStart: number, 
  latestEnd: number
): { top: string; height: string } => {
  const totalMinutes = latestEnd - earliestStart;
  const startOffset = ((time - earliestStart) / totalMinutes) * 100;
  return { top: `${startOffset}%`, height: 'auto' };
};

export default function VenusScheduleView({ 
  schedules = [], 
  semester = 'Spring',
  year = 2026,
  onScheduleIndexChange 
}: VenusScheduleViewProps) {
  const [currentScheduleIndex, setCurrentScheduleIndex] = useState(0);
  
  const updateScheduleIndex = (newIndex: number) => {
    setCurrentScheduleIndex(newIndex);
    if (onScheduleIndexChange) {
      onScheduleIndexChange(newIndex);
    }
  };

  if (!schedules || schedules.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Schedule Options
        </Typography>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <EventNoteIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="body1" color="text.secondary">
            No schedules to display. Ask the AI assistant to generate a schedule with your courses!
          </Typography>
        </Box>
      </Paper>
    );
  }

  const currentSchedule = schedules[currentScheduleIndex];
  const hasMultipleSchedules = schedules.length > 1;

  const handlePreviousSchedule = () => {
    const newIndex = currentScheduleIndex > 0 ? currentScheduleIndex - 1 : schedules.length - 1;
    updateScheduleIndex(newIndex);
  };

  const handleNextSchedule = () => {
    const newIndex = currentScheduleIndex < schedules.length - 1 ? currentScheduleIndex + 1 : 0;
    updateScheduleIndex(newIndex);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5">
            Schedule Options - {semester} {year}
          </Typography>
          
          {hasMultipleSchedules && (
            <Stack direction="row" alignItems="center" spacing={2}>
              <Button
                variant="outlined"
                size="small"
                onClick={handlePreviousSchedule}
                startIcon={<NavigateBeforeIcon />}
              >
                Previous
              </Button>
              <Typography variant="body2" color="text.secondary">
                {currentScheduleIndex + 1} of {schedules.length}
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={handleNextSchedule}
                endIcon={<NavigateNextIcon />}
              >
                Next
              </Button>
            </Stack>
          )}
        </Stack>

        {/* Schedule Info */}
        <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
          <Chip 
            icon={<EventNoteIcon />}
            label={`${currentSchedule.credits} Credits`} 
            color="primary" 
            variant="outlined"
          />
          <Chip 
            icon={<AccessTimeIcon />}
            label={`${convertTimeToString(currentSchedule.earliestStartTime)} - ${convertTimeToString(currentSchedule.earliestEndTime)}`}
            color="secondary"
            variant="outlined"
          />
        </Stack>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Weekly Calendar View */}
      <Grid container spacing={1}>
        {DAYS_ORDER.map((day) => {
          const daySchedule = currentSchedule.scheduleDays.find(
            (sd) => sd.dayOfWeek === day
          );

          return (
            <Grid item xs={12} sm={6} md key={day}>
              <Card 
                variant="outlined" 
                sx={{ 
                  height: '100%',
                  minHeight: 300,
                  bgcolor: daySchedule ? 'background.paper' : 'grey.50'
                }}
              >
                <CardContent>
                  <Typography 
                    variant="subtitle2" 
                    fontWeight="bold" 
                    gutterBottom
                    sx={{ textAlign: 'center', mb: 2 }}
                  >
                    {day.charAt(0) + day.slice(1).toLowerCase()}
                  </Typography>

                  {daySchedule ? (
                    <Stack spacing={1.5}>
                      {daySchedule.classResults.map((classResult, idx) => (
                        <Box
                          key={idx}
                          sx={{
                            p: 1.5,
                            borderRadius: 1,
                            bgcolor: getColorForCourse(classResult.crs),
                            color: 'white',
                            border: '1px solid',
                            borderColor: 'divider',
                          }}
                        >
                          <Typography variant="body2" fontWeight="bold">
                            {classResult.crs}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {classResult.classType} • Sections: {classResult.sections.join(', ')}
                          </Typography>
                          <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                            <AccessTimeIcon sx={{ fontSize: 12, verticalAlign: 'middle', mr: 0.5 }} />
                            {convertTimeToString(classResult.startTime)} - {convertTimeToString(classResult.endTime)}
                          </Typography>
                        </Box>
                      ))}
                    </Stack>
                  ) : (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        No classes
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Course Summary */}
      <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          Course List
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {currentSchedule.courses?.map((course, idx) => (
            <Chip
              key={idx}
              label={course}
              sx={{
                bgcolor: getColorForCourse(course),
                color: 'white',
                fontWeight: 'medium',
              }}
            />
          ))}
        </Stack>
      </Box>
    </Paper>
  );
}

