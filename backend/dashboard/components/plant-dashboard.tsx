"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Switch } from "@/components/ui/switch"
import { Droplets, Thermometer, Sun, Battery, Leaf, Play, Pause } from "lucide-react"

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

interface PlantDashboardProps {
  plants: Plant[]
  setPlantsData: (plants: Plant[]) => void
}

export function PlantDashboard({ plants, setPlantsData }: PlantDashboardProps) {
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

  const toggleWatering = (plantId: number) => {
    setPlantsData(
      plants.map((plant) =>
        plant.id === plantId
          ? { ...plant, isWatering: !plant.isWatering, waterFlow: plant.isWatering ? 0 : 0.3 }
          : plant,
      ),
    )
  }

  const getProgressColor = (value: number, type: "water" | "battery" | "moisture") => {
    if (type === "water" || type === "battery") {
      if (value < 20) return "bg-red-500"
      if (value < 40) return "bg-yellow-500"
      return "bg-green-500"
    }
    if (type === "moisture") {
      if (value < 30) return "bg-red-500"
      if (value < 50) return "bg-yellow-500"
      return "bg-green-500"
    }
    return "bg-blue-500"
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {plants.map((plant) => (
        <Card key={plant.id} className="overflow-hidden">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <Leaf className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <CardTitle className="text-lg">{plant.name}</CardTitle>
                  <CardDescription>{plant.type}</CardDescription>
                </div>
              </div>
              <Badge className={`${getStatusColor(plant.status)} text-white border-0`}>
                {getStatusText(plant.status)}
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Controllo Irrigazione */}
            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
              <div className="flex items-center gap-2">
                <Droplets className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Irrigazione</span>
                {plant.isWatering && (
                  <Badge variant="secondary" className="text-xs">
                    {plant.waterFlow} L/s
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Switch checked={plant.isWatering} onCheckedChange={() => toggleWatering(plant.id)} />
                <Button
                  size="sm"
                  variant={plant.isWatering ? "destructive" : "default"}
                  onClick={() => toggleWatering(plant.id)}
                >
                  {plant.isWatering ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                </Button>
              </div>
            </div>

            {/* Sensori */}
            <div className="grid grid-cols-2 gap-3">
              {/* Livello Acqua */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Droplets className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">Acqua</span>
                </div>
                <Progress value={plant.waterLevel} className="h-2" />
                <p className="text-xs text-gray-600 dark:text-gray-400">{plant.waterLevel}%</p>
              </div>

              {/* Batteria */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Battery className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Batteria</span>
                </div>
                <Progress value={plant.batteryLevel} className="h-2" />
                <p className="text-xs text-gray-600 dark:text-gray-400">{plant.batteryLevel}%</p>
              </div>

              {/* Umidità Terreno */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Droplets className="h-4 w-4 text-cyan-500" />
                  <span className="text-sm">Umidità</span>
                </div>
                <Progress value={plant.soilMoisture} className="h-2" />
                <p className="text-xs text-gray-600 dark:text-gray-400">{plant.soilMoisture.toFixed(1)}%</p>
              </div>

              {/* Luminosità */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">Luce</span>
                </div>
                <Progress value={plant.lightLevel} className="h-2" />
                <p className="text-xs text-gray-600 dark:text-gray-400">{plant.lightLevel.toFixed(1)}%</p>
              </div>
            </div>

            {/* Dati Ambientali */}
            <div className="flex justify-between text-sm">
              <div className="flex items-center gap-1">
                <Thermometer className="h-4 w-4 text-red-500" />
                <span>{plant.temperature}°C</span>
              </div>
              <div className="text-gray-600 dark:text-gray-400">Ultima irrigazione: {plant.lastWatered}</div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
