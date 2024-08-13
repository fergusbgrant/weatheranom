import Button from 'react-bootstrap/Button'
import React, { useState, useEffect } from 'react'
import ForecastList from './ForecastList'
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {
  
  const [forecast, setForecast] = useState([])

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    const response = await fetch('https://75ny89k623.execute-api.eu-central-1.amazonaws.com/dev')
    const data  = await response.json()
    setForecast(data.body)
    console.log(data.body)
  }

  return (
    <div>
      <Button>Hello, button</Button>
      <ForecastList forecast={forecast} />
    </div>
  )

}

export default App
