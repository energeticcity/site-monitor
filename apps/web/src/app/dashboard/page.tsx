'use client';

import { useEffect, useState } from 'react';
import {
  getDashboardStats,
  getTeamMembers,
  getSites,
  getCurrentUser,
  getRecentItems,
  DashboardStats,
  TeamMember,
  Site,
  Item,
} from '@/lib/api';

interface UserInfo {
  id: string;
  email: string;
  name: string | null;
  tenants: Array<{
    tenant_id: string;
    tenant_name: string;
    role: string;
  }>;
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [recentItems, setRecentItems] = useState<Item[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        // First, get current user to determine tenant
        const userData = await getCurrentUser();
        setUser(userData);

        // If user has no tenants, show a message
        if (!userData.tenants || userData.tenants.length === 0) {
          setError('You are not part of any team. Please contact an administrator.');
          setLoading(false);
          return;
        }

        // Use the first tenant (in a real app, allow user to select)
        const tenantId = userData.tenants[0].tenant_id;

        // Fetch dashboard stats, team members, sites, and recent items in parallel
        const [statsData, teamData, sitesData, itemsData] = await Promise.all([
          getDashboardStats(tenantId),
          getTeamMembers(tenantId),
          getSites(1, 100),
          getRecentItems(tenantId, 10),
        ]);

        setStats(statsData);
        setTeamMembers(teamData.team_members);
        setSites(sitesData.sites);
        setRecentItems(itemsData.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
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

  if (!stats || !user) {
    return null;
  }

  const roleColors: Record<string, string> = {
    super_admin: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    admin: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    member: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">{stats.tenant_name}</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Team Dashboard - {user.tenants[0]?.role.replace('_', ' ')}
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-2">Sites</h2>
            <p className="text-3xl font-bold text-blue-600">
              {stats.active_sites}/{stats.total_sites}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              Active monitoring sites
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-2">Items</h2>
            <p className="text-3xl font-bold text-green-600">{stats.items_this_week}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              Discovered this week
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              Total: {stats.total_items}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-2">Runs</h2>
            <p className="text-3xl font-bold text-purple-600">
              {stats.successful_runs_today}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              Successful runs today
            </p>
            {stats.failed_runs_today > 0 && (
              <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                {stats.failed_runs_today} failed
              </p>
            )}
          </div>
        </div>

        {/* Recent Discoveries */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Recent Discoveries</h2>
          {recentItems.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400">
                No items discovered yet. Add a site to start monitoring.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentItems.map((item) => {
                const isNew =
                  new Date(item.discovered_at).getTime() >
                  Date.now() - 24 * 60 * 60 * 1000;
                const site = sites.find((s) => s.id === item.site_id);
                
                return (
                  <div
                    key={item.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition"
                  >
                    <div className="flex items-start justify-between gap-4">
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
                        <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                          {item.title || 'Untitled'}
                        </h3>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 dark:text-blue-400 hover:underline truncate block"
                        >
                          {item.url}
                        </a>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <span>
                            From: {site?.url || 'Unknown site'}
                          </span>
                          <span>
                            {new Date(item.discovered_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <a
                        href={`/sites/${item.site_id}`}
                        className="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition whitespace-nowrap"
                      >
                        View Site
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Team Members */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Team Members ({teamMembers.length})</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="text-left py-3 px-4 font-semibold text-sm">Name</th>
                  <th className="text-left py-3 px-4 font-semibold text-sm">Email</th>
                  <th className="text-left py-3 px-4 font-semibold text-sm">Role</th>
                  <th className="text-left py-3 px-4 font-semibold text-sm">Joined</th>
                </tr>
              </thead>
              <tbody>
                {teamMembers.map((member) => (
                  <tr
                    key={member.user_id}
                    className="border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                  >
                    <td className="py-3 px-4">
                      {member.name || 'N/A'}
                      {member.user_id === user.id && (
                        <span className="ml-2 text-xs text-gray-500">(You)</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                      {member.email}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          roleColors[member.role] || roleColors.member
                        }`}
                      >
                        {member.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600 dark:text-gray-400 text-sm">
                      {new Date(member.joined_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sites List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Monitored Sites ({sites.length})</h2>
            <a
              href="/sites/new"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
            >
              Add Site
            </a>
          </div>
          {sites.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                No sites are being monitored yet.
              </p>
              <a
                href="/sites/new"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition inline-block"
              >
                Add Your First Site
              </a>
            </div>
          ) : (
            <div className="space-y-4">
              {sites.map((site) => (
                <div
                  key={site.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-500 dark:hover:border-blue-400 transition"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold">{site.url}</h3>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            site.enabled
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                          }`}
                        >
                          {site.enabled ? 'Active' : 'Disabled'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <p>Check interval: {site.interval_minutes} minutes</p>
                        {site.last_run_at && (
                          <p>
                            Last checked:{' '}
                            {new Date(site.last_run_at).toLocaleString()}
                          </p>
                        )}
                        {site.keywords && site.keywords.length > 0 && (
                          <p>
                            Keywords:{' '}
                            {site.keywords.map((kw, idx) => (
                              <span
                                key={idx}
                                className="inline-block bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded mr-1 text-xs"
                              >
                                {kw}
                              </span>
                            ))}
                          </p>
                        )}
                      </div>
                    </div>
                    <a
                      href={`/sites/${site.id}`}
                      className="ml-4 px-4 py-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition text-sm"
                    >
                      View Details
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

