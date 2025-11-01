/**
 * Main application page for the UMD AI Scheduling Assistant.
 */

'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import SchoolIcon from '@mui/icons-material/School';
import ChatIcon from '@mui/icons-material/Chat';
import ChatInterface from '@/components/ChatInterface';
import ScheduleView from '@/components/ScheduleView';
import FourYearPlanView from '@/components/FourYearPlanView';

export default function Home() {
  const [activeTab, setActiveTab] = useState(0);
  const [currentSchedule, setCurrentSchedule] = useState<any>(null);
  const [currentPlan, setCurrentPlan] = useState<any>(null);
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  
  const handleScheduleGenerated = (schedule: any) => {
    setCurrentSchedule(schedule);
    setActiveTab(1); // Switch to schedule tab
  };
  
  const handlePlanGenerated = (plan: any) => {
    setCurrentPlan(plan);
    setActiveTab(2); // Switch to plan tab
  };
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <SchoolIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            UMD AI Scheduling Assistant
          </Typography>
        </Toolbar>
      </AppBar>
      
      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Grid container spacing={3} sx={{ height: 'calc(100vh - 150px)' }}>
          {/* Chat Interface - Left Side */}
          <Grid item xs={12} md={5} sx={{ height: '100%' }}>
            <ChatInterface
              userId="demo-user"
              onScheduleGenerated={handleScheduleGenerated}
              onPlanGenerated={handlePlanGenerated}
            />
          </Grid>
          
          {/* Main View - Right Side */}
          <Grid item xs={12} md={7} sx={{ height: '100%' }}>
            <Paper elevation={3} sx={{ height: '100%', borderRadius: 2, overflow: 'hidden' }}>
              <Tabs
                value={activeTab}
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab icon={<ChatIcon />} label="Assistant" />
                <Tab icon={<CalendarTodayIcon />} label="Schedule" />
                <Tab icon={<SchoolIcon />} label="4-Year Plan" />
              </Tabs>
              
              <Box sx={{ p: 3, height: 'calc(100% - 64px)', overflowY: 'auto' }}>
                {activeTab === 0 && (
                  <Box>
                    <Typography variant="h5" gutterBottom>
                      Welcome to UMD AI Scheduling Assistant
                    </Typography>
                    <Typography variant="body1" paragraph>
                      Get started by asking me questions about:
                    </Typography>
                    <Box component="ul" sx={{ pl: 3 }}>
                      <Typography component="li" variant="body1">
                        Building your semester schedule
                      </Typography>
                      <Typography component="li" variant="body1">
                        Generating a four-year academic plan
                      </Typography>
                      <Typography component="li" variant="body1">
                        Finding courses and professors
                      </Typography>
                      <Typography component="li" variant="body1">
                        Understanding degree requirements
                      </Typography>
                    </Box>
                    <Typography variant="body1" sx={{ mt: 3 }}>
                      I use data from PlanetTerp and RateMyProfessor to help you make informed decisions about your courses!
                    </Typography>
                  </Box>
                )}
                
                {activeTab === 1 && (
                  <ScheduleView sections={currentSchedule?.sections || []} />
                )}
                
                {activeTab === 2 && (
                  <FourYearPlanView plan={currentPlan} />
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>
      
      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 2,
          px: 2,
          mt: 'auto',
          backgroundColor: 'grey.100',
        }}
      >
        <Container maxWidth="xl">
          <Typography variant="body2" color="text.secondary" align="center">
            UMD AI Scheduling Assistant - Helping Terps plan their academic journey
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}

