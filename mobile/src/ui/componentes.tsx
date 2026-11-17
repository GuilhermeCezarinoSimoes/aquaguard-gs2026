import { Ionicons } from '@expo/vector-icons';
import type { ComponentProps, ReactNode } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View, type ViewStyle } from 'react-native';
import { ICONE_RISCO, ROTULO_RISCO } from '../lib/constantes';
import type { NivelRisco, OrigemDados } from '../lib/types';
import { COR_RISCO, espaco, raio, tipografia, useCores } from './tema';

type NomeIcone = ComponentProps<typeof Ionicons>['name'];

export function Cartao({ children, style }: { children: ReactNode; style?: ViewStyle }) {
  const c = useCores();
  return <View style={[estilos.cartao, { backgroundColor: c.superficie, borderColor: c.borda }, style]}>{children}</View>;
}

/** Selo de risco: cor + ícone + texto (nunca só cor — acessível a daltônicos). */
export function SeloRisco({ risco, grande = false }: { risco: NivelRisco; grande?: boolean }) {
  return (
    <View
      style={[estilos.selo, { backgroundColor: COR_RISCO[risco] }, grande && estilos.seloGrande]}
      accessible
      accessibilityRole="text"
      accessibilityLabel={`Nível de risco: ${ROTULO_RISCO[risco]}`}
    >
      <Ionicons name={ICONE_RISCO[risco] as NomeIcone} size={grande ? 18 : 14} color="#fff" />
      <Text style={[estilos.seloTexto, grande && { fontSize: 16 }]}>{ROTULO_RISCO[risco]}</Text>
    </View>
  );
}

export function Botao({
  titulo, onPress, icone, variante = 'primario', carregando = false, desabilitado = false, dica,
}: {
  titulo: string; onPress: () => void; icone?: NomeIcone; variante?: 'primario' | 'secundario';
  carregando?: boolean; desabilitado?: boolean; dica?: string;
}) {
  const c = useCores();
  const primario = variante === 'primario';
  const inativo = desabilitado || carregando;
  return (
    <Pressable
      onPress={onPress}
      disabled={inativo}
      accessibilityRole="button"
      accessibilityLabel={titulo}
      accessibilityHint={dica}
      accessibilityState={{ disabled: inativo, busy: carregando }}
      style={({ pressed }) => [
        estilos.botao,
        { backgroundColor: primario ? c.marcaForte : c.marcaSuave, opacity: inativo ? 0.5 : pressed ? 0.85 : 1,
          transform: [{ scale: pressed ? 0.98 : 1 }] },
      ]}
    >
      {carregando ? (
        <ActivityIndicator color={primario ? '#fff' : c.marca} />
      ) : (
        <>
          {icone && <Ionicons name={icone} size={20} color={primario ? '#fff' : c.marca} />}
          <Text style={[estilos.botaoTexto, { color: primario ? '#fff' : c.marca }]}>{titulo}</Text>
        </>
      )}
    </Pressable>
  );
}

export function Carregando({ texto = 'Carregando…' }: { texto?: string }) {
  const c = useCores();
  return (
    <View style={estilos.centro} accessibilityLiveRegion="polite" accessibilityLabel={texto}>
      <ActivityIndicator size="large" color={c.marca} />
      <Text style={[tipografia.legenda, { color: c.textoSecundario, marginTop: espaco.sm }]}>{texto}</Text>
    </View>
  );
}

export function EstadoVazio({ icone, titulo, texto }: { icone: NomeIcone; titulo: string; texto: string }) {
  const c = useCores();
  return (
    <View style={[estilos.centro, { paddingVertical: espaco.xl }]} accessible accessibilityLabel={`${titulo}. ${texto}`}>
      <Ionicons name={icone} size={44} color={c.textoSecundario} />
      <Text style={[tipografia.subtitulo, { color: c.texto, marginTop: espaco.sm }]}>{titulo}</Text>
      <Text style={[tipografia.legenda, { color: c.textoSecundario, textAlign: 'center', marginTop: espaco.xs }]}>{texto}</Text>
    </View>
  );
}

/** Aviso quando os dados não vêm da API ao vivo. */
export function AvisoOrigem({ origem, atualizadoEm }: { origem: OrigemDados; atualizadoEm: string }) {
  if (origem === 'api') return null;
  const texto = origem === 'cache'
    ? `Sem conexão. Mostrando dados salvos de ${new Date(atualizadoEm).toLocaleString('pt-BR')}.`
    : 'Sem conexão com o servidor. Mostrando dados de demonstração.';
  return (
    <View style={estilos.aviso} accessibilityRole="alert" accessibilityLiveRegion="polite">
      <Ionicons name="cloud-offline" size={18} color="#5C3B00" />
      <Text style={estilos.avisoTexto}>{texto}</Text>
    </View>
  );
}

/** Barra de nível da água com marcas de alerta e crítico. */
export function BarraNivel({ nivel, alerta, critico }: { nivel: number | null; alerta: number; critico: number }) {
  const c = useCores();
  const max = critico * 1.15;
  const pct = Math.min(100, Math.max(0, ((nivel ?? 0) / max) * 100));
  const cor = nivel == null ? c.borda : nivel >= critico ? COR_RISCO.Critico : nivel >= alerta ? COR_RISCO.Alerta
    : nivel >= alerta * 0.6 ? COR_RISCO.Atencao : COR_RISCO.Normal;
  return (
    <View accessible accessibilityLabel={`Nível da água ${nivel ?? 'sem leitura'} centímetros. Alerta em ${alerta}, perigo em ${critico}.`}>
      <View style={[estilos.trilho, { backgroundColor: c.borda }]}>
        <View style={[estilos.preenchimento, { width: `${pct}%`, backgroundColor: cor }]} />
        <View style={[estilos.marca, { left: `${(alerta / max) * 100}%`, backgroundColor: COR_RISCO.Alerta }]} />
        <View style={[estilos.marca, { left: `${(critico / max) * 100}%`, backgroundColor: COR_RISCO.Critico }]} />
      </View>
    </View>
  );
}

export const estilos = StyleSheet.create({
  cartao: { borderRadius: raio.md, padding: espaco.md, borderWidth: StyleSheet.hairlineWidth,
    shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 12, shadowOffset: { width: 0, height: 4 }, elevation: 1 },
  selo: { flexDirection: 'row', alignItems: 'center', gap: 4, alignSelf: 'flex-start', paddingHorizontal: 10,
    paddingVertical: 4, borderRadius: raio.pill },
  seloGrande: { paddingHorizontal: 14, paddingVertical: 6 },
  seloTexto: { color: '#fff', fontWeight: '700', fontSize: 13 },
  botao: { minHeight: 52, borderRadius: raio.md, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: espaco.sm, paddingHorizontal: espaco.md },
  botaoTexto: { fontSize: 17, fontWeight: '600' },
  centro: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: espaco.lg },
  aviso: { flexDirection: 'row', gap: espaco.sm, alignItems: 'center', backgroundColor: '#FFF4D6',
    borderRadius: raio.sm, padding: espaco.sm + 2 },
  avisoTexto: { color: '#5C3B00', flex: 1, fontSize: 14 },
  trilho: { height: 12, borderRadius: 6, overflow: 'visible', marginTop: espaco.sm },
  preenchimento: { height: 12, borderRadius: 6 },
  marca: { position: 'absolute', top: -3, width: 3, height: 18, borderRadius: 2 },
});
