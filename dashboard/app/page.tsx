"use client"

import { useState, useEffect, useCallback } from "react"
import { Leaf } from "lucide-react"
import { PlantDashboard } from "@/components/plant-dashboard"
import { apiService, type Plant, type Alert } from "@/lib/api"

/**
 * Componente principale del dashboard delle piante intelligenti.
 * 
 * Questo componente gestisce il caricamento e l'aggiornamento dei dati
 * delle piante e degli alert, fornendo un'interfaccia utente completa
 * per il monitoraggio del sistema IoT delle piante.
 * 
 * @returns JSX.Element - Il componente del dashboard principale
 */
export default function SmartPlantDashboard() {
  const [plants, setPlantsData] = useState<Plant[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)
  const [lastRequestTime, setLastRequestTime] = useState<number>(0)
  const [isInitialized, setIsInitialized] = useState(false)

  // Throttle requests to prevent consecutive calls
  /**
   * Funzione per controllare se è possibile effettuare una richiesta API.
   * 
   * Questa funzione controlla se è stato sufficientemente tempo dall'ultima richiesta
   * per evitare richieste consecutive troppo frequenti.
   * 
   * @returns true se la richiesta può essere effettuata, false altrimenti
   */
  const canMakeRequest = useCallback(() => {
    const now = Date.now()
    const timeSinceLastRequest = now - lastRequestTime
    const minInterval = 5000 // Minimum 5 seconds between requests
    
    if (timeSinceLastRequest < minInterval) {
      console.log(`Throttling request - only ${timeSinceLastRequest}ms since last request`)
      return false
    }
    return true
  }, [lastRequestTime])

  /**
   * Funzione per caricare i dati delle piante.
   * 
   * Questa funzione carica i dati delle piante dall'API e aggiorna lo stato locale.
   * 
   * @param isInitialLoad true se è la prima richiesta, false altrimenti
   */
  const loadPlantsData = useCallback(async (isInitialLoad = false) => {
    // Prevent multiple simultaneous requests
    if (isUpdating && !isInitialLoad) {
      console.log('Skipping update - already in progress')
      return
    }
    
    // Throttle requests to prevent consecutive calls
    if (!isInitialLoad && !canMakeRequest()) {
      console.log('Skipping update - request throttled')
      return
    }
    
    try {
      setIsUpdating(true)
      setLastRequestTime(Date.now())
      
      if (isInitialLoad) {
        setLoading(true)
      }
      
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
          type: "basilico",  // Show species instead of generic type
          status: "healthy",
          waterLevel: 75,  // 0.75 liters = 75%
          temperature: 22,
          humidity: 60,
          lightLevel: 65,  // ~39000 lux = 65%
          batteryLevel: 85,
          waterFlow: 0.2,
          isWatering: false,
          lastWatered: "2 ore fa",
        },
      ])
    } finally {
      setLoading(false)
      setIsUpdating(false)
    }
  }, [isUpdating, lastRequestTime, canMakeRequest])

  /**
   * Funzione per caricare i dati degli alert.
   * 
   * Questa funzione carica i dati degli alert dall'API e aggiorna lo stato locale.
   */
  const loadAlertsData = useCallback(async () => {
    // Throttle requests to prevent consecutive calls
    if (!canMakeRequest()) {
      console.log('Skipping alerts update - request throttled')
      return
    }
    
    try {
      setLastRequestTime(Date.now())
      const alertsData = await apiService.getAllAlerts()
      setAlerts(alertsData)
    } catch (err) {
      console.error("Failed to load alerts data:", err)
      // Fallback to empty alerts if API fails
      setAlerts([])
    }
  }, [canMakeRequest])

  /**
   * Effetto per inizializzare e aggiornare i dati delle piante e degli alert.
   * 
   * Questo effetto si occupa di caricare i dati iniziali e di aggiornarli periodicamente.
   */
  useEffect(() => {
    // Prevent multiple initializations
    if (isInitialized) {
      return
    }
    
    console.log('Initializing app...')
    setIsInitialized(true)
    
    loadPlantsData(true) // Initial load
    loadAlertsData()

    // Poll for updates every 60 seconds
    const interval = setInterval(() => {
      console.log('Scheduled update...')
      loadPlantsData(false) // Refresh without loading state
      loadAlertsData()
    }, 60000)

    return () => {
      console.log('Cleaning up interval...')
      clearInterval(interval)
    }
  }, [isInitialized, loadPlantsData, loadAlertsData])

  /**
   * Renderizza un componente di caricamento se i dati non sono ancora stati caricati.
   * 
   * @returns JSX.Element - Il componente di caricamento
   */
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="text-center">
          <Leaf className="h-12 w-12 text-green-500 animate-pulse mx-auto mb-4" />
          <p className="text-lg text-gray-600 dark:text-gray-300">Caricamento dati delle piante...</p>
        </div>
      </div>
    )
  }

  /**
   * Renderizza il componente principale del dashboard.
   * 
   * @returns JSX.Element - Il componente del dashboard principale
   */
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto p-4 sm:p-6 lg:p-8">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <div className="flex justify-center mb-4">
            <div className="flex flex-col sm:flex-row items-center gap-3 text-center sm:text-left">
              <div className="p-2 bg-green-500 rounded-lg flex-shrink-0">
                <Leaf className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white">
                  Smart Plants - IoT System
                </h1>
                  <p className="text-sm sm:text-base text-gray-600 dark:text-gray-300 mt-1">
                    Sistema intelligente per la gestione e monitoraggio dei tuoi vasi
                  </p>
                  {error && <p className="text-red-500 text-xs sm:text-sm mt-1">{error} - Usando dati di fallback</p>}
                  {isUpdating && (
                    <p className="text-blue-500 text-xs sm:text-sm mt-1 flex items-center gap-1">
                      <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      Aggiornamento dati...
                    </p>
                  )}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content - Only Dashboard */}
        <PlantDashboard
          plants={plants}
          setPlantsData={setPlantsData}
          alerts={alerts}
        />
      </div>
    </div>
  )
}
