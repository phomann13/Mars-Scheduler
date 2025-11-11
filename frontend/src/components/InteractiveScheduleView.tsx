'use client';

import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Alert
} from '@mui/material';
import {
  Delete as DeleteIcon,
  SwapHoriz as SwapIcon,
  Warning as WarningIcon,
  DirectionsWalk as WalkIcon
} from '@mui/icons-material';
import { Schedule, Section } from '@/types';

interface InteractiveScheduleViewProps {
  schedule: Schedule;
  onSectionRemove?: (sectionId: number) => void;
  onSectionSwap?: (sectionId: number) => void;
  showWalkingTimes?: boolean;
}

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const TIME_SLOTS = [
  '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
  '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM'
];

const InteractiveScheduleView: React.FC<InteractiveScheduleViewProps> = ({
  schedule,
  onSectionRemove,
  onSectionSwap,
  showWalkingTimes = true
}) => {
  const [hoveredSection, setHoveredSection] = useState<number | null>(null);

  const getSectionColor = useCallback((courseCode: string): string => {
    // Generate consistent color based on course code
    const hash = courseCode.split('').reduce((acc, char) => 
      char.charCodeAt(0) + ((acc << 5) - acc), 0);
    
    const colors = [
      '#e3f2fd', '#f3e5f5', '#e8f5e9', '#fff3e0', '#fce4ec',
      '#e0f2f1', '#f1f8e9', '#ede7f6', '#e8eaf6', '#ffebee'
    ];
    
    return colors[Math.abs(hash) % colors.length];
  }, []);

  const parseTimeToMinutes = (timeStr: string): number => {
    const [time, period] = timeStr.split(' ');
    const [hours, minutes] = time.split(':').map(Number);
    let totalHours = hours;
    
    if (period === 'PM' && hours !== 12) {
      totalHours += 12;
    } else if (period === 'AM' && hours === 12) {
      totalHours = 0;
    }
    
    return totalHours * 60 + minutes;
  };

  const calculatePosition = (startTime: string, endTime: string) => {
    const startMinutes = parseTimeToMinutes(startTime);
    const endMinutes = parseTimeToMinutes(endTime);
    const baseMinutes = parseTimeToMinutes('8:00 AM');
    
    const top = ((startMinutes - baseMinutes) / 60) * 100;
    const height = ((endMinutes - startMinutes) / 60) * 100;
    
    return { top, height };
  };

  const getSectionsForDay = (day: string): Section[] => {
    return schedule.sections.filter(section =>
      section.days.includes(day.substring(0, 2))
    );
  };

  const renderSection = (section: Section, day: string) => {
    const { top, height } = calculatePosition(section.startTime, section.endTime);
    const color = getSectionColor(section.course?.courseCode || '');
    const isHovered = hoveredSection === section.id;

    return (
      <Box
        key={`${section.id}-${day}`}
        sx={{
          position: 'absolute',
          top: `${top}px`,
          left: '10px',
          right: '10px',
          height: `${height}px`,
          minHeight: '80px',
          backgroundColor: color,
          border: isHovered ? '2px solid #1976d2' : '1px solid #ccc',
          borderRadius: 1,
          p: 1,
          cursor: 'pointer',
          transition: 'all 0.2s',
          '&:hover': {
            boxShadow: 3,
            transform: 'scale(1.02)',
            zIndex: 10
          },
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}
        onMouseEnter={() => setHoveredSection(section.id)}
        onMouseLeave={() => setHoveredSection(null)}
      >
        <Box>
          <Typography variant="subtitle2" fontWeight="bold" noWrap>
            {section.course?.courseCode}
          </Typography>
          <Typography variant="caption" display="block" noWrap>
            {section.professor?.name || 'TBA'}
          </Typography>
          <Typography variant="caption" display="block">
            {section.startTime} - {section.endTime}
          </Typography>
          {section.building && (
            <Typography variant="caption" display="block" noWrap>
              📍 {section.building} {section.room}
            </Typography>
          )}
        </Box>
        
        {isHovered && (
          <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
            {onSectionSwap && (
              <Tooltip title="Swap Section">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSectionSwap(section.id);
                  }}
                  sx={{ p: 0.5, bgcolor: 'white' }}
                >
                  <SwapIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {onSectionRemove && (
              <Tooltip title="Remove Section">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSectionRemove(section.id);
                  }}
                  sx={{ p: 0.5, bgcolor: 'white' }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box>
      {/* Walking Time Warnings */}
      {showWalkingTimes && schedule.walkingTimeWarnings && schedule.walkingTimeWarnings.length > 0 && (
        <Alert severity="warning" icon={<WalkIcon />} sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Walking Time Alerts:
          </Typography>
          {schedule.walkingTimeWarnings.map((warning: any, idx: number) => (
            <Typography key={idx} variant="body2">
              • {warning.message}
            </Typography>
          ))}
        </Alert>
      )}

      {/* Schedule Grid */}
      <Paper sx={{ p: 2, overflow: 'auto' }}>
        <Grid container spacing={1}>
          {/* Time Column */}
          <Grid item xs={1}>
            <Box sx={{ position: 'sticky', top: 0, bgcolor: 'background.paper', zIndex: 1 }}>
              <Typography variant="caption" sx={{ height: 40, display: 'block' }}>
                Time
              </Typography>
              {TIME_SLOTS.map((time, idx) => (
                <Box
                  key={time}
                  sx={{
                    height: 100,
                    borderTop: '1px solid #e0e0e0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    {time}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Grid>

          {/* Day Columns */}
          {DAYS.map((day) => (
            <Grid item xs={2.2} key={day}>
              <Box>
                {/* Day Header */}
                <Box
                  sx={{
                    height: 40,
                    bgcolor: 'primary.main',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 1,
                    mb: 1
                  }}
                >
                  <Typography variant="subtitle2" fontWeight="bold">
                    {day}
                  </Typography>
                </Box>

                {/* Time Grid */}
                <Box sx={{ position: 'relative' }}>
                  {TIME_SLOTS.map((time, idx) => (
                    <Box
                      key={time}
                      sx={{
                        height: 100,
                        borderTop: '1px solid #e0e0e0',
                        borderLeft: '1px solid #e0e0e0',
                        borderRight: '1px solid #e0e0e0',
                        bgcolor: 'background.paper'
                      }}
                    />
                  ))}

                  {/* Sections */}
                  {getSectionsForDay(day).map((section) =>
                    renderSection(section, day)
                  )}
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Legend */}
      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Typography variant="subtitle2" sx={{ width: '100%' }}>
          Course Legend:
        </Typography>
        {schedule.sections.map((section) => (
          <Chip
            key={section.id}
            label={`${section.course?.courseCode} - ${section.professor?.name || 'TBA'}`}
            sx={{
              bgcolor: getSectionColor(section.course?.courseCode || ''),
              border: '1px solid #ccc'
            }}
            size="small"
          />
        ))}
      </Box>
    </Box>
  );
};

export default InteractiveScheduleView;

