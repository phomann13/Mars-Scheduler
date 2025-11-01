/**
 * Four-year plan visualization component.
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
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import SchoolIcon from '@mui/icons-material/School';
import type { FourYearPlan, SemesterPlan } from '@/types';

interface FourYearPlanViewProps {
  plan?: FourYearPlan;
}

export default function FourYearPlanView({ plan }: FourYearPlanViewProps) {
  if (!plan) {
    return (
      <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Four-Year Plan
        </Typography>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No plan to display. Ask the AI assistant to generate a four-year plan!
          </Typography>
        </Box>
      </Paper>
    );
  }
  
  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        {plan.planName}
      </Typography>
      
      <Timeline position="alternate">
        {plan.semesterPlans.map((semester: SemesterPlan, index: number) => (
          <TimelineItem key={index}>
            <TimelineSeparator>
              <TimelineDot color="primary">
                <SchoolIcon />
              </TimelineDot>
              {index < plan.semesterPlans.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            
            <TimelineContent>
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {semester.semester} {semester.year}
                  </Typography>
                  
                  <Chip
                    label={`${semester.totalCredits} Credits`}
                    color="primary"
                    size="small"
                    sx={{ mb: 2 }}
                  />
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {semester.courses.map((course: string, courseIndex: number) => (
                      <Box
                        key={courseIndex}
                        sx={{
                          p: 1.5,
                          bgcolor: 'grey.100',
                          borderRadius: 1,
                          borderLeft: 3,
                          borderColor: 'primary.main',
                        }}
                      >
                        <Typography variant="body2" fontWeight="medium">
                          {course}
                        </Typography>
                      </Box>
                    ))}
                    
                    {semester.courses.length === 0 && (
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        No courses planned
                      </Typography>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
      
      {/* Plan Summary */}
      <Box sx={{ mt: 4, pt: 3, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          Plan Summary
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="primary">
                  {plan.semesterPlans.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Semesters
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="primary">
                  {plan.semesterPlans.reduce((sum: number, sem: SemesterPlan) => sum + sem.courses.length, 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Courses
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="primary">
                  {plan.semesterPlans.reduce((sum: number, sem: SemesterPlan) => sum + sem.totalCredits, 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Credits
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
}

