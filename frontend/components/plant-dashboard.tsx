"use client"

import type React from "react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Droplets, Leaf, Play, Pause, ChevronDown, ChevronUp } from "lucide-react"
import Image from "next/image"
import { useState, useEffect } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

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

interface PlantCardProps {
  plant: Plant
  onIrrigationControl?: (plantId: string, action: "start" | "stop") => void
}

// Componente per gestire le immagini delle piante con fallback
function PlantImage({ plantType, plantName }: { plantType: string; plantName: string }) {
  const [currentImage, setCurrentImage] = useState<string>('')
  const [imageError, setImageError] = useState(false)

  // Funzione per ottenere l'immagine della pianta basata sul tipo
  const getPlantImage = (plantType: string): string => {
    const type = plantType.toLowerCase()
    
    // Cerca prima PNG, poi JPG come fallback
    return `/plant-images/${type}.png`
  }

  // Inizializza l'immagine corrente
  useEffect(() => {
    setCurrentImage(getPlantImage(plantType))
    setImageError(false)
  }, [plantType])

  const handleImageError = () => {
    if (!imageError) {
      setImageError(true)
      // Prova fallback con PNG se JPG fallisce
      if (currentImage.endsWith('.jpg')) {
        setCurrentImage(currentImage.replace('.jpg', '.png'))
      } else if (currentImage.endsWith('.png')) {
        // Se anche PNG fallisce, usa immagine generica
        setCurrentImage('/plant-images/plant.jpg')
      }
    }
  }

  return (
    <div className="w-24 h-24 sm:w-28 sm:h-28 md:w-32 md:h-32 lg:w-36 lg:h-36 xl:w-40 xl:h-40 relative">
      <Image
        src={currentImage}
        alt={`${plantName} - ${plantType}`}
        fill
        className="object-contain rounded-lg"
        onError={handleImageError}
        priority={true}
      />
    </div>
  )
}

// Componente per il grafico umidità integrato
function HumidityChart({ plantId }: { plantId: string }) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/plants/${plantId}/sensors/humidity/history?hours=24`)
        if (response.ok) {
          const result = await response.json()
          if (result.success && result.data) {
            const chartData = result.data.map((point: any) => ({
              time: point.time_formatted,
              humidity: point.value,
              timestamp: point.timestamp
            }))
            setData(chartData)
          }
        }
      } catch (error) {
        console.error('Errore fetch dati umidità:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [plantId])

  if (loading) {
    return (
      <div className="h-32 flex items-center justify-center">
        <div className="text-gray-500 text-sm">Caricamento...</div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-32 flex items-center justify-center">
        <div className="text-gray-500 text-sm">Nessun dato disponibile</div>
      </div>
    )
  }

  return (
    <div className="h-20 sm:h-24 md:h-28 lg:h-32">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 8 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            domain={[0, 100]}
            tick={{ fontSize: 8 }}
          />
          <Tooltip 
            formatter={(value: any) => [`${value.toFixed(1)}%`, 'Umidità']}
            labelFormatter={(label) => `Ora: ${label}`}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '10px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="humidity" 
            stroke="#3b82f6" 
            strokeWidth={1.5}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

// Componente per la singola card pianta
function PlantCard({ plant, onIrrigationControl }: PlantCardProps) {
  const [showChart, setShowChart] = useState(false)

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

  return (
    <Card className="overflow-hidden w-full h-full flex flex-col">
      <CardHeader className="pb-3 flex-shrink-0">
        <div className="flex items-center gap-3">
          {/* Immagine della pianta a sinistra */}
          <div className="flex-shrink-0">
            <PlantImage plantType={plant.type} plantName={plant.name} />
          </div>
          
          {/* Nome e specie a destra */}
          <div className="min-w-0 flex-1">
            <CardTitle className="text-sm sm:text-base lg:text-lg truncate">{plant.name}</CardTitle>
            <CardDescription className="text-xs sm:text-sm truncate">{plant.type}</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-2 sm:space-y-3 flex-1 flex flex-col">
        <div className="flex items-center justify-between p-2 sm:p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <Droplets className="h-3 w-3 sm:h-4 sm:w-4 text-blue-600 flex-shrink-0" />
            <span className="text-xs sm:text-sm font-medium">Irrigazione</span>
            {plant.isWatering && <span className="text-xs text-blue-600 font-medium">ATTIVA</span>}
          </div>
          <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
            <Button
              size="sm"
              variant={plant.isWatering ? "destructive" : "default"}
              onClick={() => handleManualControl(plant.id, plant.isWatering ? "stop" : "start")}
              className="h-6 w-6 sm:h-7 sm:w-7 lg:h-8 lg:w-8 p-0"
            >
              {plant.isWatering ? <Pause className="h-2 w-2 sm:h-3 sm:w-3" /> : <Play className="h-2 w-2 sm:h-3 sm:w-3" />}
            </Button>
          </div>
        </div>

        <div className="space-y-1 sm:space-y-2">
          <div className="flex items-center gap-2">
            <Droplets className="h-3 w-3 sm:h-4 sm:w-4 text-cyan-500 flex-shrink-0" />
            <span className="text-xs sm:text-sm font-medium">Umidità</span>
          </div>
          <Progress
            value={plant.soilMoisture}
            className="h-2 sm:h-3"
            style={
              {
                "--progress-background": getMoistureColor(plant.soilMoisture),
              } as React.CSSProperties
            }
          />
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">{plant.soilMoisture.toFixed(1)}%</p>
        </div>

        {/* Grafico umidità integrato nella card */}
        <div className="space-y-1 sm:space-y-2 flex-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Droplets className="h-3 w-3 sm:h-4 sm:w-4 text-blue-500 flex-shrink-0" />
              <span className="text-xs sm:text-sm font-medium">Andamento Umidità</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-5 w-5 sm:h-6 sm:w-6 p-0"
              onClick={() => setShowChart(!showChart)}
            >
              {showChart ? <ChevronUp className="h-3 w-3 sm:h-4 sm:w-4" /> : <ChevronDown className="h-3 w-3 sm:h-4 sm:w-4" />}
            </Button>
          </div>
          {showChart && <HumidityChart plantId={plant.id} />}
        </div>

        <div className="text-xs text-gray-600 dark:text-gray-400 text-center pt-1 sm:pt-2 border-t flex-shrink-0">
          Ultima irrigazione: {plant.lastWatered}
        </div>
      </CardContent>
    </Card>
  )
}

export function PlantDashboard({ plants, setPlantsData, onIrrigationControl }: PlantDashboardProps) {
  const getGridClasses = () => {
    if (plants.length === 1) {
      return "flex justify-center max-w-sm mx-auto"
    }
    if (plants.length === 2) {
      return "grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 max-w-4xl mx-auto"
    }
    return "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4 lg:gap-6"
  }

  return (
    <div className={getGridClasses()}>
      {plants.map((plant) => (
        <PlantCard 
          key={plant.id} 
          plant={plant} 
          onIrrigationControl={onIrrigationControl}
        />
      ))}
    </div>
  )
}