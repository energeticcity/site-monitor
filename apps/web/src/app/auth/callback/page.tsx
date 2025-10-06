'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setError('No token provided');
      return;
    }

    // Exchange magic link token for JWT session
    const exchangeToken = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/v1/auth/magic-link/callback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ token }),
        });

        if (response.ok) {
          const data = await response.json();
          
          // Store the JWT token in localStorage for cross-domain access
          // (Cookie won't work because Railway and Vercel are different domains)
          if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
          }
          
          // Successfully authenticated, redirect to dashboard
          router.push('/dashboard');
        } else {
          const data = await response.json();
          setError(data.detail || 'Invalid or expired magic link');
        }
      } catch (err) {
        console.error('Error exchanging token:', err);
        setError('Failed to authenticate. Please try again.');
      }
    };

    exchangeToken();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
              Authentication Error
            </h2>
            <p className="mt-2 text-center text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
            <div className="mt-4 text-center">
              <a
                href="/auth/signin"
                className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
              >
                Request a new magic link
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Signing you in...
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Please wait while we verify your magic link.
          </p>
          <div className="mt-8 flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AuthCallback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  );
}
