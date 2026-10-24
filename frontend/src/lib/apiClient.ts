// Centralised fetch for the Code Optimizer backend.
// Backend defaults to http://localhost:8008; override with PUBLIC_API_BASE.

export const BASE: string =
  (import.meta.env.PUBLIC_API_BASE as string | undefined) ??
  'http://localhost:8008';

async function handle(res: Response): Promise<any> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = (data as { detail?: string }).detail ?? JSON.stringify(data);
    } catch {
      // keep statusText
    }
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json();
}

export async function apiGet(path: string): Promise<any> {
  const res = await fetch(`${BASE}${path}`);
  return handle(res);
}

export async function apiPost(path: string, body: unknown): Promise<any> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handle(res);
}
