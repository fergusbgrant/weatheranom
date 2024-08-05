import React, { useState, useEffect } from 'react'
import ForecastList from './ForecastList'

function App() {
  
  const [forecast, setForecast] = useState([{}])

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    const response = await fetch('https://75ny89k623.execute-api.eu-central-1.amazonaws.com/dev')
    const data  = await response.json()
    setForecast(data.body)
    console.log(data.body)
  }

  /*useEffect (() => {
    fetch('https://75ny89k623.execute-api.eu-central-1.amazonaws.com/dev').then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data)
      }
    )
  }, [])*/



  return (
    <ForecastList forecast={forecast} />
  )
}

export default App
