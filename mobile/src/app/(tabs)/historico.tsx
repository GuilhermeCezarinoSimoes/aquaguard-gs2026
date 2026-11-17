import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';
import { banco } from '../../db/database';
import { TIPOS_OCORRENCIA } from '../../lib/constantes';
import { servicos } from '../../lib/servicos';
import type { RelatoLocal, StatusSync } from '../../lib/types';
import { Botao, Cartao, Carregando, EstadoVazio } from '../../ui/componentes';
import { espaco, tipografia, useCores } from '../../ui/tema';

const STATUS: Record<StatusSync, { texto: string; icone: 'cloud-done' | 'cloud-upload' | 'alert-circle' }> = {
  enviado: { texto: 'Enviado', icone: 'cloud-done' },
  pendente: { texto: 'Aguardando conexão', icone: 'cloud-upload' },
  erro: { texto: 'Erro no envio', icone: 'alert-circle' },
};

export default function Historico() {
  const c = useCores();
  const [relatos, setRelatos] = useState<RelatoLocal[] | null>(null);
  const [sincronizando, setSincronizando] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);

  const carregar = useCallback(async () => setRelatos(await banco.listarRelatos()), []);
  useFocusEffect(useCallback(() => { carregar(); }, [carregar]));

  const sincronizar = async () => {
    setSincronizando(true);
    const r = await servicos.sincronizarPendentes();
    setSincronizando(false);
    setMensagem(r.pendentes === 0 ? `${r.enviados} relato(s) enviado(s).` : `${r.pendentes} relato(s) ainda sem conexão.`);
    carregar();
  };

  if (!relatos) return <Carregando />;
  const pendentes = relatos.filter((r) => r.statusSync !== 'enviado').length;

  return (
    <FlatList
      data={relatos}
      keyExtractor={(r) => String(r.idLocal)}
      contentContainerStyle={{ padding: espaco.md, gap: espaco.md, flexGrow: 1 }}
      ListHeaderComponent={
        <View style={{ gap: espaco.sm }}>
          <Text style={[tipografia.legenda, { color: c.textoSecundario }]}>
            Seus relatos ficam salvos neste celular, mesmo sem internet.
          </Text>
          {pendentes > 0 && (
            <Botao titulo={`Enviar ${pendentes} pendente(s)`} icone="cloud-upload" variante="secundario"
              onPress={sincronizar} carregando={sincronizando} />
          )}
          {mensagem && <Text accessibilityLiveRegion="polite" style={{ color: c.texto }}>{mensagem}</Text>}
        </View>
      }
      ListEmptyComponent={<EstadoVazio icone="document-text-outline" titulo="Nenhum relato ainda"
        texto="Quando você relatar um alagamento, ele aparece aqui." />}
      renderItem={({ item: r }) => {
        const tipo = TIPOS_OCORRENCIA.find((t) => t.valor === r.tipo);
        const st = STATUS[r.statusSync];
        return (
          <Cartao>
            <View style={estilos.topo}>
              <Text style={[tipografia.subtitulo, { color: c.texto, flex: 1 }]}>{tipo?.rotulo ?? r.tipo}</Text>
              <View style={estilos.status} accessible accessibilityLabel={`Status: ${st.texto}`}>
                <Ionicons name={st.icone} size={16} color={r.statusSync === 'enviado' ? c.sucesso : c.textoSecundario} />
                <Text style={[tipografia.legenda, { color: c.textoSecundario }]}>{st.texto}</Text>
              </View>
            </View>
            <Text style={[tipografia.corpo, { color: c.texto, marginTop: espaco.xs }]}>{r.descricao}</Text>
            <Text style={[tipografia.legenda, { color: c.textoSecundario, marginTop: espaco.xs }]}>
              {r.bairro} · gravidade {r.severidade}/5 · {new Date(r.criadoEm).toLocaleString('pt-BR')}
              {r.idRemoto ? ` · protocolo #${r.idRemoto}` : ''}
            </Text>
          </Cartao>
        );
      }}
    />
  );
}

const estilos = StyleSheet.create({
  topo: { flexDirection: 'row', alignItems: 'center', gap: espaco.sm },
  status: { flexDirection: 'row', alignItems: 'center', gap: 4 },
});
