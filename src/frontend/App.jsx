import { useState } from 'react'
import reactLogo from '../assets/react.svg'
import './App.css'

/* Component Imports */
import Login from './components/Login'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <Login />
    </div>
  )
}

export default App
