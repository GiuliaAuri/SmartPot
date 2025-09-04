"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Leaf } from "lucide-react"
import { PlantDashboard } from "@/components/plant-dashboard"
import { PlantConfiguration } from "@/components/plant-configuration"
import { AlertsPanel } from "@/components/alerts-panel"
import { RealTimeMonitoring } from "@/components/real-time-monitoring"

// Mock data per la demo
const mockPlants = [
  {
    id: 1,
    userId: "mario",
    name: "Basilico",
    type: "Erba aromatica",
    status: "healthy",
    waterLevel: 75,
    soilMoisture: 65,
    temperature: 22,
    humidity: 60,
    lightLevel: 80,
    batteryLevel: 85,
    waterFlow: 0.2,
    isWatering: false,
    lastWatered: "2 ore fa",
  },
  {
    id: 2,
    userId: "mario",
    name: "Pomodori",
    type: "Ortaggio",
    status: "warning",
    waterLevel: 25,
    soilMoisture: 35,
    temperature: 25,
    humidity: 55,
    lightLevel: 90,
    batteryLevel: 20,
    waterFlow: 0,
    isWatering: false,
    lastWatered: "6 ore fa",
  },
  {
    id: 3,
    userId: "lucia",
    name: "Orchidea",
    type: "Fiore",
    status: "good",
    waterLevel: 60,
    soilMoisture: 70,
    temperature: 20,
    humidity: 70,
    lightLevel: 60,
    batteryLevel: 95,
    waterFlow: 0,
    isWatering: false,
    lastWatered: "1 giorno fa",
  },
  {
    id: 4,
    userId: "lucia",
    name: "Rosmarino",
    type: "Erba aromatica",
    status: "healthy",
    waterLevel: 80,
    soilMoisture: 55,
    temperature: 24,
    humidity: 50,
    lightLevel: 85,
    batteryLevel: 70,
    waterFlow: 0,
    isWatering: false,
    lastWatered: "4 ore fa",
  },
  {
    id: 5,
    userId: "giovanni",
    name: "Menta",
    type: "Erba aromatica",
    status: "critical",
    waterLevel: 10,
    soilMoisture: 20,
    temperature: 28,
    humidity: 40,
    lightLevel: 75,
    batteryLevel: 15,
    waterFlow: 0,
    isWatering: false,
    lastWatered: "12 ore fa",
  },
]

// Mock data per la demo
const mockAlerts = [
  {
    id: 1,
    userId: "mario",
    type: "warning",
    plantName: "Pomodori",
    message: "Livello acqua basso (25%)",
    timestamp: "5 minuti fa",
  },
  {
    id: 2,
    userId: "mario",
    type: "critical",
    plantName: "Pomodori",
    message: "Batteria scarica (20%)",
    timestamp: "10 minuti fa",
  },
  {
    id: 3,
    userId: "mario",
    type: "info",
    plantName: "Basilico",
    message: "Irrigazione completata",
    timestamp: "2 ore fa",
  },
  {
    id: 4,
    userId: "giovanni",
    type: "critical",
    plantName: "Menta",
    message: "Serbatoio vuoto (10%)",
    timestamp: "1 minuto fa",
  },
  {
    id: 5,
    userId: "giovanni",
    type: "critical",
    plantName: "Menta",
    message: "Batteria critica (15%)",
    timestamp: "3 minuti fa",
  },
]

// Lista utenti disponibili
const users = [
  { id: "mario", name: "Mario Rossi" },
  { id: "lucia", name: "Lucia Bianchi" },
  { id: "giovanni", name: "Giovanni Verdi" },
]

const userCredentials = [
  { id: "mario", name: "Mario Rossi", username: "mario", password: "password123" },
  { id: "lucia", name: "Lucia Bianchi", username: "lucia", password: "password123" },
  { id: "giovanni", name: "Giovanni Verdi", username: "giovanni", password: "password123" },
]

export default function SmartPlantDashboard() {
  const [plants, setPlantsData] = useState(mockPlants)
  const [alerts, setAlerts] = useState(mockAlerts)
  const [activeTab, setActiveTab] = useState("dashboard")
  const [selectedUser, setSelectedUser] = useState("mario")
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [loginError, setLoginError] = useState("")

  const userPlants = plants.filter((plant) => plant.userId === selectedUser)
  const userAlerts = alerts.filter((alert) => alert.userId === selectedUser)

  // Simula aggiornamenti in tempo reale
  useEffect(() => {
    const interval = setInterval(() => {
      setPlantsData((prev) =>
        prev.map((plant) => ({
          ...plant,
          soilMoisture: Math.max(0, plant.soilMoisture + (Math.random() - 0.5) * 2),
          temperature: Math.max(15, Math.min(35, plant.temperature + (Math.random() - 0.5) * 1)),
          humidity: Math.max(30, Math.min(90, plant.humidity + (Math.random() - 0.5) * 2)),
          lightLevel: Math.max(0, Math.min(100, plant.lightLevel + (Math.random() - 0.5) * 3)),
        })),
      )
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-500"
      case "good":
        return "bg-blue-500"
      case "warning":
        return "bg-yellow-500"
      case "critical":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "healthy":
        return "Ottimo"
      case "good":
        return "Buono"
      case "warning":
        return "Attenzione"
      case "critical":
        return "Critico"
      default:
        return "Sconosciuto"
    }
  }

  const handleLogin = () => {
    const user = userCredentials.find((u) => u.username === username && u.password === password)

    if (user) {
      setSelectedUser(user.id)
      setIsLoginOpen(false)
      setUsername("")
      setPassword("")
      setLoginError("")
    } else {
      setLoginError("Nome utente o password non corretti")
    }
  }

  const handleCloseLogin = () => {
    setIsLoginOpen(false)
    setUsername("")
    setPassword("")
    setLoginError("")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-center mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500 rounded-lg">
                <Leaf className="h-6 w-6 text-white" />
              </div>
              <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white text-left">Smart Plants - IoT System</h1>
                <p className="text-gray-600 dark:text-gray-300 text-left">
                  Sistema intelligente per la gestione e monitoraggio dei tuoi vasi
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="monitoring">Monitoraggio</TabsTrigger>
            <TabsTrigger value="configuration">Configurazione</TabsTrigger>
            <TabsTrigger value="alerts">Avvisi</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard">
            <PlantDashboard plants={userPlants} setPlantsData={setPlantsData} />
          </TabsContent>

          <TabsContent value="monitoring">
            <RealTimeMonitoring plants={userPlants} />
          </TabsContent>

          <TabsContent value="configuration">
            <PlantConfiguration plants={userPlants} setPlantsData={setPlantsData} />
          </TabsContent>

          <TabsContent value="alerts">
            <AlertsPanel alerts={userAlerts} setAlerts={setAlerts} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
