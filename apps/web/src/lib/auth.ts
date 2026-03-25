import { API_BASE_URL } from './config';
/**
 * JWT Authentication Utilities
 * Token management and API calls
 */


export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
}

/**
 * Login with email and password
 */
export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data: TokenResponse = await response.json();
  
  // Save tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('token_expires_at', (Date.now() + data.expires_in * 1000).toString());
  
  return data;
};

/**
 * Register a new account
 */
export const register = async (email: string, password: string, displayName?: string): Promise<TokenResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, display_name: displayName }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  const data: TokenResponse = await response.json();

  // Save tokens (auto-login)
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('token_expires_at', (Date.now() + data.expires_in * 1000).toString());

  return data;
};

/**
 * Request password reset
 */
export const forgotPassword = async (email: string): Promise<{ message: string; reset_token?: string }> => {
  const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password?email=${encodeURIComponent(email)}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return await response.json();
};

/**
 * Reset password with token
 */
export const resetPassword = async (token: string, newPassword: string): Promise<{ message: string }> => {
  const response = await fetch(`${API_BASE_URL}/api/auth/reset-password?token=${encodeURIComponent(token)}&new_password=${encodeURIComponent(newPassword)}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Reset failed');
  }

  return await response.json();
};

/**
 * Refresh access token
 */
export const refreshToken = async (): Promise<TokenResponse> => {
  const refresh_token = localStorage.getItem('refresh_token');
  
  if (!refresh_token) {
    throw new Error('No refresh token');
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token }),
  });

  if (!response.ok) {
    // Refresh failed, clear tokens
    logout();
    throw new Error('Token refresh failed');
  }

  const data: TokenResponse = await response.json();
  
  // Save new tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('token_expires_at', (Date.now() + data.expires_in * 1000).toString());
  
  return data;
};

/**
 * Get current user info
 */
export const getCurrentUser = async (): Promise<User | null> => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, try refresh
        try {
          await refreshToken();
          // Retry with new token
          const newToken = localStorage.getItem('access_token');
          const retryResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${newToken}`,
            },
          });
          
          if (retryResponse.ok) {
            return await retryResponse.json();
          }
        } catch {
          logout();
        }
      }
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
};

/**
 * Logout user
 */
export const logout = async () => {
  const token = localStorage.getItem('access_token');
  
  // Call logout API (optional, for token blacklist)
  if (token) {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Logout API call failed:', error);
    }
  }
  
  // Clear local storage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token_expires_at');
  localStorage.removeItem('user_email');
  localStorage.removeItem('user_password');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('access_token');
  const expiresAt = localStorage.getItem('token_expires_at');
  
  if (!token || !expiresAt) {
    return false;
  }
  
  // Check if token is expired
  return Date.now() < parseInt(expiresAt);
};

/**
 * Get authorization headers for API calls
 */
export const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return {};
  }
  
  return {
    'Authorization': `Bearer ${token}`,
  };
};

/**
 * Make authenticated API call
 */
export const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const headers = {
    ...options.headers,
    ...getAuthHeaders(),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 401 (unauthorized)
  if (response.status === 401) {
    try {
      await refreshToken();
      // Retry with new token
      const newHeaders = {
        ...options.headers,
        ...getAuthHeaders(),
      };
      return await fetch(url, {
        ...options,
        headers: newHeaders,
      });
    } catch (error) {
      throw new Error('Authentication failed');
    }
  }

  return response;
};
