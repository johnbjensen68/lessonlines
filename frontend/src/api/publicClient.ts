import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

// A plain axios client without the 401→/login redirect interceptor.
// Used for public endpoints that anonymous visitors may access.
const publicClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export default publicClient;
