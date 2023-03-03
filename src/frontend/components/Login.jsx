import React from 'react'
import image from '../../assets/login-left-modal.png'

/* Styling Imports */

const Login = () => {
  return (
    <div className = "window-login">
        <div className = "overall-modal">
          <div className = "modal-left">
            <img src = {image}></img>
          </div>
          <div className = "modal-right">

          </div>
        </div>
    </div>
  )
}

export default Login