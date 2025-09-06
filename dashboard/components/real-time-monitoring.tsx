"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts"
import { Droplets, Thermometer, Sun, Battery, Activity, Leaf } from "lucide-react"

interface Plant {
  id: number
  name: string
  type: string
  status: string
  waterLevel: number
  soilMoisture: number
  temperature: number
  humidity: number
  lightLevel: number
  batteryLevel: number
  waterFlow: number
  isWatering: boolean
  lastWatered: string
}

interface RealTimeMonitoringProps {
  plants: Plant[]
}

export function RealTimeMonitoring({ plants }: RealTimeMonitoringProps) {
  const [historicalData, setHistoricalData] = useState<any[]>([])
  const [selectedPlant, setSelectedPlant] = useState(plants[0]?.id || 1)

  // Genera dati storici simulati
  useEffect(() => {
    const generateHistoricalData = () => {
      const data = []
      const now = new Date()

      for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000)
        const plant = plants.find((p) => p.id === selectedPlant)

        if (plant) {
          data.push({
            time: time.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" }),
            temperature: plant.temperature + (Math.random() - 0.5) * 4,
            humidity: plant.soilMoisture + (Math.random() - 0.5) * 10,
            lightLevel: plant.lightLevel + (Math.random() - 0.5) * 20,
            waterLevel: Math.max(0, plant.waterLevel + (Math.random() - 0.7) * 5),
          })
        }
      }

      return data
    }

    setHistoricalData(generateHistoricalData())
  }, [selectedPlant, plants])

  const selectedPlantData = plants.find((p) => p.id === selectedPlant)

  if (!selectedPlantData) return null

  return (
    <div className="space-y-6">
      {/* Selezione Pianta */}
      <Card
        className="bg-gradient-to-r from-green-25 to-blue-25 dark:from-green-950 dark:to-blue-950 border-green-100 dark:border-green-800"
        style={{ background: "linear-gradient(to right, #f0fdf4, #f0f9ff)" }}
      >
        <CardHeader className="pb-4">
          <CardTitle className="text-green-800 dark:text-green-200 flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Monitoraggio in Tempo Reale
          </CardTitle>
          <CardDescription className="text-green-700 dark:text-green-300">
            Seleziona una pianta per visualizzare i dati storici e in tempo reale
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {plants.map((plant) => (
              <Badge
                key={plant.id}
                variant={selectedPlant === plant.id ? "default" : "outline"}
                className={`cursor-pointer px-6 py-4 text-center font-medium transition-all duration-200 hover:scale-105 flex items-center justify-center gap-2 text-lg flex-1 min-w-0 ${
                  selectedPlant === plant.id
                    ? "bg-green-600 hover:bg-green-700 text-white shadow-lg"
                    : "border-green-300 text-green-700 hover:bg-green-100 dark:border-green-600 dark:text-green-300 dark:hover:bg-green-900"
                }`}
                onClick={() => setSelectedPlant(plant.id)}
              >
                <Leaf className="h-5 w-5" />
                {plant.name}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dati Attuali */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                <Thermometer className="h-5 w-5 text-red-600 dark:text-red-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-600 dark:text-gray-400">Temperatura</p>
                <p className="text-2xl font-bold truncate">{selectedPlantData.temperature.toFixed(1)}°C</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Droplets className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Umidità Terreno</p>
                <p className="text-2xl font-bold">{selectedPlantData.soilMoisture.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <Sun className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Luminosità</p>
                <p className="text-2xl font-bold">{selectedPlantData.lightLevel.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <Battery className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Livello Acqua</p>
                <p className="text-2xl font-bold">{selectedPlantData.waterLevel}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Grafici */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temperatura e Umidità */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Temperatura e Umidità (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="temperature" stroke="#ef4444" strokeWidth={2} name="Temperatura (°C)" />
                <Line type="monotone" dataKey="humidity" stroke="#06b6d4" strokeWidth={2} name="Umidità (%)" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Luminosità e Livello Acqua */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sun className="h-5 w-5" />
              Luminosità e Livello Acqua (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="lightLevel"
                  stackId="1"
                  stroke="#eab308"
                  fill="#eab308"
                  fillOpacity={0.3}
                  name="Luminosità (%)"
                />
                <Area
                  type="monotone"
                  dataKey="waterLevel"
                  stackId="2"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                  name="Livello Acqua (%)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Status Irrigazione */}
      {selectedPlantData.isWatering && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500 rounded-lg animate-pulse">
                <Droplets className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="font-medium text-blue-900 dark:text-blue-100">
                  Irrigazione in corso per {selectedPlantData.name}
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-300">Flusso: {selectedPlantData.waterFlow} L/s</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
