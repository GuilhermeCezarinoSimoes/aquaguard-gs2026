import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { banco } from '../db/database';
import { BAIRROS } from './constantes';

interface BairroCtx {
  bairro: string;
  definirBairro: (nome: string) => Promise<void>;
  pronto: boolean;
}

const Contexto = createContext<BairroCtx | null>(null);

/** Guarda o bairro do morador no banco local (persistente entre aberturas do app). */
export function BairroProvider({ children }: { children: ReactNode }) {
  const [bairro, setBairro] = useState(BAIRROS[0].nome);
  const [pronto, setPronto] = useState(false);

  useEffect(() => {
    banco.obterPreferencia('bairro')
      .then((v) => { if (v) setBairro(v); })
      .finally(() => setPronto(true));
  }, []);

  const definirBairro = useCallback(async (nome: string) => {
    setBairro(nome);
    await banco.salvarPreferencia('bairro', nome);
  }, []);

  const valor = useMemo(() => ({ bairro, definirBairro, pronto }), [bairro, definirBairro, pronto]);
  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useBairro(): BairroCtx {
  const ctx = useContext(Contexto);
  if (!ctx) throw new Error('useBairro deve ser usado dentro de BairroProvider');
  return ctx;
}
