import { Ionicons } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useBairro } from '../../lib/bairro';
import { ORIENTACAO_RISCO, ROTULO_RISCO } from '../../lib/constantes';
import { servicos, type Resultado } from '../../lib/servicos';
import type { Alerta, Painel } from '../../lib/types';
import { AvisoOrigem, Botao, Cartao, Carregando, SeloRisco } from '../../ui/componentes';
import { COR_RISCO, espaco, raio, tipografia, useCores } from '../../ui/tema';

export default function Inicio() {
  const c = useCores();
  const { bairro } = useBairro();
  const [painel, setPainel] = useState<Resultado<Painel> | null>(null);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [atualizando, setAtualizando] = useState(false);

  const carregar = useCallback(async () => {
    const [p, a] = await Promise.all([servicos.painel(), servicos.alertas(bairro)]);
    setPainel(p);
    setAlertas(a.dados);
  }, [bairro]);

  useFocusEffect(useCallback(() => { carregar(); }, [carregar]));

  const atualizar = async () => {
    setAtualizando(true);
    await carregar();
    setAtualizando(false);
  };

  if (!painel) return <Carregando texto="Consultando a situação do seu bairro…" />;

  const resumo = painel.dados.bairros.find((b) => b.bairro === bairro);
  const risco = resumo?.riscoAtual ?? 'Normal';
  const orientacao = ORIENTACAO_RISCO[risco];

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: c.fundo }} edges={['top']}>
      <ScrollView
        contentContainerStyle={estilos.conteudo}
        refreshControl={<RefreshControl refreshing={atualizando} onRefresh={atualizar} tintColor={c.marca} />}
      >
        <Text style={[tipografia.legenda, { color: c.textoSecundario }]}>AquaGuard</Text>
        <Pressable
          onPress={() => router.push('/bairro')}
          accessibilityRole="button"
          accessibilityLabel={`Seu bairro: ${bairro}. Toque para trocar.`}
          style={estilos.linhaBairro}
          hitSlop={8}
        >
          <Text style={[tipografia.tituloGrande, { color: c.texto }]} numberOfLines={1} adjustsFontSizeToFit>{bairro}</Text>
          <Ionicons name="chevron-down" size={22} color={c.marca} />
        </Pressable>

        <AvisoOrigem origem={painel.origem} atualizadoEm={painel.atualizadoEm} />

        <View
          style={[estilos.status, { backgroundColor: COR_RISCO[risco] }]}
          accessible
          accessibilityRole="summary"
          accessibilityLiveRegion="polite"
          accessibilityLabel={`Situação agora em ${bairro}: ${ROTULO_RISCO[risco]}. ${orientacao.titulo}`}
        >
          <Text style={estilos.statusRotulo}>SITUAÇÃO AGORA</Text>
          <Text style={estilos.statusRisco}>{ROTULO_RISCO[risco]}</Text>
          <Text style={estilos.statusTitulo}>{orientacao.titulo}</Text>
          {resumo?.maiorNivelCm != null && (
            <Text style={estilos.statusDetalhe}>Maior nível de água medido: {resumo.maiorNivelCm} cm</Text>
          )}
        </View>

        <Cartao>
          <Text style={[tipografia.subtitulo, { color: c.texto, marginBottom: espaco.sm }]}>O que fazer</Text>
          {orientacao.dicas.map((d) => (
            <View key={d} style={estilos.dica}>
              <Ionicons name="checkmark" size={18} color={c.marca} />
              <Text style={[tipografia.corpo, { color: c.texto, flex: 1 }]}>{d}</Text>
            </View>
          ))}
        </Cartao>

        <Text style={[tipografia.titulo, { color: c.texto }]}>Alertas no bairro</Text>
        {alertas.length === 0 ? (
          <Cartao>
            <Text style={[tipografia.corpo, { color: c.textoSecundario }]}>Nenhum alerta ativo em {bairro}.</Text>
          </Cartao>
        ) : (
          alertas.map((a) => (
            <Cartao key={a.id} style={{ borderLeftWidth: 5, borderLeftColor: COR_RISCO[a.nivel] }}>
              <SeloRisco risco={a.nivel} />
              <Text style={[tipografia.corpo, { color: c.texto, marginTop: espaco.sm }]}>{a.mensagem}</Text>
              <Text style={[tipografia.legenda, { color: c.textoSecundario, marginTop: espaco.xs }]}>
                Emitido em {new Date(a.criadoEmUtc).toLocaleString('pt-BR')}
              </Text>
            </Cartao>
          ))
        )}

        <Botao titulo="Relatar alagamento" icone="megaphone" onPress={() => router.push('/relatar')}
          dica="Abre o formulário para informar um problema na sua rua" />

        <Text style={[tipografia.titulo, { color: c.texto }]}>Cidade</Text>
        <View style={estilos.kpis}>
          {[
            { v: painel.dados.totalSensoresAtivos, l: 'sensores' },
            { v: painel.dados.totalAlertasAtivos, l: 'alertas' },
            { v: painel.dados.totalOcorrenciasAbertas, l: 'relatos abertos' },
          ].map((k) => (
            <Cartao key={k.l} style={estilos.kpi}>
              <Text style={[tipografia.titulo, { color: c.texto }]} accessibilityLabel={`${k.v} ${k.l}`}>{k.v}</Text>
              <Text style={[tipografia.legenda, { color: c.textoSecundario }]}>{k.l}</Text>
            </Cartao>
          ))}
        </View>
        {painel.dados.bairros.map((b) => (
          <Cartao key={b.bairro} style={estilos.linhaCidade}>
            <Text style={[tipografia.corpo, { color: c.texto, flex: 1 }]}>{b.bairro}</Text>
            <SeloRisco risco={b.riscoAtual} />
          </Cartao>
        ))}
        <Text style={[tipografia.legenda, { color: c.textoSecundario, textAlign: 'center' }]}>
          Puxe para atualizar · Emergência: Defesa Civil 199
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const estilos = StyleSheet.create({
  conteudo: { padding: espaco.md, gap: espaco.md, paddingBottom: espaco.xl },
  linhaBairro: { flexDirection: 'row', alignItems: 'center', gap: espaco.xs, minHeight: 48 },
  status: { borderRadius: raio.lg, padding: espaco.lg, gap: 4 },
  statusRotulo: { color: '#ffffffcc', fontSize: 13, fontWeight: '700', letterSpacing: 1 },
  statusRisco: { color: '#fff', fontSize: 40, fontWeight: '800', letterSpacing: -1 },
  statusTitulo: { color: '#fff', fontSize: 19, fontWeight: '600' },
  statusDetalhe: { color: '#ffffffdd', fontSize: 15, marginTop: 4 },
  dica: { flexDirection: 'row', gap: espaco.sm, marginBottom: espaco.xs },
  kpis: { flexDirection: 'row', gap: espaco.sm },
  kpi: { flex: 1, alignItems: 'center', paddingVertical: espaco.md },
  linhaCidade: { flexDirection: 'row', alignItems: 'center', paddingVertical: espaco.sm + 4 },
});
