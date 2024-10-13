import React from 'react'
import ForecastList from './ForecastList'
import 'bootstrap/dist/css/bootstrap.min.css'
import { BrowserRouter, Routes, Route, Navlink } from 'react-router-dom'

// Pages
import Login from './pages/Login'

function App() {

  return (
    <BrowserRouter>
      <main>
        <Routes>
          <Route path='allcities' element={<ForecastList />} />
          <Route path='login' element={<Login />} />
        </Routes>
      </main>
    </BrowserRouter>
  )

  /*<div>
  <Button>Hello, button</Button>
  <ForecastList forecast={forecast} />
</div>*/

}

export default App
