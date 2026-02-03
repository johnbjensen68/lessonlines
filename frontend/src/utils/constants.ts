export const API_BASE_URL = '/api';

export const COLOR_SCHEMES = {
  blue_green: {
    name: 'Blue to Green',
    gradient: 'linear-gradient(90deg, #3498db, #2ecc71)',
    primary: '#3498db',
    secondary: '#2ecc71',
  },
  red_orange: {
    name: 'Red to Orange',
    gradient: 'linear-gradient(90deg, #e74c3c, #f39c12)',
    primary: '#e74c3c',
    secondary: '#f39c12',
  },
  purple_blue: {
    name: 'Purple to Blue',
    gradient: 'linear-gradient(90deg, #9b59b6, #3498db)',
    primary: '#9b59b6',
    secondary: '#3498db',
  },
  dark: {
    name: 'Dark',
    gradient: '#34495e',
    primary: '#34495e',
    secondary: '#34495e',
  },
};

export const FONTS = {
  system: {
    name: 'System Default',
    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif',
  },
  serif: {
    name: 'Serif',
    family: 'Georgia, Cambria, "Times New Roman", serif',
  },
  rounded: {
    name: 'Rounded',
    family: 'Nunito, Quicksand, sans-serif',
  },
};

export const LAYOUTS = {
  horizontal: 'Horizontal',
  vertical: 'Vertical',
};

export const LOCAL_STORAGE_TOKEN_KEY = 'lessonlines_token';
