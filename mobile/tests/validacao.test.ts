// Testes unitários da validação de relatos (executar: npm test — usa o test runner nativo do Node 22+).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { validarRelato } from '../src/lib/validacao.ts';

const base = {
  tipo: 'RuaAlagada' as const,
  descricao: 'Rua alagada perto da escola',
  bairro: 'Jardim Pantanal',
  latitude: -23.49,
  longitude: -46.43,
  severidade: 3,
  apelido: null,
};

test('relato válido não gera erros', () => {
  assert.deepEqual(validarRelato(base), []);
});

test('descrição curta é rejeitada', () => {
  assert.equal(validarRelato({ ...base, descricao: 'abc' }).length, 1);
});

test('severidade fora de 1..5 é rejeitada', () => {
  assert.ok(validarRelato({ ...base, severidade: 6 }).some((e) => e.includes('gravidade')));
  assert.ok(validarRelato({ ...base, severidade: 0 }).some((e) => e.includes('gravidade')));
});

test('CPF na descrição é bloqueado (LGPD)', () => {
  assert.ok(validarRelato({ ...base, descricao: 'Meu CPF é 123.456.789-09, rua alagada' }).some((e) => e.includes('CPF')));
});

test('telefone e e-mail no apelido são bloqueados', () => {
  assert.equal(validarRelato({ ...base, apelido: '(11) 98765-4321' }).length, 1);
  assert.equal(validarRelato({ ...base, apelido: 'joao@email.com' }).length, 1);
});
