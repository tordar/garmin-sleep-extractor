import { NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'

export async function GET() {
    try {
        const dataDirectory = path.join(process.cwd(), 'data')
        const fileContents = await fs.readFile(dataDirectory + '/garmin_sleep_data.csv', 'utf8')

        const rows = fileContents.split('\n').slice(1) // Skip header row
        const sleepData = rows
            .filter(row => row.trim() !== '') // Filter out empty rows
            .map(row => {
                const [date, totalSleep, , , , , ,] = row.split(',')
                const sleepTime = parseFloat(totalSleep)
                return {
                    date,
                    sleep_time: sleepTime,
                    awake_time: 24 - sleepTime
                }
            })

        const avgSleepTime = sleepData.length > 0
            ? sleepData.reduce((sum, day) => sum + day.sleep_time, 0) / sleepData.length
            : null

        return NextResponse.json({
            sleep_data: sleepData,
            avg_sleep_time: avgSleepTime
        })
    } catch (error) {
        console.error('Error fetching sleep data:', error)
        return NextResponse.json({ sleep_data: [], avg_sleep_time: null }, { status: 500 })
    }
}