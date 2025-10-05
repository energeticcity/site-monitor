'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  getSite,
  getSiteItems,
  getSiteRuns,
  triggerSiteRun,
  Site,
  Item,
  Run,
} from '@/lib/api';

export default function SiteDetail() {
  const params = useParams();
  const siteId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [site, setSite] = useState<Site | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [triggering, setTriggering] = useState(false);
  const [triggerSuccess, setTriggerSuccess] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        // Fetch site, items, and runs in parallel
        const [siteData, itemsData, runsData] = await Promise.all([
          getSite(siteId),
          getSiteItems(siteId, undefined, 50),
          getSiteRuns(siteId, 1, 20),
        ]);

        setSite(siteData);
        setItems(itemsData.items);
        setRuns(runsData.runs);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load site');
        console.error('Site detail error:', err);
      } finally {
        setLoading(false);
      }
    }

    if (siteId) {
      fetchData();
    }
  }, [siteId]);

  const handleTriggerRun = async () => {
    if (!site) return;

    try {
      setTriggering(true);
      setTriggerSuccess(false);
      await triggerSiteRun(siteId);
      setTriggerSuccess(true);

      // Refresh runs after a short delay
      setTimeout(async () => {
        const runsData = await getSiteRuns(siteId, 1, 20);
        setRuns(runsData.runs);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger run');
      console.error('Trigger run error:', err);
    } finally {
      setTriggering(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-600 dark:text-gray-400">Loading site details...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <a
              href="/dashboard"
              className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
            >
              ← Back to Dashboard
            </a>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">
              Error
            </h2>
            <p className="text-red-600 dark:text-red-300">{error}</p>
          </div>
        </div>
      </main>
    );
  }

  if (!site) {
    return null;
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <a
            href="/dashboard"
            className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
          >
            ← Back to Dashboard
          </a>
        </div>

        {/* Site Info */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold">{site.url}</h1>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    site.enabled
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}
                >
                  {site.enabled ? 'Active' : 'Disabled'}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 text-sm">
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Check Interval:</span>
                  <span className="ml-2 font-medium">{site.interval_minutes} minutes</span>
                </div>
                {site.last_run_at && (
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Last Checked:</span>
                    <span className="ml-2 font-medium">
                      {new Date(site.last_run_at).toLocaleString()}
                    </span>
                  </div>
                )}
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Items Found:</span>
                  <span className="ml-2 font-medium">{items.length}</span>
                </div>
              </div>
              {site.keywords && site.keywords.length > 0 && (
                <div className="mt-4">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Keywords:</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {site.keywords.map((keyword, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <button
              onClick={handleTriggerRun}
              disabled={triggering}
              className="ml-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {triggering ? 'Running...' : 'Check Now'}
            </button>
          </div>

          {triggerSuccess && (
            <div className="mt-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
              <p className="text-green-700 dark:text-green-300 text-sm">
                ✓ Check started successfully! Results will appear below shortly.
              </p>
            </div>
          )}
        </div>

        {/* Recent Items */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">
            Discovered Items ({items.length})
          </h2>
          {items.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                No items discovered yet.
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                Click &quot;Check Now&quot; to manually trigger a discovery run.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {items.map((item) => {
                const isNew =
                  new Date(item.discovered_at).getTime() >
                  Date.now() - 24 * 60 * 60 * 1000;

                return (
                  <div
                    key={item.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {isNew && (
                            <span className="px-2 py-0.5 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 text-xs font-medium rounded">
                              NEW
                            </span>
                          )}
                          {item.source && (
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs font-medium rounded">
                              {item.source}
                            </span>
                          )}
                        </div>
                        <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                          {item.title || 'Untitled'}
                        </h3>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 dark:text-blue-400 hover:underline block truncate"
                        >
                          {item.url}
                        </a>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                          Discovered {new Date(item.discovered_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Run History */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Run History ({runs.length})</h2>
          {runs.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400">No runs yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="border-b border-gray-200 dark:border-gray-700">
                  <tr>
                    <th className="text-left py-3 px-4 font-semibold text-sm">Status</th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">Method</th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">
                      Pages Scanned
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">Duration</th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">Started</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((run) => (
                    <tr
                      key={run.id}
                      className="border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                    >
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            run.status === 'success'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : run.status === 'error'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          }`}
                        >
                          {run.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {run.method || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {run.pages_scanned}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {run.duration_ms ? `${run.duration_ms}ms` : 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400 text-sm">
                        {new Date(run.started_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

