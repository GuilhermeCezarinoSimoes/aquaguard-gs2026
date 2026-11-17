import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { router } from 'expo-router';
import { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useBairro } from '../../lib/bairro';
import { BAIRROS, TIPOS_OCORRENCIA } from '../../lib/constantes';
import { servicos } from '../../lib/servicos';
import type { TipoOcorrencia } from '../../lib/types';
import { Botao, Cartao } from '../../ui/componentes';
import { espaco, raio, tipografia, useCores } from '../../ui/tema';
import { validarRelato } from '../../lib/validacao';

const ROTULO_SEVERIDADE = ['', 'Leve', 'Moderado', 'Sério', 'Grave', 'Muito grave'];

export default function Relatar() {
  const c = useCores();
  const { bairro } = useBairro();
  const [tipo, setTipo] = useState<TipoOcorrencia>('RuaAlagada');
  const [descricao, setDescricao] = useState('');
  const [severidade, setSeveridade] = useState(3);
  const [apelido, setApelido] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [erros, setErros] = useState<string[]>([]);

  const enviar = async () => {
    const ref = BAIRROS.find((b) => b.nome === bairro) ?? BAIRROS[0];
    const relato = { tipo, descricao: descricao.trim(), bairro, latitude: ref.latitude, longitude: ref.longitude,
      severidade, apelido: apelido.trim() || null };
    const problemas = validarRelato(relato);
    setErros(problemas);
    if (problemas.length) return;

    setEnviando(true);
    const { enviado } = await servicos.registrarRelato(relato);
    setEnviando(false);
    if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success).catch(() => {});
    setDescricao('');
    setApelido('');
    const msg = enviado
      ? 'Obrigado! Seu relato foi enviado e ajuda a avisar seus vizinhos.'
      : 'Sem conexão agora. Seu relato ficou salvo no celular e será enviado depois.';
    if (Platform.OS === 'web') { globalThis.alert?.(msg); router.push('/historico'); }
    else Alert.alert('Relato registrado', msg, [{ text: 'Ver meus relatos', onPress: () => router.push('/historico') }]);
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={estilos.conteudo} keyboardShouldPersistTaps="handled">
        <Text style={[tipografia.corpo, { color: c.textoSecundario }]}>
          Viu um alagamento ou bueiro entupido em <Text style={{ fontWeight: '700', color: c.texto }}>{bairro}</Text>? Conte para a comunidade.
        </Text>

        <Text style={[tipografia.subtitulo, { color: c.texto }]} nativeID="lblTipo">O que está acontecendo?</Text>
        <View style={estilos.grade} accessibilityRole="radiogroup" accessibilityLabelledBy="lblTipo">
          {TIPOS_OCORRENCIA.map((t) => {
            const ativo = t.valor === tipo;
            return (
              <Pressable key={t.valor} onPress={() => setTipo(t.valor)} accessibilityRole="radio"
                accessibilityState={{ checked: ativo }} accessibilityLabel={t.rotulo}
                style={[estilos.opcao, { borderColor: ativo ? c.marca : c.borda, backgroundColor: ativo ? c.marcaSuave : c.superficie }]}>
                <Ionicons name={t.icone as never} size={22} color={ativo ? c.marca : c.textoSecundario} />
                <Text style={[tipografia.legenda, { color: c.texto, fontWeight: ativo ? '700' : '400' }]}>{t.rotulo}</Text>
              </Pressable>
            );
          })}
        </View>

        <Text style={[tipografia.subtitulo, { color: c.texto }]} nativeID="lblDesc">Descreva em poucas palavras</Text>
        <TextInput
          value={descricao}
          onChangeText={setDescricao}
          placeholder="Ex.: Água na altura do joelho na esquina da escola"
          placeholderTextColor={c.textoSecundario}
          multiline
          maxLength={500}
          accessibilityLabel="Descrição do problema"
          accessibilityHint="Mínimo de 5 caracteres. Não escreva CPF, telefone ou dados pessoais."
          style={[estilos.campo, { color: c.texto, borderColor: c.borda, backgroundColor: c.superficie, minHeight: 110 }]}
        />
        <Text style={[tipografia.legenda, { color: c.textoSecundario }]}>{descricao.length}/500 · Não inclua dados pessoais.</Text>

        <Text style={[tipografia.subtitulo, { color: c.texto }]}>Gravidade: {ROTULO_SEVERIDADE[severidade]}</Text>
        <View style={estilos.severidade} accessibilityRole="adjustable" accessibilityLabel="Gravidade"
          accessibilityValue={{ min: 1, max: 5, now: severidade, text: ROTULO_SEVERIDADE[severidade] }}
          accessibilityActions={[{ name: 'increment' }, { name: 'decrement' }]}
          onAccessibilityAction={(e) => setSeveridade((s) => Math.min(5, Math.max(1, s + (e.nativeEvent.actionName === 'increment' ? 1 : -1))))}>
          {[1, 2, 3, 4, 5].map((n) => (
            <Pressable key={n} onPress={() => setSeveridade(n)} accessibilityLabel={`${n}, ${ROTULO_SEVERIDADE[n]}`}
              style={[estilos.nivel, { backgroundColor: n <= severidade ? c.marcaForte : c.borda }]}>
              <Text style={{ color: n <= severidade ? '#fff' : c.texto, fontWeight: '700', fontSize: 17 }}>{n}</Text>
            </Pressable>
          ))}
        </View>

        <Text style={[tipografia.subtitulo, { color: c.texto }]}>Como quer aparecer? (opcional)</Text>
        <TextInput value={apelido} onChangeText={setApelido} placeholder="Apelido, ex.: Vizinho da rua 3" maxLength={40}
          placeholderTextColor={c.textoSecundario} accessibilityLabel="Apelido opcional"
          style={[estilos.campo, { color: c.texto, borderColor: c.borda, backgroundColor: c.superficie }]} />

        {erros.length > 0 && (
          <Cartao style={{ borderColor: c.perigo }}>
            <View accessibilityRole="alert" accessibilityLiveRegion="assertive">
              {erros.map((e) => <Text key={e} style={{ color: c.perigo, fontSize: 15 }}>• {e}</Text>)}
            </View>
          </Cartao>
        )}

        <Botao titulo="Enviar relato" icone="send" onPress={enviar} carregando={enviando}
          dica="Salva no celular e envia para o AquaGuard" />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const estilos = StyleSheet.create({
  conteudo: { padding: espaco.md, gap: espaco.md, paddingBottom: espaco.xl },
  grade: { flexDirection: 'row', flexWrap: 'wrap', gap: espaco.sm },
  opcao: { flexBasis: '47%', flexGrow: 1, minHeight: 64, borderWidth: 1.5, borderRadius: raio.md, padding: espaco.sm + 2,
    gap: 4, justifyContent: 'center' },
  campo: { borderWidth: 1, borderRadius: raio.sm, padding: espaco.md, fontSize: 17, textAlignVertical: 'top', minHeight: 52 },
  severidade: { flexDirection: 'row', gap: espaco.sm },
  nivel: { flex: 1, height: 52, borderRadius: raio.sm, alignItems: 'center', justifyContent: 'center' },
});
