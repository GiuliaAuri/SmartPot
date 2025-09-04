"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Settings, Droplets, Thermometer, Sun, Clock, Save, RotateCcw } from "lucide-react"

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

interface PlantConfigurationProps {
  plants: Plant[]
  setPlantsData: (plants: Plant[]) => void
}

interface IrrigationPolicy {
  id: number
  plantId: number
  minMoisture: number
  maxMoisture: number
  minTemperature: number
  maxTemperature: number
  minLight: number
  maxWateringTime: number
  autoMode: boolean
  schedule: string[]
}

export function PlantConfiguration({ plants, setPlantsData }: PlantConfigurationProps) {
  const [selectedPlant, setSelectedPlant] = useState(plants[0]?.id || 1)
  const [policies, setPolicies] = useState<IrrigationPolicy[]>([
    {
      id: 1,
      plantId: 1,
      minMoisture: 40,
      maxMoisture: 70,
      minTemperature: 18,
      maxTemperature: 28,
      minLight: 60,
      maxWateringTime: 300,
      autoMode: true,
      schedule: ["08:00", "18:00"],
    },
    {
      id: 2,
      plantId: 2,
      minMoisture: 50,
      maxMoisture: 80,
      minTemperature: 20,
      maxTemperature: 30,
      minLight: 80,
      maxWateringTime: 600,
      autoMode: true,
      schedule: ["07:00", "19:00"],
    },
    {
      id: 3,
      plantId: 3,
      minMoisture: 60,
      maxMoisture: 85,
      minTemperature: 16,
      maxTemperature: 24,
      minLight: 40,
      maxWateringTime: 180,
      autoMode: false,
      schedule: ["09:00"],
    },
  ])

  const selectedPlantData = plants.find((p) => p.id === selectedPlant)
  const currentPolicy = policies.find((p) => p.plantId === selectedPlant)

  const updatePolicy = (updates: Partial<IrrigationPolicy>) => {
    setPolicies((prev) => prev.map((policy) => (policy.plantId === selectedPlant ? { ...policy, ...updates } : policy)))
  }

  const saveConfiguration = () => {
    // Simula il salvataggio della configurazione
    alert("Configurazione salvata con successo!")
  }

  const resetToDefaults = () => {
    if (currentPolicy) {
      const defaults = {
        minMoisture: 40,
        maxMoisture: 70,
        minTemperature: 18,
        maxTemperature: 28,
        minLight: 60,
        maxWateringTime: 300,
        autoMode: true,
        schedule: ["08:00", "18:00"],
      }
      updatePolicy(defaults)
    }
  }

  if (!selectedPlantData || !currentPolicy) return null

  return (
    <div className="space-y-6">
      {/* Selezione Pianta */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Configurazione Piante
          </CardTitle>
          <CardDescription>Configura le policy di irrigazione e i parametri per ogni pianta</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {plants.map((plant) => (
              <Badge
                key={plant.id}
                variant={selectedPlant === plant.id ? "default" : "outline"}
                className="cursor-pointer px-3 py-1"
                onClick={() => setSelectedPlant(plant.id)}
              >
                {plant.name} ({plant.type})
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Configurazione */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Informazioni Pianta */}
        <Card>
          <CardHeader>
            <CardTitle>Informazioni Pianta</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="plant-name">Nome</Label>
              <Input
                id="plant-name"
                value={selectedPlantData.name}
                onChange={(e) => {
                  setPlantsData(plants.map((p) => (p.id === selectedPlant ? { ...p, name: e.target.value } : p)))
                }}
              />
            </div>

            <div>
              <Label htmlFor="plant-type">Tipo</Label>
              <Select
                value={selectedPlantData.type}
                onValueChange={(value) => {
                  setPlantsData(plants.map((p) => (p.id === selectedPlant ? { ...p, type: value } : p)))
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Erba aromatica">Erba aromatica</SelectItem>
                  <SelectItem value="Ortaggio">Ortaggio</SelectItem>
                  <SelectItem value="Fiore">Fiore</SelectItem>
                  <SelectItem value="Pianta grassa">Pianta grassa</SelectItem>
                  <SelectItem value="Albero da frutto">Albero da frutto</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="auto-mode">Modalità Automatica</Label>
              <Switch
                id="auto-mode"
                checked={currentPolicy.autoMode}
                onCheckedChange={(checked) => updatePolicy({ autoMode: checked })}
              />
            </div>
          </CardContent>
        </Card>

        {/* Policy di Irrigazione */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Policy di Irrigazione</CardTitle>
            <CardDescription>Configura i parametri per l'irrigazione automatica</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="moisture" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="moisture">Umidità</TabsTrigger>
                <TabsTrigger value="temperature">Temperatura</TabsTrigger>
                <TabsTrigger value="light">Luminosità</TabsTrigger>
                <TabsTrigger value="timing">Timing</TabsTrigger>
              </TabsList>

              <TabsContent value="moisture" className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Droplets className="h-4 w-4 text-blue-500" />
                    <Label>Umidità Minima: {currentPolicy.minMoisture}%</Label>
                  </div>
                  <Slider
                    value={[currentPolicy.minMoisture]}
                    onValueChange={([value]) => updatePolicy({ minMoisture: value })}
                    max={100}
                    step={5}
                    className="w-full"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Droplets className="h-4 w-4 text-blue-500" />
                    <Label>Umidità Massima: {currentPolicy.maxMoisture}%</Label>
                  </div>
                  <Slider
                    value={[currentPolicy.maxMoisture]}
                    onValueChange={([value]) => updatePolicy({ maxMoisture: value })}
                    max={100}
                    step={5}
                    className="w-full"
                  />
                </div>

                <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    L'irrigazione si attiva quando l'umidità scende sotto {currentPolicy.minMoisture}% e si ferma quando
                    raggiunge {currentPolicy.maxMoisture}%
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="temperature" className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Thermometer className="h-4 w-4 text-red-500" />
                    <Label>Temperatura Minima: {currentPolicy.minTemperature}°C</Label>
                  </div>
                  <Slider
                    value={[currentPolicy.minTemperature]}
                    onValueChange={([value]) => updatePolicy({ minTemperature: value })}
                    min={0}
                    max={40}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Thermometer className="h-4 w-4 text-red-500" />
                    <Label>Temperatura Massima: {currentPolicy.maxTemperature}°C</Label>
                  </div>
                  <Slider
                    value={[currentPolicy.maxTemperature]}
                    onValueChange={([value]) => updatePolicy({ maxTemperature: value })}
                    min={0}
                    max={40}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div className="p-3 bg-red-50 dark:bg-red-950 rounded-lg">
                  <p className="text-sm text-red-700 dark:text-red-300">
                    L'irrigazione è più frequente quando la temperatura è tra {currentPolicy.minTemperature}°C e{" "}
                    {currentPolicy.maxTemperature}°C
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="light" className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Sun className="h-4 w-4 text-yellow-500" />
                    <Label>Luminosità Minima: {currentPolicy.minLight}%</Label>
                  </div>
                  <Slider
                    value={[currentPolicy.minLight]}
                    onValueChange={([value]) => updatePolicy({ minLight: value })}
                    max={100}
                    step={5}
                    className="w-full"
                  />
                </div>

                <div className="p-3 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">
                    L'irrigazione si attiva solo se la luminosità è superiore al {currentPolicy.minLight}%
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="timing" className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-purple-500" />
                    <Label>Tempo Massimo Irrigazione: {currentPolicy.maxWateringTime}s</Label>
                  </div>
                  <Slider
                    value={[currentPolicy.maxWateringTime]}
                    onValueChange={([value]) => updatePolicy({ maxWateringTime: value })}
                    min={60}
                    max={1800}
                    step={30}
                    className="w-full"
                  />
                </div>

                <div>
                  <Label>Orari Programmati</Label>
                  <div className="flex gap-2 mt-2">
                    {currentPolicy.schedule.map((time, index) => (
                      <Input
                        key={index}
                        type="time"
                        value={time}
                        onChange={(e) => {
                          const newSchedule = [...currentPolicy.schedule]
                          newSchedule[index] = e.target.value
                          updatePolicy({ schedule: newSchedule })
                        }}
                        className="w-32"
                      />
                    ))}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        updatePolicy({
                          schedule: [...currentPolicy.schedule, "12:00"],
                        })
                      }}
                    >
                      +
                    </Button>
                  </div>
                </div>

                <div className="p-3 bg-purple-50 dark:bg-purple-950 rounded-lg">
                  <p className="text-sm text-purple-700 dark:text-purple-300">
                    L'irrigazione si ferma automaticamente dopo {currentPolicy.maxWateringTime} secondi
                  </p>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Azioni */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-3">
            <Button onClick={saveConfiguration} className="flex items-center gap-2">
              <Save className="h-4 w-4" />
              Salva Configurazione
            </Button>
            <Button variant="outline" onClick={resetToDefaults} className="flex items-center gap-2 bg-transparent">
              <RotateCcw className="h-4 w-4" />
              Ripristina Default
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
