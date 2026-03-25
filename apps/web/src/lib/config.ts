/**
 * Centralized app configuration.
 * All environment-dependent values should be accessed through this module.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
