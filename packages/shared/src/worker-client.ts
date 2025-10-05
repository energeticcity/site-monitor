/**
 * Cloudflare Worker client for site discovery.
 */

import { z } from 'zod';

/**
 * Worker response schema.
 */
export const WorkerResponseSchema = z.object({
  source: z.string(),
  links: z.array(z.string()).optional(),
  feeds: z.array(z.string()).optional(),
  count: z.number(),
  diagnostics: z.record(z.any()).optional(),
});

export type WorkerResponse = z.infer<typeof WorkerResponseSchema>;

/**
 * Discover request schema.
 */
export const DiscoverRequestSchema = z.object({
  url: z.string().url(),
});

export type DiscoverRequest = z.infer<typeof DiscoverRequestSchema>;

/**
 * RCMP FSJ request schema.
 */
export const RCMPFSJRequestSchema = z.object({
  monthsBack: z.number().optional(),
});

export type RCMPFSJRequest = z.infer<typeof RCMPFSJRequestSchema>;

/**
 * Worker client error.
 */
export class WorkerClientError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: unknown
  ) {
    super(message);
    this.name = 'WorkerClientError';
  }
}

/**
 * Worker client options.
 */
export interface WorkerClientOptions {
  baseUrl: string;
  timeout?: number;
}

/**
 * Cloudflare Worker client.
 */
export class WorkerClient {
  private baseUrl: string;
  private timeout: number;

  constructor(options: WorkerClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = options.timeout || 30000; // 30s default
  }

  /**
   * Discover new posts on a website.
   */
  async discover(url: string): Promise<WorkerResponse> {
    // Validate input
    const request = DiscoverRequestSchema.parse({ url });

    const response = await this.post('/discover', { url: request.url });
    return WorkerResponseSchema.parse(response);
  }

  /**
   * Get RCMP FSJ posts.
   */
  async rcmpFSJ(monthsBack?: number): Promise<WorkerResponse> {
    // Validate input
    const request = RCMPFSJRequestSchema.parse({ monthsBack });

    const response = await this.post('/profiles/rcmp-fsj', {
      monthsBack: request.monthsBack,
    });
    return WorkerResponseSchema.parse(response);
  }

  /**
   * Make a POST request to the Worker.
   */
  private async post(path: string, body?: unknown): Promise<unknown> {
    const url = `${this.baseUrl}${path}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const text = await response.text();
        throw new WorkerClientError(
          `Worker request failed: ${response.statusText}`,
          response.status,
          text
        );
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof WorkerClientError) {
        throw error;
      }

      if ((error as Error).name === 'AbortError') {
        throw new WorkerClientError('Worker request timed out');
      }

      throw new WorkerClientError(
        `Worker request failed: ${(error as Error).message}`
      );
    }
  }
}

/**
 * Create a Worker client instance.
 */
export function createWorkerClient(baseUrl: string): WorkerClient {
  return new WorkerClient({ baseUrl });
}

