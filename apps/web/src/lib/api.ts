/**
 * API Client for SiteWatcher
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DashboardStats {
  tenant_id: string;
  tenant_name: string;
  total_sites: number;
  active_sites: number;
  total_items: number;
  items_this_week: number;
  total_runs: number;
  successful_runs_today: number;
  failed_runs_today: number;
}

export interface TeamMember {
  user_id: string;
  name: string | null;
  email: string;
  role: string;
  joined_at: string;
}

export interface TeamListResponse {
  team_members: TeamMember[];
  total: number;
}

export interface Site {
  id: string;
  tenant_id: string;
  url: string;
  profile_key: string | null;
  keywords: string[] | null;
  enabled: boolean;
  interval_minutes: number;
  last_run_at: string | null;
  created_at: string;
}

export interface SiteListResponse {
  sites: Site[];
  total: number;
}

export interface Item {
  id: string;
  site_id: string;
  url: string;
  canonical_url: string | null;
  title: string | null;
  published_at: string | null;
  discovered_at: string;
  source: string | null;
  meta_json: any;
}

export interface ItemListResponse {
  items: Item[];
  next_cursor: string | null;
}

export interface Run {
  id: string;
  site_id: string;
  status: string;
  method: string | null;
  pages_scanned: number;
  duration_ms: number | null;
  diagnostics_json: any;
  started_at: string;
  finished_at: string | null;
}

export interface RunListResponse {
  runs: Run[];
  total: number;
}

/**
 * Fetch dashboard statistics for a tenant
 */
export async function getDashboardStats(tenantId: string): Promise<DashboardStats> {
  const response = await fetch(
    `${API_BASE_URL}/v1/dashboard/stats?tenant_id=${tenantId}`,
    {
      credentials: 'include',
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard stats: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch team members for a tenant
 */
export async function getTeamMembers(tenantId: string): Promise<TeamListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/v1/dashboard/team?tenant_id=${tenantId}`,
    {
      credentials: 'include',
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch team members: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch sites for the user's tenant
 */
export async function getSites(page: number = 1, limit: number = 100): Promise<SiteListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/v1/sites?page=${page}&limit=${limit}`,
    {
      credentials: 'include',
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch sites: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get authorization headers with JWT from localStorage
 */
function getAuthHeaders(): HeadersInit {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
}

/**
 * Get current user info
 */
export async function getCurrentUser(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/v1/auth/me`, {
    credentials: 'include',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch current user: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch recent items discovered across all sites for a tenant
 */
export async function getRecentItems(tenantId: string, limit: number = 20): Promise<ItemListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/v1/dashboard/recent-items?tenant_id=${tenantId}&limit=${limit}`,
    {
      credentials: 'include',
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch recent items: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch recent runs across all sites for a tenant
 */
export async function getRecentRuns(tenantId: string, limit: number = 10): Promise<RunListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/v1/dashboard/recent-runs?tenant_id=${tenantId}&limit=${limit}`,
    {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch recent runs: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Create a new site
 */
export async function createSite(site: {
  url: string;
  profile_key?: string | null;
  interval_minutes?: number;
  keywords?: string[] | null;
}): Promise<Site> {
  const response = await fetch(`${API_BASE_URL}/v1/sites`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(site),
  });

  if (!response.ok) {
    throw new Error(`Failed to create site: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get a specific site by ID
 */
export async function getSite(siteId: string): Promise<Site> {
  const response = await fetch(`${API_BASE_URL}/v1/sites/${siteId}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch site: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get items for a specific site
 */
export async function getSiteItems(siteId: string, cursor?: string, limit: number = 20): Promise<ItemListResponse> {
  const url = new URL(`${API_BASE_URL}/v1/sites/${siteId}/items`);
  if (cursor) url.searchParams.set('cursor', cursor);
  url.searchParams.set('limit', limit.toString());

  const response = await fetch(url.toString(), {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch site items: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get runs for a specific site
 */
export async function getSiteRuns(siteId: string, page: number = 1, limit: number = 10): Promise<RunListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/v1/sites/${siteId}/runs?page=${page}&limit=${limit}`,
    {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch site runs: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Trigger a manual run for a site
 */
export async function triggerSiteRun(siteId: string): Promise<{ run_id: string; status: string }> {
  const response = await fetch(`${API_BASE_URL}/v1/sites/${siteId}/run`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to trigger site run: ${response.statusText}`);
  }

  return response.json();
}

