import { Ionicons } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { useBairro } from '../../lib/bairro';
import { ORDEM_RISCO } from '../../lib/constantes';
import { servicos, type Resultado } from '../../lib/servicos';
import type { Sensor } from '../../lib/types';
import { AvisoOrigem, BarraNivel, Cartao, Carregando, EstadoVazio, SeloRisco } from '../../ui/componentes';
import { espaco, tipografia, useCores } from '../../ui/tema';

export default function Sensores() {
  const c = useCores();
  const { bairro } = useBairro();
  const [res, setRes] = useState<Resultado<Sensor[]> | null>(null);
  const [atualizando, setAtualizando] = useState(false);

  const carregar = useCallback(async () => setRes(await servicos.sensores()), []);
  useFocusEffect(useCallback(() => { carregar(); }, [carregar]));

  if (!res) return <Carregando texto="Buscando pontos monitorados…" />;

  // Bairro do usuário primeiro; depois, maior risco.
  const lista = [...res.dados].sort((a, b) =>
    Number(b.bairro === bairro) - Number(a.bairro === bairro) ||
    ORDEM_RISCO[b.ultimoRisco ?? 'Normal'] - ORDEM_RISCO[a.ultimoRisco ?? 'Normal']);

  return (
    <FlatList
      data={lista}
      keyExtractor={(s) => String(s.id)}
      contentContainerStyle={{ padding: espaco.md, gap: espaco.md }}
      refreshControl={<RefreshControl refreshing={atualizando} tintColor={c.marca}
        onRefresh={async () => { setAtualizando(true); await carregar(); setAtualizando(false); }} />}
      ListHeaderComponent={<AvisoOrigem origem={res.origem} atualizadoEm={res.atualizadoEm} />}
      ListEmptyComponent={<EstadoVazio icone="water-outline" titulo="Nenhum sensor ativo" texto="Ainda não há pontos monitorados." />}
      renderItem={({ item: s }) => (
        <Pressable
          onPress={() => router.push({ pathname: '/sensor/[id]', params: { id: String(s.id) } })}
          accessibilityRole="button"
          accessibilityLabel={`${s.nome}, bairro ${s.bairro}. Nível ${s.ultimoNivelCm ?? 'sem leitura'} centímetros.`}
          accessibilityHint="Abre o histórico deste ponto"
          style={({ pressed }) => ({ opacity: pressed ? 0.85 : 1 })}
        >
          <Cartao>
            <View style={estilos.topo}>
              <View style={{ flex: 1 }}>
                <Text style={[tipografia.legenda, { color: c.textoSecundario }]}>
                  {s.codigo} · {s.bairro}{s.bairro === bairro ? ' · seu bairro' : ''}
                </Text>
                <Text style={[tipografia.subtitulo, { color: c.texto }]}>{s.nome}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={c.textoSecundario} />
            </View>
            <View style={estilos.linha}>
              <Text style={[tipografia.titulo, { color: c.texto }]}>
                {s.ultimoNivelCm != null ? `${s.ultimoNivelCm} cm` : '—'}
              </Text>
              {s.ultimoRisco && <SeloRisco risco={s.ultimoRisco} />}
            </View>
            <BarraNivel nivel={s.ultimoNivelCm} alerta={s.nivelAlertaCm} critico={s.nivelCriticoCm} />
            <Text style={[tipografia.legenda, { color: c.textoSecundario, marginTop: espaco.sm }]}>
              Alerta a partir de {s.nivelAlertaCm} cm · perigo a partir de {s.nivelCriticoCm} cm
            </Text>
          </Cartao>
        </Pressable>
      )}
    />
  );
}

const estilos = StyleSheet.create({
  topo: { flexDirection: 'row', alignItems: 'center', gap: espaco.sm },
  linha: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: espaco.sm },
});
