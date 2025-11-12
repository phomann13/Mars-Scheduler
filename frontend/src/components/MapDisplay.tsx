/**
 * MapDisplay component - Renders OpenStreetMap with walking routes using OSRM
 */

'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Box, Typography, CircularProgress } from '@mui/material';

// Fix for default marker icons in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Create custom colored marker icons
const createColoredIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="position: relative; width: 32px; height: 42px;">
        <svg width="32" height="42" viewBox="0 0 32 42" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
          <path d="M16 0C7.2 0 0 7.2 0 16c0 11.7 16 26 16 26s16-14.3 16-26C32 7.2 24.8 0 16 0z" 
                fill="${color}" 
                stroke="#fff" 
                stroke-width="2"/>
          <circle cx="16" cy="16" r="6" fill="#fff"/>
        </svg>
      </div>
    `,
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -42],
  });
};

interface ClassResult {
  crs: string;
  sections: string[];
  classType: string;
  startTime: number;
  endTime: number;
  location?: [number, number];
  building?: string;
}

interface MapDisplayProps {
  classes: ClassResult[];
  day: string;
}

// Component to fit map bounds to markers
function MapBoundsSetter({ positions }: { positions: [number, number][] }) {
  const map = useMap();
  
  useEffect(() => {
    if (positions.length > 0) {
      const bounds = L.latLngBounds(positions);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [positions, map]);
  
  return null;
}

const convertTimeToString = (timeInMinutes: number): string => {
  const hours = Math.floor(timeInMinutes / 60);
  const minutes = timeInMinutes % 60;
  const period = hours < 12 ? 'AM' : 'PM';
  const displayHours = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
};

// Color palette for different classes
const getColorForIndex = (index: number): string => {
  const colors = ['#1976d2', '#2e7d32', '#d32f2f', '#7b1fa2', '#f57c00', '#0288d1'];
  return colors[index % colors.length];
};

// OSRM route interface
interface OSRMRoute {
  positions: [number, number][];
  distance: number; // meters
  duration: number; // seconds
  color: string;
}

// Fetch route from OSRM API
async function fetchOSRMRoute(
  start: [number, number],
  end: [number, number]
): Promise<{ coordinates: [number, number][]; distance: number; duration: number } | null> {
  try {
    // OSRM expects coordinates as lng,lat (not lat,lng!)
    const url = `https://router.project-osrm.org/route/v1/walking/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
      const route = data.routes[0];
      // Convert GeoJSON coordinates (lng,lat) back to Leaflet format (lat,lng)
      const coordinates = route.geometry.coordinates.map(
        (coord: [number, number]) => [coord[1], coord[0]] as [number, number]
      );
      
      return {
        coordinates,
        distance: route.distance, // meters
        duration: route.duration, // seconds
      };
    }
    
    return null;
  } catch (error) {
    console.error('Error fetching OSRM route:', error);
    return null;
  }
}

export default function MapDisplay({ classes, day }: MapDisplayProps) {
  const [routes, setRoutes] = useState<OSRMRoute[]>([]);
  const [isLoadingRoutes, setIsLoadingRoutes] = useState(false);
  
  // Filter classes that have location data
  const classesWithLocation = useMemo(
    () => classes.filter((c) => c.location && c.location.length === 2),
    [classes]
  );

  // Extract positions for bounds
  const positions = useMemo(
    () => classesWithLocation.map((c) => c.location!),
    [classesWithLocation]
  );

  // Fetch OSRM routes when classes change
  useEffect(() => {
    const fetchRoutes = async () => {
      if (classesWithLocation.length < 2) {
        setRoutes([]);
        return;
      }

      setIsLoadingRoutes(true);
      const fetchedRoutes: OSRMRoute[] = [];

      for (let i = 0; i < classesWithLocation.length - 1; i++) {
        const start = classesWithLocation[i].location!;
        const end = classesWithLocation[i + 1].location!;
        
        const routeData = await fetchOSRMRoute(start, end);
        
        if (routeData) {
          fetchedRoutes.push({
            positions: routeData.coordinates,
            distance: routeData.distance,
            duration: routeData.duration,
            color: getColorForIndex(i),
          });
        } else {
          // Fallback to straight line if OSRM fails
          fetchedRoutes.push({
            positions: [start, end],
            distance: 0,
            duration: 0,
            color: getColorForIndex(i),
          });
        }
      }

      setRoutes(fetchedRoutes);
      setIsLoadingRoutes(false);
    };

    fetchRoutes();
  }, [classesWithLocation]);

  // Default center (UMD campus)
  const defaultCenter: [number, number] = [38.9869, -76.9426];
  const center = positions.length > 0 ? positions[0] : defaultCenter;

  if (classesWithLocation.length === 0) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.100',
          borderRadius: 2,
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Location data not available for these classes
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ position: 'relative', height: '100%', width: '100%' }}>
      {isLoadingRoutes && (
        <Box
          sx={{
            position: 'absolute',
            top: 10,
            right: 10,
            zIndex: 1000,
            bgcolor: 'white',
            p: 1,
            borderRadius: 1,
            boxShadow: 2,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          <CircularProgress size={20} />
          <Typography variant="caption">Loading routes...</Typography>
        </Box>
      )}
      
      <MapContainer
        center={center}
        zoom={15}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Routes by <a href="http://project-osrm.org/">OSRM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapBoundsSetter positions={positions} />

                    {/* Render markers for each class location */}
                    {classesWithLocation.map((classResult, idx) => {
                      // Find walking info for this segment
                      const walkingInfo = idx < routes.length ? routes[idx] : null;
                      const markerColor = getColorForIndex(idx);

                      return (
                        <Marker key={idx} position={classResult.location!} icon={createColoredIcon(markerColor)}>
              <Popup>
                <Box sx={{ p: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {classResult.crs}
                  </Typography>
                  <Typography variant="caption" display="block">
                    {classResult.classType} • {classResult.sections.join(', ')}
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                    {convertTimeToString(classResult.startTime)} -{' '}
                    {convertTimeToString(classResult.endTime)}
                  </Typography>
                  {classResult.building && (
                    <Typography variant="caption" display="block" color="text.secondary">
                      📍 {classResult.building}
                    </Typography>
                  )}
                  {walkingInfo && walkingInfo.distance > 0 && (
                    <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid #ddd' }}>
                      <Typography variant="caption" display="block" fontWeight="bold">
                        Walking to next class:
                      </Typography>
                      <Typography variant="caption" display="block">
                        🚶 {Math.round(walkingInfo.distance)} meters
                      </Typography>
                      <Typography variant="caption" display="block">
                        ⏱️ ~{Math.ceil(walkingInfo.duration / 60)} min walk
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Popup>
            </Marker>
          );
        })}

        {/* Render OSRM walking routes between classes */}
        {routes.map((route, idx) => (
          <Polyline
            key={idx}
            positions={route.positions}
            pathOptions={{
              color: route.color,
              weight: 5,
              opacity: 0.8,
            }}
          />
        ))}
      </MapContainer>
    </Box>
  );
}

