interface JwtPayload {
  sub: string;
  exp?: number;
  iat?: number;
  is_admin?: boolean;
}

export function jwtDecode(token: string): JwtPayload {
  const parts = token.split('.');
  if (parts.length !== 3) {
    throw new Error('Invalid JWT token');
  }

  const payload = parts[1];
  const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
  return JSON.parse(decoded);
}
