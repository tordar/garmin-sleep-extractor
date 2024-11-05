'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import SleepChart from '../components/SleepChart'

interface SleepData {
    date: string
    sleep_time: number
    awake_time: number
}

interface ApiResponse {
    sleep_data: SleepData[]
    avg_sleep_time: number
}

export default function Home() {
    const [sleepData, setSleepData] = useState<SleepData[]>([])
    const [avgSleepTime, setAvgSleepTime] = useState<number>(0)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetch('/api/sleep-data')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch sleep data')
                }
                return response.json()
            })
            .then((data: ApiResponse) => {
                setSleepData(data.sleep_data)
                if (data.sleep_data.length > 0) {
                    const totalSleep = data.sleep_data.reduce((sum, day) => sum + day.sleep_time, 0)
                    const average = totalSleep / data.sleep_data.length
                    setAvgSleepTime(average)
                } else {
                    setAvgSleepTime(null)
                }
                setIsLoading(false)
            })
            .catch(err => {
                console.error('Error fetching sleep data:', err)
                setError('Failed to load sleep data. Please try again later.')
                setIsLoading(false)
            })
    }, [])
    
    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <Card className="w-full max-w-4xl">
                <CardHeader>
                    <CardTitle className="text-3xl font-bold text-primary">Garmin Sleep Dashboard</CardTitle>
                    <CardDescription className="text-lg text-muted-foreground">Daily sleep and awake time</CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <p className="text-center">Loading sleep data...</p>
                    ) : error ? (
                        <p className="text-center text-red-500">{error}</p>
                    ) : (
                        <>
                            <SleepChart sleepData={sleepData} />
                            <div className="mt-6 text-center">
                                <p className="text-xl font-semibold text-primary">
                                    Average Sleep Time: {avgSleepTime !== null ? avgSleepTime.toFixed(2) : 'N/A'} hours
                                </p>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}