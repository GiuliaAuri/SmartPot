"use client"

import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Droplets, TrendingUp } from 'lucide-react'

interface HumidityDataPoint {
  timestamp: number
  value: number
  time_formatted: string
  hour: number
  minute: number
}

interface HumidityChartProps {
  plantId: string
  plantName: string
}

interface ChartData {
  time: string
  humidity: number
  timestamp: number
}

export function HumidityChart({ plantId, plantName }: HumidityChartProps) {
  const [data, setData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hours, setHours] = useState(24)

  const fetchHumidityData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`http://localhost:5000/api/plants/${plantId}/sensors/humidity/history?hours=${hours}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success && result.data) {
        // Trasforma i dati per il grafico
        const chartData: ChartData[] = result.data.map((point: HumidityDataPoint) => ({
          time: point.time_formatted,
          humidity: point.value,
          timestamp: point.timestamp
        }))
        
        setData(chartData)
      } else {
        throw new Error(result.error || 'Errore nel recupero dei dati')
      }
    } catch (err) {
      console.error('Errore fetch dati umidità:', err)
      setError(err instanceof Error ? err.message : 'Errore sconosciuto')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHumidityData()
  }, [plantId, hours])

  const formatTooltipValue = (value: number) => {
    return `${value.toFixed(1)}%`
  }

  const formatTooltipLabel = (label: string) => {
    return `Ora: ${label}`
  }

  const getLastIrrigationTime = () => {
    // Per ora restituiamo un valore di esempio
    // In futuro potremmo recuperare questo dato dall'API
    return "2 ore fa"
  }

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Andamento Umidità
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Caricamento dati...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-red-600" />
            Andamento Umidità
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="text-red-500">Errore: {error}</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-gray-600" />
            Andamento Umidità
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Nessun dato disponibile</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-600" />
          Andamento Umidità
        </CardTitle>
        <div className="flex gap-2">
          <button
            onClick={() => setHours(24)}
            className={`px-3 py-1 text-sm rounded ${
              hours === 24 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            24h
          </button>
          <button
            onClick={() => setHours(168)}
            className={`px-3 py-1 text-sm rounded ${
              hours === 168 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            7gg
          </button>
        </div>
      </CardHeader>
      <CardContent>
        <div style={{ width: '100%' }}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              width={500}
              height={300}
              data={data}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis 
                domain={[0, 100]}
                tick={{ fontSize: 12 }}
                label={{ value: 'Umidità (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                formatter={(value: any) => [formatTooltipValue(value), 'Umidità']}
                labelFormatter={formatTooltipLabel}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="humidity" 
                stroke="#3b82f6" 
                strokeWidth={2}
                activeDot={{ r: 6, fill: '#3b82f6' }}
                dot={{ r: 3, fill: '#3b82f6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="text-center text-sm text-gray-500 mt-2">
          Ultima irrigazione: {getLastIrrigationTime()}
        </div>
      </CardContent>
    </Card>
  )
}
