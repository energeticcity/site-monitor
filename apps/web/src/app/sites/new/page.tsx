'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createSite } from '@/lib/api';

export default function NewSite() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    url: '',
    profile_key: '',
    interval_minutes: 60,
    keywords: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Parse keywords
      const keywordsArray = formData.keywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0);

      await createSite({
        url: formData.url,
        profile_key: formData.profile_key || null,
        interval_minutes: formData.interval_minutes,
        keywords: keywordsArray.length > 0 ? keywordsArray : null,
      });

      // Redirect to dashboard on success
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create site');
      console.error('Error creating site:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <a
            href="/dashboard"
            className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
          >
            ← Back to Dashboard
          </a>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
          <h1 className="text-3xl font-bold mb-6">Add New Site</h1>

          {error && (
            <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-600 dark:text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* URL */}
            <div>
              <label
                htmlFor="url"
                className="block text-sm font-medium mb-2"
              >
                Website URL *
              </label>
              <input
                id="url"
                type="url"
                value={formData.url}
                onChange={(e) =>
                  setFormData({ ...formData, url: e.target.value })
                }
                placeholder="https://example.com"
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                The website you want to monitor for new content
              </p>
            </div>

            {/* Check Interval */}
            <div>
              <label
                htmlFor="interval"
                className="block text-sm font-medium mb-2"
              >
                Check Interval (minutes) *
              </label>
              <input
                id="interval"
                type="number"
                min="1"
                value={formData.interval_minutes}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    interval_minutes: parseInt(e.target.value) || 60,
                  })
                }
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                How often to check for new content (default: 60 minutes)
              </p>
            </div>

            {/* Keywords */}
            <div>
              <label
                htmlFor="keywords"
                className="block text-sm font-medium mb-2"
              >
                Keywords (optional)
              </label>
              <input
                id="keywords"
                type="text"
                value={formData.keywords}
                onChange={(e) =>
                  setFormData({ ...formData, keywords: e.target.value })
                }
                placeholder="keyword1, keyword2, keyword3"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Comma-separated keywords to filter content (optional)
              </p>
            </div>

            {/* Profile Key */}
            <div>
              <label
                htmlFor="profile_key"
                className="block text-sm font-medium mb-2"
              >
                Profile Key (optional)
              </label>
              <input
                id="profile_key"
                type="text"
                value={formData.profile_key}
                onChange={(e) =>
                  setFormData({ ...formData, profile_key: e.target.value })
                }
                placeholder="e.g., rcmp_fsj"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Special profile for custom discovery methods (advanced)
              </p>
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? 'Adding Site...' : 'Add Site'}
              </button>
              <button
                type="button"
                onClick={() => router.push('/dashboard')}
                disabled={loading}
                className="px-6 py-3 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
}

