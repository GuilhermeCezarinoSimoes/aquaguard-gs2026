import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { Pressable, ScrollView, Text } from 'react-native';
import { useBairro } from '../lib/bairro';
import { BAIRROS } from '../lib/constantes';
import { espaco, raio, tipografia, useCores } from '../ui/tema';

export default function EscolherBairro() {
  const c = useCores();
  const { bairro, definirBairro } = useBairro();
  return (
    <ScrollView contentContainerStyle={{ padding: espaco.md, gap: espaco.sm }} accessibilityRole="radiogroup">
      <Text style={[tipografia.corpo, { color: c.textoSecundario, marginBottom: espaco.sm }]}>
        Escolha onde você mora ou passa todos os dias. Os alertas da tela inicial serão deste bairro.
      </Text>
      {BAIRROS.map((b) => {
        const ativo = b.nome === bairro;
        return (
          <Pressable
            key={b.nome}
            onPress={async () => { await definirBairro(b.nome); router.back(); }}
            accessibilityRole="radio"
            accessibilityState={{ checked: ativo }}
            accessibilityLabel={b.nome}
            style={{ minHeight: 56, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
              paddingHorizontal: espaco.md, borderRadius: raio.md, backgroundColor: c.superficie,
              borderWidth: ativo ? 2 : 1, borderColor: ativo ? c.marca : c.borda }}
          >
            <Text style={[tipografia.corpo, { color: c.texto, fontWeight: ativo ? '700' : '400' }]}>{b.nome}</Text>
            {ativo && <Ionicons name="checkmark-circle" size={24} color={c.marca} />}
          </Pressable>
        );
      })}
    </ScrollView>
  );
}
