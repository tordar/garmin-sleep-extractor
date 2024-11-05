'use client'

import { Bar } from 'react-chartjs-2'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js'

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
)

interface SleepData {
    date: string
    sleep_time: number
    awake_time: number
}

interface SleepChartProps {
    sleepData: SleepData[]
}

export default function SleepChart({ sleepData }: SleepChartProps) {
    if (sleepData.length === 0) {
        return <p className="text-center">No sleep data available.</p>
    }

    const chartData = {
        labels: sleepData.map(d => d.date),
        datasets: [
            {
                label: 'Sleep Time',
                data: sleepData.map(d => d.sleep_time),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
            },
            {
                label: 'Awake Time',
                data: sleepData.map(d => d.awake_time),
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
            },
        ],
    }

    const options = {
        responsive: true,
        scales: {
            x: {
                stacked: true,
            },
            y: {
                stacked: true,
                max: 24,
            },
        },
    }

    return (
        <div className="w-full h-[400px]">
            <Bar data={chartData} options={options} />
        </div>
    )
}