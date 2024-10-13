import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const ForecastList = () => {
    const [forecast, setForecast] = useState([])
    const navigate = useNavigate()

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        const response = await fetch('/all', {
                                    method: "GET",
                                    headers: {"Content-Type": "application/json"}
                                })
        const data  = await response.json()
        if (data.body === 'Login required') {
            navigate('../login')
        }
        setForecast(data.body)
    }

    return <div>
        <h2>Forecast</h2>
        <table>
            <thead>
                <tr>
                    <th>City</th>
                    <th>Country</th>
                    <th>Hist Avg</th>
                    <th>Forecast Avg</th>
                    <th>Discrepancy</th>
                </tr>
            </thead>
            <tbody>
                {
                    forecast.map((entry) => 
                        <tr key={entry.city}>
                            <td>{entry.city}</td>
                            <td>{entry.country}</td>
                            <td>{entry.historical}</td>
                            <td>{entry.forecast}</td>
                            <td>{entry.discrepancy}</td>
                        </tr>
                    )
                }
            </tbody>
        </table>
    </div>
}

export default ForecastList