import * as SQLite from 'expo-sqlite';
import type { NovaOcorrencia, RelatoLocal, StatusSync } from '../lib/types';

/**
 * Banco local do aparelho (SQLite via expo-sqlite).
 * - relatos: ocorrências criadas pelo cidadão (funciona offline; sincroniza depois)
 * - preferencias: bairro escolhido etc.
 * - cache: última resposta da API, para uso sem internet
 */
let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;

function db(): Promise<SQLite.SQLiteDatabase> {
  if (!dbPromise) {
    dbPromise = (async () => {
      const conn = await SQLite.openDatabaseAsync('aquaguard.db');
      await conn.execAsync(`
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS relatos (
          id_local     INTEGER PRIMARY KEY AUTOINCREMENT,
          tipo         TEXT    NOT NULL,
          descricao    TEXT    NOT NULL,
          bairro       TEXT    NOT NULL,
          latitude     REAL    NOT NULL,
          longitude    REAL    NOT NULL,
          severidade   INTEGER NOT NULL CHECK (severidade BETWEEN 1 AND 5),
          apelido      TEXT,
          criado_em    TEXT    NOT NULL,
          status_sync  TEXT    NOT NULL DEFAULT 'pendente',
          id_remoto    INTEGER
        );
        CREATE TABLE IF NOT EXISTS preferencias (chave TEXT PRIMARY KEY, valor TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS cache (chave TEXT PRIMARY KEY, json TEXT NOT NULL, atualizado_em TEXT NOT NULL);
      `);
      return conn;
    })();
  }
  return dbPromise;
}

interface LinhaRelato {
  id_local: number;
  tipo: string;
  descricao: string;
  bairro: string;
  latitude: number;
  longitude: number;
  severidade: number;
  apelido: string | null;
  criado_em: string;
  status_sync: string;
  id_remoto: number | null;
}

const paraRelato = (r: LinhaRelato): RelatoLocal => ({
  idLocal: r.id_local,
  tipo: r.tipo as RelatoLocal['tipo'],
  descricao: r.descricao,
  bairro: r.bairro,
  latitude: r.latitude,
  longitude: r.longitude,
  severidade: r.severidade,
  apelido: r.apelido,
  criadoEm: r.criado_em,
  statusSync: r.status_sync as StatusSync,
  idRemoto: r.id_remoto,
});

export const banco = {
  async salvarRelato(o: NovaOcorrencia): Promise<number> {
    const conn = await db();
    const r = await conn.runAsync(
      `INSERT INTO relatos (tipo, descricao, bairro, latitude, longitude, severidade, apelido, criado_em)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      o.tipo, o.descricao, o.bairro, o.latitude, o.longitude, o.severidade, o.apelido ?? null, new Date().toISOString(),
    );
    return r.lastInsertRowId;
  },

  async listarRelatos(): Promise<RelatoLocal[]> {
    const conn = await db();
    const linhas = await conn.getAllAsync<LinhaRelato>('SELECT * FROM relatos ORDER BY criado_em DESC');
    return linhas.map(paraRelato);
  },

  async atualizarSync(idLocal: number, status: StatusSync, idRemoto: number | null = null): Promise<void> {
    const conn = await db();
    await conn.runAsync('UPDATE relatos SET status_sync = ?, id_remoto = COALESCE(?, id_remoto) WHERE id_local = ?',
      status, idRemoto, idLocal);
  },

  async excluirRelato(idLocal: number): Promise<void> {
    const conn = await db();
    await conn.runAsync('DELETE FROM relatos WHERE id_local = ?', idLocal);
  },

  async obterPreferencia(chave: string): Promise<string | null> {
    const conn = await db();
    const r = await conn.getFirstAsync<{ valor: string }>('SELECT valor FROM preferencias WHERE chave = ?', chave);
    return r?.valor ?? null;
  },

  async salvarPreferencia(chave: string, valor: string): Promise<void> {
    const conn = await db();
    await conn.runAsync('INSERT OR REPLACE INTO preferencias (chave, valor) VALUES (?, ?)', chave, valor);
  },

  async salvarCache<T>(chave: string, dados: T): Promise<void> {
    const conn = await db();
    await conn.runAsync('INSERT OR REPLACE INTO cache (chave, json, atualizado_em) VALUES (?, ?, ?)',
      chave, JSON.stringify(dados), new Date().toISOString());
  },

  async lerCache<T>(chave: string): Promise<{ dados: T; atualizadoEm: string } | null> {
    const conn = await db();
    const r = await conn.getFirstAsync<{ json: string; atualizado_em: string }>(
      'SELECT json, atualizado_em FROM cache WHERE chave = ?', chave);
    return r ? { dados: JSON.parse(r.json) as T, atualizadoEm: r.atualizado_em } : null;
  },
};

export type Banco = typeof banco;
