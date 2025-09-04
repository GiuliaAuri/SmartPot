"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { AlertTriangle, AlertCircle, Info, CheckCircle, X, Bell, BellOff, Trash2 } from "lucide-react"

interface AlertItem {
  id: number
  type: "info" | "warning" | "critical"
  plantName: string
  message: string
  timestamp: string
}

interface AlertsPanelProps {
  alerts: AlertItem[]
  setAlerts: (alerts: AlertItem[]) => void
}

export function AlertsPanel({ alerts, setAlerts }: AlertsPanelProps) {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)
  const [autoResolve, setAutoResolve] = useState(true)

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

  const dismissAlert = (alertId: number) => {
    setAlerts(alerts.filter((alert) => alert.id !== alertId))
  }

  const clearAllAlerts = () => {
    setAlerts([])
  }

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
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className={`${getAlertTextColor(alert.type)} flex-shrink-0`}>{getAlertIcon(alert.type)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <AlertTitle className={`${getAlertTextColor(alert.type)} truncate`}>
                          {alert.plantName}
                        </AlertTitle>
                        <Badge
                          variant={alert.type === "critical" ? "destructive" : "secondary"}
                          className="text-xs ml-2 flex-shrink-0"
                        >
                          {alert.type === "critical" ? "Critico" : alert.type === "warning" ? "Avviso" : "Info"}
                        </Badge>
                      </div>
                      <AlertDescription className={`${getAlertTextColor(alert.type)} text-sm leading-relaxed`}>
                        {alert.message}
                      </AlertDescription>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">{alert.timestamp}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 ml-3 flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => markAsResolved(alert.id)}
                      className="h-8 w-8 p-0 hover:bg-green-100 dark:hover:bg-green-900"
                      title="Risolvi"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => dismissAlert(alert.id)}
                      className="h-8 w-8 p-0 hover:bg-red-100 dark:hover:bg-red-900"
                      title="Elimina"
                    >
                      <X className="h-4 w-4" />
                    </Button>
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
                Avviso quando il livello dell'acqua scende sotto il 30%
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
                Avviso quando l'umidità del terreno è troppo bassa
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
