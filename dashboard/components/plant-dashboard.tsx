"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Switch } from "@/components/ui/switch"
import { Droplets, Thermometer, Sun, Battery, Leaf, Play, Pause, AlertTriangle, AlertCircle, Info } from "lucide-react"

interface Plant {
  id: number
  name: string
  type: string
  status: string
  waterLevel: number
  temperature: number
  humidity: number
  lightLevel: number
  batteryLevel: number
  waterFlow: number
  isWatering: boolean
  lastWatered: string
}

interface Alert {
  id: string
  plantName: string
  type: "critical" | "warning" | "info"
  message: string
  timestamp: string
  isActive: boolean
}

interface PlantDashboardProps {
  plants: Plant[]
  setPlantsData: (plants: Plant[]) => void
  alerts: Alert[]
}

export function PlantDashboard({ plants, setPlantsData, alerts }: PlantDashboardProps) {
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

  const getStatusTextColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-white"
      case "good":
        return "text-white"
      case "warning":
        return "text-yellow-900 dark:text-yellow-100" // Dark text on yellow background for better contrast
      case "critical":
        return "text-white"
      default:
        return "text-white"
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

  const getActiveAlertsForPlant = (plantName: string) => {
    return alerts.filter((alert) => alert.plantName === plantName && alert.isActive)
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "critical":
        return <AlertTriangle className="h-3 w-3" />
      case "warning":
        return <AlertCircle className="h-3 w-3" />
      case "info":
        return <Info className="h-3 w-3" />
      default:
        return <Info className="h-3 w-3" />
    }
  }

  const getAlertColor = (type: string) => {
    switch (type) {
      case "critical":
        return "bg-red-100 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800"
      case "warning":
        return "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800"
      case "info":
        return "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800"
      default:
        return "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-950 dark:text-gray-300 dark:border-gray-800"
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4 sm:gap-6">
      {plants.map((plant) => {
        const plantAlerts = getActiveAlertsForPlant(plant.name)

        return (
          <Card key={plant.id} className="overflow-hidden">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg flex-shrink-0">
                    <Leaf className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <CardTitle className="text-base sm:text-lg truncate">{plant.name}</CardTitle>
                    <CardDescription className="text-xs sm:text-sm truncate">{plant.type}</CardDescription>
                  </div>
                </div>
                <Badge
                  className={`${getStatusColor(plant.status)} ${getStatusTextColor(plant.status)} border-0 text-xs sm:text-sm flex-shrink-0 ml-2`}
                >
                  {getStatusText(plant.status)}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-3 sm:space-y-4">
              {plantAlerts.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300">Avvisi Attivi:</h4>
                  <div className="space-y-1 sm:space-y-2 max-h-32 overflow-y-auto">
                    {plantAlerts.map((alert) => (
                      <div
                        key={alert.id}
                        className={`flex items-start gap-2 p-2 rounded-lg border ${getAlertColor(alert.type)}`}
                      >
                        <div className="flex-shrink-0 mt-0.5">{getAlertIcon(alert.type)}</div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium leading-tight">{alert.message}</p>
                          <p className="text-xs opacity-75 mt-0.5">{alert.timestamp}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <Droplets className="h-4 w-4 text-blue-600 flex-shrink-0" />
                  <span className="text-xs sm:text-sm font-medium">Irrigazione</span>
                  {plant.isWatering && (
                    <Badge variant="secondary" className="text-xs ml-1">
                      {plant.waterFlow} L/s
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                  <Switch
                    checked={plant.isWatering}
                    onCheckedChange={() => toggleWatering(plant.id)}
                    className="scale-75 sm:scale-100"
                  />
                  <Button
                    size="sm"
                    variant={plant.isWatering ? "destructive" : "default"}
                    onClick={() => toggleWatering(plant.id)}
                    className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                  >
                    {plant.isWatering ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 sm:gap-3">
                {/* Livello Acqua */}
                <div className="space-y-1 sm:space-y-2">
                  <div className="flex items-center gap-1 sm:gap-2">
                    <Droplets className="h-3 w-3 sm:h-4 sm:w-4 text-blue-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm truncate">Acqua</span>
                  </div>
                  <Progress value={plant.waterLevel} className="h-1.5 sm:h-2" />
                  <p className="text-xs text-gray-600 dark:text-gray-400">{plant.waterLevel.toFixed(1)}%</p>
                </div>

                {/* Batteria */}
                <div className="space-y-1 sm:space-y-2">
                  <div className="flex items-center gap-1 sm:gap-2">
                    <Battery className="h-3 w-3 sm:h-4 sm:w-4 text-green-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm truncate">Batteria</span>
                  </div>
                  <Progress value={plant.batteryLevel} className="h-1.5 sm:h-2" />
                  <p className="text-xs text-gray-600 dark:text-gray-400">{plant.batteryLevel}%</p>
                </div>

                {/* Umidità Terreno */}
                <div className="space-y-1 sm:space-y-2">
                  <div className="flex items-center gap-1 sm:gap-2">
                    <Droplets className="h-3 w-3 sm:h-4 sm:w-4 text-cyan-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm truncate">Umidità</span>
                  </div>
                  <Progress value={plant.humidity} className="h-1.5 sm:h-2" />
                  <p className="text-xs text-gray-600 dark:text-gray-400">{plant.humidity.toFixed(1)}%</p>
                </div>

                {/* Luminosità */}
                <div className="space-y-1 sm:space-y-2">
                  <div className="flex items-center gap-1 sm:gap-2">
                    <Sun className="h-3 w-3 sm:h-4 sm:w-4 text-yellow-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm truncate">Luce</span>
                  </div>
                  <Progress value={plant.lightLevel} className="h-1.5 sm:h-2" />
                  <p className="text-xs text-gray-600 dark:text-gray-400">{plant.lightLevel.toFixed(1)}%</p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:justify-between gap-2 text-xs sm:text-sm">
                <div className="flex items-center gap-1">
                  <Thermometer className="h-3 w-3 sm:h-4 sm:w-4 text-red-500 flex-shrink-0" />
                  <span>{plant.temperature.toFixed(1)}°C</span>
                </div>
                <div className="text-gray-600 dark:text-gray-400 text-xs">Ultima irrigazione: {plant.lastWatered}</div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
