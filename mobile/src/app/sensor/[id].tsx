import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { servicos, type Resultado } from '../../lib/servicos';
import type { Leitura, Sensor } from '../../lib/types';
import { AvisoOrigem, BarraNivel, Cartao, Carregando, EstadoVazio, SeloRisco } from '../../ui/componentes';
import { COR_RISCO, espaco, tipografia, useCores } from '../../ui/tema';

export default function DetalheSensor() {
  const c = useCores();
  const { id } = useLocalSearchParams<{ id: string }>();
  const sensorId = Number(id);
  const [sensor, setSensor] = useState<Sensor | null>(null);
  const [leituras, setLeituras] = useState<Resultado<Leitura[]> | null>(null);

  useEffect(() => {
    (async () => {
      const [s, l] = await Promise.all([servicos.sensores(), servicos.leituras(sensorId)]);
      setSensor(s.dados.find((x) => x.id === sensorId) ?? null);
      setLeituras(l);
    })();
  }, [sensorId]);

  if (!leituras) return <Carregando />;
  if (!sensor) return <EstadoVazio icone="help-circle-outline" titulo="Ponto não encontrado" texto="Volte e escolha outro ponto." />;

  const serie = [...leituras.dados].reverse().slice(-24); // cronológica, últimas 24
  const max = Math.max(sensor.nivelCriticoCm, ...serie.map((l) => l.nivelAguaCm), 1);

  return (
    <ScrollView contentContainerStyle={{ padding: espaco.md, gap: espaco.md }}>
      <AvisoOrigem origem={leituras.origem} atualizadoEm={leituras.atualizadoEm} />
      <View>
        <Text style={[tipografia.legenda, { color: c.textoSecundario }]}>{sensor.codigo} · {sensor.bairro}</Text>
        <Text style={[tipografia.titulo, { color: c.texto }]}>{sensor.nome}</Text>
      </View>

      <Cartao>
        <View style={estilos.linha}>
          <Text style={[tipografia.tituloGrande, { color: c.texto }]}>
            {sensor.ultimoNivelCm != null ? `${sensor.ultimoNivelCm} cm` : '—'}
          </Text>
          {sensor.ultimoRisco && <SeloRisco risco={sensor.ultimoRisco} grande />}
        </View>
        <BarraNivel nivel={sensor.ultimoNivelCm} alerta={sensor.nivelAlertaCm} critico={sensor.nivelCriticoCm} />
        <Text style={[tipografia.legenda, { color: c.textoSecundario, marginTop: espaco.sm }]}>
          {sensor.ultimaLeituraUtc ? `Última leitura: ${new Date(sensor.ultimaLeituraUtc).toLocaleString('pt-BR')}` : 'Sem leituras recentes'}
        </Text>
      </Cartao>

      <Cartao>
        <Text style={[tipografia.subtitulo, { color: c.texto }]}>Nível da água nas últimas leituras</Text>
        {serie.length === 0 ? (
          <Text style={[tipografia.corpo, { color: c.textoSecundario, marginTop: espaco.sm }]}>Sem leituras nas últimas 24 h.</Text>
        ) : (
          <View style={estilos.grafico} accessible
            accessibilityLabel={`Gráfico com ${serie.length} leituras. Mínimo ${Math.min(...serie.map((l) => l.nivelAguaCm))} e máximo ${Math.max(...serie.map((l) => l.nivelAguaCm))} centímetros.`}>
            {serie.map((l) => (
              <View key={l.id} style={estilos.colunaWrap}>
                <View style={[estilos.coluna, { height: `${(l.nivelAguaCm / max) * 100}%`, backgroundColor: COR_RISCO[l.risco] }]} />
              </View>
            ))}
          </View>
        )}
      </Cartao>

      <Cartao>
        <Text style={[tipografia.subtitulo, { color: c.texto, marginBottom: espaco.sm }]}>Leituras recentes</Text>
        {leituras.dados.slice(0, 8).map((l) => (
          <View key={l.id} style={[estilos.item, { borderBottomColor: c.borda }]}>
            <Text style={[tipografia.corpo, { color: c.texto, flex: 1 }]}>
              {new Date(l.dataHoraUtc).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
            </Text>
            <Text style={[tipografia.corpo, { color: c.texto, width: 80 }]}>{l.nivelAguaCm} cm</Text>
            <Text style={[tipografia.legenda, { color: c.textoSecundario, width: 80 }]}>{l.chuvaMmH} mm/h</Text>
          </View>
        ))}
      </Cartao>
    </ScrollView>
  );
}

const estilos = StyleSheet.create({
  linha: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  grafico: { height: 140, flexDirection: 'row', alignItems: 'flex-end', gap: 3, marginTop: espaco.md },
  colunaWrap: { flex: 1, maxWidth: 28, height: '100%', justifyContent: 'flex-end' },
  coluna: { borderTopLeftRadius: 4, borderTopRightRadius: 4, minHeight: 2 },
  item: { flexDirection: 'row', alignItems: 'center', paddingVertical: espaco.sm, borderBottomWidth: StyleSheet.hairlineWidth },
});
