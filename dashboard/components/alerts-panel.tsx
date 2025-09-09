"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { AlertTriangle, AlertCircle, Info, CheckCircle, X, Bell, BellOff, Trash2 } from "lucide-react"

/**
 * Interfaccia per rappresentare un singolo alert.
 */
interface AlertItem {
  id: number
  type: "info" | "warning" | "critical"
  plantName: string
  message: string
  timestamp: string
}

/**
 * Interfaccia per rappresentare le props del componente AlertsPanel.
 */
interface AlertsPanelProps {
  alerts: AlertItem[]
  setAlerts: (alerts: AlertItem[]) => void
}

/**
 * Componente per la gestione degli avvisi.
 * 
 * Questo componente permette di gestire gli avvisi attivi e di configurare
 * le impostazioni per la gestione degli avvisi.
 * 
 * @param alerts - Array di oggetti AlertItem
 * @param setAlerts - Funzione per impostare gli avvisi
 * @returns JSX.Element - Il componente AlertsPanel
 */
export function AlertsPanel({ alerts, setAlerts }: AlertsPanelProps) {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)
  const [autoResolve, setAutoResolve] = useState(true)

  /**
   * Funzione per ottenere l'icona dell'alert in base al tipo.
   * 
   * @param type - Tipo dell'alert
   * @returns JSX.Element - L'icona dell'alert
   */
  const getAlertIcon = (type: string) => {
    switch (type) {
      case "critical":
        return <AlertTriangle className="h-4 w-4" />
      case "warning":
        return <AlertCircle className="h-4 w-4" />
      case "info":
        return <Info className="h-4 w-4" />
      default:
        return <Info className="h-4 w-4" />
    }
  }

  /**
   * Funzione per ottenere il colore dell'alert in base al tipo.
   * 
   * @param type - Tipo dell'alert
   * @returns Stringa con il colore dell'alert
   */
  const getAlertColor = (type: string) => {
    switch (type) {
      case "critical":
        return "border-red-200 bg-red-50 dark:bg-red-950"
      case "warning":
        return "border-yellow-200 bg-yellow-50 dark:bg-yellow-950"
      case "info":
        return "border-blue-200 bg-blue-50 dark:bg-blue-950"
      default:
        return "border-gray-200 bg-gray-50 dark:bg-gray-950"
    }
  }

  /**
   * Funzione per ottenere il colore del testo dell'alert in base al tipo.
   * 
   * @param type - Tipo dell'alert
   * @returns Stringa con il colore del testo dell'alert
   */
  const getAlertTextColor = (type: string) => {
    switch (type) {
      case "critical":
        return "text-red-700 dark:text-red-300"
      case "warning":
        return "text-yellow-700 dark:text-yellow-300"
      case "info":
        return "text-blue-700 dark:text-blue-300"
      default:
        return "text-gray-700 dark:text-gray-300"
    }
  }

  /**
   * Funzione per eliminare un alert.
   * 
   * @param alertId - ID dell'alert da eliminare
   */
  const dismissAlert = (alertId: number) => {
    setAlerts(alerts.filter((alert) => alert.id !== alertId))
  }

  /**
   * Funzione per eliminare tutti gli alert.
   */
  const clearAllAlerts = () => {
    setAlerts([])
  }

  /**
   * Funzione per marcare un alert come risolto.
   * 
   * @param alertId - ID dell'alert da marcare come risolto
   */
  const markAsResolved = (alertId: number) => {
    // In un'implementazione reale, questo potrebbe cambiare lo stato dell'alert
    dismissAlert(alertId)
  }

  return (
    <div className="space-y-6">
      {/* Impostazioni Notifiche */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Gestione Avvisi
          </CardTitle>
          <CardDescription>Configura le impostazioni per gli avvisi e le notifiche</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {notificationsEnabled ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
              <Label htmlFor="notifications">Notifiche Push</Label>
            </div>
            <Switch id="notifications" checked={notificationsEnabled} onCheckedChange={setNotificationsEnabled} />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              <Label htmlFor="auto-resolve">Risoluzione Automatica</Label>
            </div>
            <Switch id="auto-resolve" checked={autoResolve} onCheckedChange={setAutoResolve} />
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={clearAllAlerts}
              className="flex items-center gap-2 bg-transparent"
            >
              <Trash2 className="h-4 w-4" />
              Cancella Tutti
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Lista Avvisi */}
      <Card>
        <CardHeader>
          <CardTitle>Avvisi Attivi</CardTitle>
          <CardDescription>
            {alerts.length === 0 ? "Nessun avviso attivo" : `${alerts.length} avvisi attivi`}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {alerts.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
              <p className="text-gray-600 dark:text-gray-400">
                Tutto funziona correttamente! Nessun avviso da mostrare.
              </p>
            </div>
          ) : (
            alerts.map((alert) => (
              <Alert key={alert.id} className={getAlertColor(alert.type)}>
                <div className="flex items-start gap-4 w-full">
                  <div className={`${getAlertTextColor(alert.type)} flex-shrink-0 mt-1`}>
                    {getAlertIcon(alert.type)}
                  </div>
                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <AlertTitle className={`${getAlertTextColor(alert.type)} font-semibold mb-1`}>
                          Pianta: {alert.plantName}
                        </AlertTitle>
                        <AlertDescription className={`${getAlertTextColor(alert.type)} text-sm leading-relaxed`}>
                          {alert.message}
                        </AlertDescription>
                      </div>
                      <Badge
                        variant={alert.type === "critical" ? "destructive" : "secondary"}
                        className="text-xs flex-shrink-0 ml-2"
                      >
                        {alert.type === "critical" ? "Critico" : alert.type === "warning" ? "Avviso" : "Info"}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between pt-2">
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => markAsResolved(alert.id)}
                          className="h-8 px-3 hover:bg-green-100 dark:hover:bg-green-900 text-xs"
                          title="Risolvi"
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Risolvi
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => dismissAlert(alert.id)}
                          className="h-8 px-3 hover:bg-red-100 dark:hover:bg-red-900 text-xs"
                          title="Elimina"
                        >
                          <X className="h-4 w-4 mr-1" />
                          Elimina
                        </Button>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{alert.timestamp}</p>
                    </div>
                  </div>
                </div>
              </Alert>
            ))
          )}
        </CardContent>
      </Card>

      {/* Regole Avvisi */}
      <Card>
        <CardHeader>
          <CardTitle>Regole di Avviso</CardTitle>
          <CardDescription>Configurazione automatica degli avvisi basata sui sensori</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3 border rounded-lg">
              <h4 className="font-medium mb-2">Livello Acqua Basso</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Avviso quando il livello dell&apos;acqua scende sotto il 30%
              </p>
            </div>

            <div className="p-3 border rounded-lg">
              <h4 className="font-medium mb-2">Batteria Scarica</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Avviso critico quando la batteria scende sotto il 25%
              </p>
            </div>

            <div className="p-3 border rounded-lg">
              <h4 className="font-medium mb-2">Umidità Critica</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Avviso quando l&apos;umidità del terreno è troppo bassa
              </p>
            </div>

            <div className="p-3 border rounded-lg">
              <h4 className="font-medium mb-2">Temperatura Anomala</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Avviso per temperature fuori dal range ottimale
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
