/**
 * Schedule visualization component.
 */

'use client';

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Rating,
} from '@mui/material';
import type { Section } from '@/types';

interface ScheduleViewProps {
  sections: Section[];
  title?: string;
}

export default function ScheduleView({ sections, title = 'Schedule' }: ScheduleViewProps) {
  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  
  const getSectionsForDay = (day: string) => {
    return sections.filter(section => section.days.includes(day));
  };
  
  const formatTime = (time: string) => {
    return time;
  };
  
  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        {title}
      </Typography>
      
      {sections.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No schedule to display. Start by chatting with the AI assistant!
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={2}>
          {daysOfWeek.map(day => (
            <Grid item xs={12} md key={day}>
              <Box>
                <Typography variant="h6" sx={{ mb: 1, textAlign: 'center' }}>
                  {day}
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {getSectionsForDay(day).map((section, index) => (
                    <Card
                      key={index}
                      variant="outlined"
                      sx={{
                        bgcolor: 'primary.light',
                        color: 'primary.contrastText',
                      }}
                    >
                      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {section.course?.courseCode}
                        </Typography>
                        <Typography variant="caption" display="block">
                          {formatTime(section.startTime)} - {formatTime(section.endTime)}
                        </Typography>
                        {section.professor && (
                          <Typography variant="caption" display="block">
                            {section.professor.name}
                          </Typography>
                        )}
                        {section.building && (
                          <Typography variant="caption" display="block">
                            {section.building} {section.room}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                  
                  {getSectionsForDay(day).length === 0 && (
                    <Box
                      sx={{
                        p: 2,
                        textAlign: 'center',
                        color: 'text.secondary',
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        borderStyle: 'dashed',
                      }}
                    >
                      <Typography variant="caption">No classes</Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Schedule Summary */}
      {sections.length > 0 && (
        <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="h6" gutterBottom>
            Schedule Summary
          </Typography>
          
          <Grid container spacing={2}>
            {sections.map((section, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {section.course?.courseCode}: {section.course?.courseName}
                    </Typography>
                    
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        {section.professor?.name}
                      </Typography>
                      
                      {section.professor?.aggregatedScore && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                          <Rating
                            value={section.professor.aggregatedScore}
                            precision={0.1}
                            size="small"
                            readOnly
                          />
                          <Typography variant="caption" sx={{ ml: 1 }}>
                            ({section.professor.aggregatedScore.toFixed(1)})
                          </Typography>
                        </Box>
                      )}
                    </Box>
                    
                    <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {section.days.map(day => (
                        <Chip key={day} label={day.substring(0, 3)} size="small" />
                      ))}
                    </Box>
                    
                    <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                      {section.startTime} - {section.endTime}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Paper>
  );
}

