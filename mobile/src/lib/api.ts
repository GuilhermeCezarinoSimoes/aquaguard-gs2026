import type { Alerta, Leitura, NovaOcorrencia, Painel, Sensor } from './types';

/**
 * URL da API AquaGuard (backend C#). Configure em .env:
 *   EXPO_PUBLIC_API_URL=http://192.168.0.10:5080   (IP do computador na mesma rede do celular)
 * Emulador Android: http://10.0.2.2:5080 · Web/iOS simulator: http://localhost:5080
 */
export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:5080').replace(/\/$/, '');

const TIMEOUT_MS = 6000;

export class ApiError extends Error {
  constructor(message: string, public readonly status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function requisitar<T>(caminho: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const resp = await fetch(`${API_URL}${caminho}`, {
      ...init,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', Accept: 'application/json', ...(init?.headers ?? {}) },
    });
    if (!resp.ok) {
      let detalhe = `Erro ${resp.status}`;
      try {
        const corpo = (await resp.json()) as { detail?: string; title?: string };
        detalhe = corpo.detail ?? corpo.title ?? detalhe;
      } catch {
        /* corpo não-JSON */
      }
      throw new ApiError(detalhe, resp.status);
    }
    return (await resp.json()) as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    throw new ApiError('Sem conexão com o servidor AquaGuard.');
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  painel: () => requisitar<Painel>('/api/painel'),
  sensores: () => requisitar<Sensor[]>('/api/sensores?ativo=true'),
  sensor: (id: number) => requisitar<Sensor>(`/api/sensores/${id}`),
  leituras: (id: number, horas = 24) => requisitar<Leitura[]>(`/api/sensores/${id}/leituras?horas=${horas}&limite=48`),
  alertas: (bairro?: string) =>
    requisitar<Alerta[]>(`/api/alertas${bairro ? `?bairro=${encodeURIComponent(bairro)}` : ''}`),
  criarOcorrencia: (o: NovaOcorrencia) =>
    requisitar<{ id: number }>('/api/ocorrencias', { method: 'POST', body: JSON.stringify(o) }),
};
