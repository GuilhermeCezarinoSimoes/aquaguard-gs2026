import { Ionicons } from '@expo/vector-icons';
import { Tabs } from 'expo-router/tabs';
import { useCores } from '../../ui/tema';

export default function TabsLayout() {
  const c = useCores();
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: c.marca,
        tabBarInactiveTintColor: c.textoSecundario,
        tabBarStyle: { backgroundColor: c.superficie, borderTopColor: c.borda, minHeight: 60 },
        tabBarLabelStyle: { fontSize: 12, fontWeight: '600' },
        headerStyle: { backgroundColor: c.fundo },
        headerTitleStyle: { color: c.texto, fontWeight: '700' },
        headerShadowVisible: false,
        sceneStyle: { backgroundColor: c.fundo },
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Início', headerShown: false,
        tabBarIcon: ({ color, size }) => <Ionicons name="home" color={color as string} size={size} />,
        tabBarAccessibilityLabel: 'Início: situação do seu bairro' }} />
      <Tabs.Screen name="sensores" options={{ title: 'Pontos',
        tabBarIcon: ({ color, size }) => <Ionicons name="water" color={color as string} size={size} />,
        tabBarAccessibilityLabel: 'Pontos monitorados por sensores' }} />
      <Tabs.Screen name="relatar" options={{ title: 'Relatar',
        tabBarIcon: ({ color, size }) => <Ionicons name="add-circle" color={color as string} size={size} />,
        tabBarAccessibilityLabel: 'Relatar um alagamento' }} />
      <Tabs.Screen name="historico" options={{ title: 'Meus relatos',
        tabBarIcon: ({ color, size }) => <Ionicons name="time" color={color as string} size={size} />,
        tabBarAccessibilityLabel: 'Histórico dos meus relatos' }} />
    </Tabs>
  );
}

