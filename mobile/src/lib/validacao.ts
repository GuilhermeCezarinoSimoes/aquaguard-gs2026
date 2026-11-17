import type { NovaOcorrencia } from './types';

// Padrões simples de dados pessoais: o relato é público e não deve expor o cidadão (LGPD).
const CPF = /\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b/;
const TELEFONE = /\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b/;
const EMAIL = /[\w.+-]+@[\w-]+\.[\w.]+/;

/** Validações de entrada (as mesmas regras de negócio da API + proteção de dados pessoais). */
export function validarRelato(o: NovaOcorrencia): string[] {
  const erros: string[] = [];
  const d = o.descricao.trim();
  if (d.length < 5) erros.push('Descreva o problema com pelo menos 5 caracteres.');
  if (d.length > 500) erros.push('A descrição pode ter no máximo 500 caracteres.');
  if (o.severidade < 1 || o.severidade > 5) erros.push('Escolha a gravidade de 1 a 5.');
  if (!o.bairro) erros.push('Escolha o seu bairro.');
  const texto = `${d} ${o.apelido ?? ''}`;
  if (CPF.test(texto) || TELEFONE.test(texto) || EMAIL.test(texto))
    erros.push('Por segurança, não informe CPF, telefone ou e-mail no relato.');
  return erros;
}
