import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { jwtDecode } from './jwtDecode';
import { login as apiLogin, register as apiRegister } from '../api/auth';
import { User, AuthState, RegisterRequest } from '../types';
import { LOCAL_STORAGE_TOKEN_KEY } from '../utils/constants';

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { token: string; user: User } }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' };

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem(LOCAL_STORAGE_TOKEN_KEY),
  isLoading: true,
  error: null,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        error: null,
      };
    case 'LOGIN_ERROR':
      return { ...state, isLoading: false, error: action.payload };
    case 'LOGOUT':
      return { ...state, user: null, token: null, isLoading: false };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const token = localStorage.getItem(LOCAL_STORAGE_TOKEN_KEY);
    if (token) {
      try {
        const decoded = jwtDecode(token);
        if (decoded.exp && decoded.exp * 1000 > Date.now()) {
          const user: User = {
            id: decoded.sub,
            email: '',
            display_name: null,
            is_pro: false,
            pro_purchased_at: null,
            created_at: '',
          };
          dispatch({ type: 'LOGIN_SUCCESS', payload: { token, user } });
        } else {
          localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY);
          dispatch({ type: 'LOGOUT' });
        }
      } catch {
        localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY);
        dispatch({ type: 'LOGOUT' });
      }
    } else {
      dispatch({ type: 'LOGOUT' });
    }
  }, []);

  const login = async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await apiLogin(email, password);
      localStorage.setItem(LOCAL_STORAGE_TOKEN_KEY, response.access_token);
      const decoded = jwtDecode(response.access_token);
      const user: User = {
        id: decoded.sub,
        email,
        display_name: null,
        is_pro: false,
        pro_purchased_at: null,
        created_at: '',
      };
      dispatch({ type: 'LOGIN_SUCCESS', payload: { token: response.access_token, user } });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      dispatch({ type: 'LOGIN_ERROR', payload: message });
      throw err;
    }
  };

  const register = async (data: RegisterRequest) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      await apiRegister(data);
      await login(data.email, data.password);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      dispatch({ type: 'LOGIN_ERROR', payload: message });
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY);
    dispatch({ type: 'LOGOUT' });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, clearError }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
