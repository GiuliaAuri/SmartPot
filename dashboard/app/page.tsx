"use client"

import { useState, useEffect } from "react"
import { Leaf } from "lucide-react"
import { PlantDashboard } from "@/components/plant-dashboard"
import { apiService, type Plant, type Alert } from "@/lib/api"

export default function SmartPlantDashboard() {
  const [plants, setPlantsData] = useState<Plant[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadPlantsData = async () => {
    try {
      setLoading(true)
      const plantsData = await apiService.getAllPlants()
      setPlantsData(plantsData)
      setError(null)
    } catch (err) {
      console.error("Failed to load plants data:", err)
      setError("Errore nel caricamento dei dati delle piante")
      // Fallback to mock data if API fails
      setPlantsData([
        {
          id: "1",
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
      ])
    } finally {
      setLoading(false)
    }
  }

  const loadAlertsData = async () => {
    try {
      const alertsData = await apiService.getAllAlerts()
      setAlerts(alertsData)
    } catch (err) {
      console.error("Failed to load alerts data:", err)
      // Fallback to empty alerts if API fails
      setAlerts([])
    }
  }

  useEffect(() => {
    loadPlantsData()
    loadAlertsData()

    // Poll for updates every 10 seconds
    const interval = setInterval(() => {
      loadPlantsData()
      loadAlertsData()
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <Leaf className="h-12 w-12 text-green-500 animate-pulse mx-auto mb-4" />
          <p className="text-lg text-gray-600 dark:text-gray-300">Caricamento dati delle piante...</p>
        </div>
      </div>
    )
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
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white text-left">
                  Smart Plants - IoT System
                </h1>
                <p className="text-gray-600 dark:text-gray-300 text-left">
                  Sistema intelligente per la gestione e monitoraggio dei tuoi vasi
                </p>
                {error && <p className="text-red-500 text-sm mt-1">{error} - Usando dati di fallback</p>}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content - Only Dashboard */}
        <PlantDashboard plants={plants} setPlantsData={setPlantsData} alerts={alerts} />
      </div>
    </div>
  )
}
