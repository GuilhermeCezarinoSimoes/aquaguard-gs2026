import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { BairroProvider } from '../lib/bairro';
import { useCores } from '../ui/tema';

export default function RootLayout() {
  const c = useCores();
  return (
    <BairroProvider>
      <StatusBar style="auto" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: c.fundo },
          headerTintColor: c.marca,
          headerTitleStyle: { color: c.texto },
          headerShadowVisible: false,
          contentStyle: { backgroundColor: c.fundo },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="sensor/[id]" options={{ title: 'Ponto monitorado', headerBackTitle: 'Voltar' }} />
        <Stack.Screen name="bairro" options={{ title: 'Seu bairro', presentation: 'modal' }} />
      </Stack>
    </BairroProvider>
  );
}
