"use client"

import type React from "react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Droplets, Leaf, Play, Pause } from "lucide-react"

interface Plant {
  id: string
  name: string
  type: string
  soilMoisture: number
  isWatering: boolean
  lastWatered: string
}

interface PlantDashboardProps {
  plants: Plant[]
  setPlantsData: (plants: Plant[]) => void
  onIrrigationControl?: (plantId: string, action: "start" | "stop") => void
}

export function PlantDashboard({ plants, setPlantsData, onIrrigationControl }: PlantDashboardProps) {
  const handleManualControl = (plantId: string, action: "start" | "stop") => {
    console.log(`🔧 Manual control clicked: ${plantId} - ${action}`)
    if (onIrrigationControl) {
      console.log(`📤 Calling onIrrigationControl...`)
      onIrrigationControl(plantId, action)
    } else {
      console.log(`❌ onIrrigationControl not provided`)
    }
  }

  const getMoistureColor = (value: number) => {
    if (value < 30) return "bg-red-500"
    if (value < 50) return "bg-yellow-500"
    return "bg-green-500"
  }

  const getGridClasses = () => {
    if (plants.length === 1) {
      return "flex justify-center"
    }
    if (plants.length === 2) {
      return "flex justify-center gap-4 sm:gap-6 flex-wrap"
    }
    return "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4 sm:gap-6"
  }

  return (
    <div className={getGridClasses()}>
      {plants.map((plant) => {
        return (
          <Card key={plant.id} className="overflow-hidden w-full max-w-sm">
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
              </div>
            </CardHeader>

            <CardContent className="space-y-3 sm:space-y-4">
              <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <Droplets className="h-4 w-4 text-blue-600 flex-shrink-0" />
                  <span className="text-xs sm:text-sm font-medium">Irrigazione</span>
                  {plant.isWatering && <span className="text-xs text-blue-600 font-medium">ATTIVA</span>}
                </div>
                <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                  <Button
                    size="sm"
                    variant={plant.isWatering ? "destructive" : "default"}
                    onClick={() => handleManualControl(plant.id, plant.isWatering ? "stop" : "start")}
                    className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                  >
                    {plant.isWatering ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                  </Button>
                </div>
                
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Droplets className="h-4 w-4 text-cyan-500 flex-shrink-0" />
                  <span className="text-sm font-medium">Umidità del Terreno</span>
                </div>
                <Progress
                  value={plant.soilMoisture}
                  className="h-3"
                  style={
                    {
                      "--progress-background": getMoistureColor(plant.soilMoisture),
                    } as React.CSSProperties
                  }
                />
                <p className="text-sm text-gray-600 dark:text-gray-400">{plant.soilMoisture.toFixed(1)}%</p>
              </div>

              <div className="text-xs text-gray-600 dark:text-gray-400 text-center pt-2 border-t">
                Ultima irrigazione: {plant.lastWatered}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
