import { banco } from '../db/database';
import { api } from './api';
import { ALERTAS_DEMO, PAINEL_DEMO, SENSORES_DEMO, leiturasDemo } from './mock';
import type { Alerta, Leitura, NovaOcorrencia, OrigemDados, Painel, Sensor } from './types';

export interface Resultado<T> {
  dados: T;
  origem: OrigemDados;
  atualizadoEm: string;
}

/** Busca na API; se falhar, usa o último cache local; se não houver, usa dados de demonstração. */
async function comFallback<T>(chave: string, buscar: () => Promise<T>, demo: () => T): Promise<Resultado<T>> {
  try {
    const dados = await buscar();
    await banco.salvarCache(chave, dados);
    return { dados, origem: 'api', atualizadoEm: new Date().toISOString() };
  } catch {
    const cache = await banco.lerCache<T>(chave);
    if (cache) return { dados: cache.dados, origem: 'cache', atualizadoEm: cache.atualizadoEm };
    return { dados: demo(), origem: 'demo', atualizadoEm: new Date().toISOString() };
  }
}

export const servicos = {
  painel: () => comFallback<Painel>('painel', api.painel, () => PAINEL_DEMO),
  sensores: () => comFallback<Sensor[]>('sensores', api.sensores, () => SENSORES_DEMO),
  alertas: (bairro?: string) =>
    comFallback<Alerta[]>(`alertas:${bairro ?? '*'}`, () => api.alertas(bairro),
      () => ALERTAS_DEMO.filter((a) => !bairro || a.bairro === bairro)),
  leituras: (id: number) => comFallback<Leitura[]>(`leituras:${id}`, () => api.leituras(id), () => leiturasDemo(id)),

  /** Salva SEMPRE no aparelho primeiro (offline-first) e tenta enviar em seguida. */
  async registrarRelato(o: NovaOcorrencia): Promise<{ enviado: boolean }> {
    const idLocal = await banco.salvarRelato(o);
    return { enviado: await this.enviarRelato(idLocal, o) };
  },

  async enviarRelato(idLocal: number, o: NovaOcorrencia): Promise<boolean> {
    try {
      // Envia somente os campos do contrato da API (nada de ids/estado locais).
      const { tipo, descricao, bairro, latitude, longitude, severidade, apelido } = o;
      const criado = await api.criarOcorrencia({ tipo, descricao, bairro, latitude, longitude, severidade, apelido: apelido ?? null });
      await banco.atualizarSync(idLocal, 'enviado', criado.id);
      return true;
    } catch {
      await banco.atualizarSync(idLocal, 'pendente');
      return false;
    }
  },

  async sincronizarPendentes(): Promise<{ enviados: number; pendentes: number }> {
    const pendentes = (await banco.listarRelatos()).filter((r) => r.statusSync !== 'enviado');
    let enviados = 0;
    for (const r of pendentes) if (await this.enviarRelato(r.idLocal, r)) enviados++;
    return { enviados, pendentes: pendentes.length - enviados };
  },
};
