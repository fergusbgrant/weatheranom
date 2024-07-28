import React, { useState, useEffect } from 'react'

function App() {
  
  const [data, setData] = useState([{}])

  useEffect (() => {
    fetch('https://75ny89k623.execute-api.eu-central-1.amazonaws.com/dev').then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data)
      }
    )
  }, [])

  return (
    <div>App</div>
  )
}

export default App
