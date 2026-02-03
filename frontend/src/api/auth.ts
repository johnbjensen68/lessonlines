import client from './client';
import { TokenResponse, User, RegisterRequest } from '../types';

export async function login(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await client.post<TokenResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
}

export async function register(data: RegisterRequest): Promise<User> {
  const response = await client.post<User>('/auth/register', data);
  return response.data;
}
