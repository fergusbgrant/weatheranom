import React from 'react'

const ForecastList = ({forecast}) => {
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