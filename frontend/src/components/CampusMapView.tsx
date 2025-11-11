'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  DirectionsWalk as WalkIcon
} from '@mui/icons-material';
import { Section } from '@/types';

interface Building {
  code: string;
  fullName: string;
  latitude: number;
  longitude: number;
  departments?: string[];
}

interface CampusMapViewProps {
  sections: Section[];
  highlightedBuildingCode?: string;
  onBuildingClick?: (buildingCode: string) => void;
}

const CampusMapView: React.FC<CampusMapViewProps> = ({
  sections,
  highlightedBuildingCode,
  onBuildingClick
}) => {
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [walkingTimes, setWalkingTimes] = useState<{[key: string]: number}>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadBuildingsData();
  }, []);

  useEffect(() => {
    if (buildings.length > 0 && sections.length > 0) {
      calculateWalkingTimes();
    }
  }, [buildings, sections]);

  useEffect(() => {
    // Initialize map when buildings are loaded
    if (buildings.length > 0 && mapRef.current) {
      initializeMap();
    }
  }, [buildings]);

  const loadBuildingsData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/campus/buildings`);
      
      if (!response.ok) {
        throw new Error('Failed to load buildings');
      }
      
      const data = await response.json();
      setBuildings(data.buildings || []);
      setError(null);
    } catch (err) {
      console.error('Error loading buildings:', err);
      setError('Failed to load campus map data');
    } finally {
      setIsLoading(false);
    }
  };

  const calculateWalkingTimes = async () => {
    const uniqueBuildings = [...new Set(sections.map(s => s.building).filter(Boolean))];
    const times: {[key: string]: number} = {};

    // Calculate walking times between consecutive classes
    for (let i = 0; i < sections.length - 1; i++) {
      const current = sections[i];
      const next = sections[i + 1];
      
      if (current.building && next.building && current.building !== next.building) {
        const key = `${current.building}-${next.building}`;
        
        if (!times[key]) {
          try {
            const response = await fetch(
              `${process.env.NEXT_PUBLIC_API_URL}/campus/walking-time?` +
              `building1=${current.building}&building2=${next.building}`
            );
            
            if (response.ok) {
              const data = await response.json();
              times[key] = data.walkingTimeMinutes;
            }
          } catch (err) {
            console.error('Error calculating walking time:', err);
          }
        }
      }
    }

    setWalkingTimes(times);
  };

  const initializeMap = () => {
    // This would integrate with Leaflet or similar
    // For now, we'll use a simple static representation
    console.log('Map initialized with', buildings.length, 'buildings');
  };

  const getBuildingColor = (buildingCode: string): string => {
    if (buildingCode === highlightedBuildingCode) {
      return '#f50057';
    }
    
    const sectionBuildings = sections.map(s => s.building);
    if (sectionBuildings.includes(buildingCode)) {
      return '#1976d2';
    }
    
    return '#757575';
  };

  const getSectionsInBuilding = (buildingCode: string): Section[] => {
    return sections.filter(s => s.building === buildingCode);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  const scheduledBuildings = buildings.filter(b => 
    sections.some(s => s.building === b.code)
  );

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LocationIcon color="primary" />
          Campus Map View
        </Typography>
        
        {/* Map Container */}
        <Box
          ref={mapRef}
          sx={{
            width: '100%',
            height: 400,
            bgcolor: '#e8f5e9',
            borderRadius: 2,
            position: 'relative',
            overflow: 'hidden',
            mb: 2
          }}
        >
          {/* Simple visual representation */}
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center'
            }}
          >
            <LocationIcon sx={{ fontSize: 64, color: 'primary.main', mb: 1 }} />
            <Typography variant="body1" color="text.secondary">
              UMD Campus
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {scheduledBuildings.length} buildings in your schedule
            </Typography>
          </Box>

          {/* Building markers overlay */}
          {scheduledBuildings.map((building, idx) => (
            <Box
              key={building.code}
              sx={{
                position: 'absolute',
                left: `${20 + (idx * 15)}%`,
                top: `${30 + (idx % 3) * 20}%`,
                cursor: 'pointer',
                '&:hover': {
                  transform: 'scale(1.2)',
                  transition: 'transform 0.2s'
                }
              }}
              onClick={() => onBuildingClick?.(building.code)}
            >
              <LocationIcon
                sx={{
                  fontSize: 40,
                  color: getBuildingColor(building.code),
                  filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))'
                }}
              />
              <Typography
                variant="caption"
                sx={{
                  position: 'absolute',
                  top: -20,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  bgcolor: 'white',
                  px: 0.5,
                  borderRadius: 0.5,
                  fontWeight: 'bold',
                  whiteSpace: 'nowrap'
                }}
              >
                {building.code}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* Legend */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip
            icon={<LocationIcon />}
            label="Your Buildings"
            sx={{ bgcolor: '#1976d2', color: 'white' }}
            size="small"
          />
          <Chip
            icon={<LocationIcon />}
            label="Other Buildings"
            sx={{ bgcolor: '#757575', color: 'white' }}
            size="small"
          />
        </Box>
      </Paper>

      {/* Building Details */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Buildings in Your Schedule
        </Typography>
        
        {scheduledBuildings.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No building information available for your classes.
          </Typography>
        ) : (
          <List>
            {scheduledBuildings.map((building) => {
              const sectionsInBuilding = getSectionsInBuilding(building.code);
              
              return (
                <React.Fragment key={building.code}>
                  <ListItem
                    button
                    onClick={() => onBuildingClick?.(building.code)}
                    sx={{
                      bgcolor: building.code === highlightedBuildingCode ? 'action.selected' : 'inherit',
                      borderRadius: 1,
                      mb: 1
                    }}
                  >
                    <LocationIcon
                      sx={{
                        mr: 2,
                        color: getBuildingColor(building.code)
                      }}
                    />
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {building.code}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {building.fullName}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Classes: {sectionsInBuilding.map(s => s.course?.courseCode).join(', ')}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            📍 {building.latitude.toFixed(4)}, {building.longitude.toFixed(4)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              );
            })}
          </List>
        )}
      </Paper>

      {/* Walking Times */}
      {Object.keys(walkingTimes).length > 0 && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WalkIcon color="primary" />
            Walking Times Between Classes
          </Typography>
          
          <List dense>
            {Object.entries(walkingTimes).map(([key, minutes]) => {
              const [building1, building2] = key.split('-');
              return (
                <ListItem key={key}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2">
                          {building1} → {building2}
                        </Typography>
                        <Chip
                          label={`${minutes} min`}
                          size="small"
                          color={minutes > 10 ? 'warning' : 'success'}
                        />
                      </Box>
                    }
                  />
                </ListItem>
              );
            })}
          </List>
        </Paper>
      )}

      {/* Integration Note */}
      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          <strong>Note:</strong> This is a simplified map view. Full interactive map with 
          OpenStreetMap integration is available. Walking times are calculated using actual 
          campus pathways.
        </Typography>
      </Alert>
    </Box>
  );
};

export default CampusMapView;

