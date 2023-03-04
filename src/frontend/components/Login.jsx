import React from 'react'
import image from '../../assets/login-left-modal.png'

import '../styling/Login.css'

/* Styling Imports */

const Login = () => {
  return (
    <div className = "window-login">
      <div className = "window-header">

      </div>

      <div className = "window-main">
        <div className = "overall-modal">
            <div className = "modal-left">
              <div className = "modal-left-top">

                <p className = "text1">The world's best computer science grading tool. </p>

              </div>

              <div className = "modal-left-bottom">
                <img className = "image1" src = {image}></img>
              </div>

            </div>
            <div className = "modal-right">
              <p className = "text2">Sign Up</p>
              <p className = "text3">Have an account already? </p>

              <form className = "sign-up-form">

                <p className = "input-label">I am a...</p>
                <div className = "user-select-outer">
                  <button className = "user-select-button" type = "button" name = "user-type">Student</button>
                  <button className = "user-select-button" type = "button" name = "user-type">Teacher</button>
                  <button className = "user-select-button" type = "button" name = "user-type">TA</button>
                </div>

                <label className = "input-label" for="fname">Full Name</label>
                <input className = "input-field" type="text" id="fname" placeholder = "Enter full name"/>

                <label className = "input-label" for="lname">Email</label>
                <input className = "input-field" type="text" id="lname" placeholder = "Enter email"/>

                <label className = "input-label" for="password">Password</label>
                <input className = "input-field" type="password" id="password" placeholder = "Enter password"/>

                <label className = "input-label" for="password">Institution Name</label>
                <select className = "dropdown-field" placeholder = "Institution">
                  <option value="">University of Maryland College Park</option>
                  <option value="">Middlesex County Academy for SMET</option>
                  <option value="mercedes">JP Stevens High School</option>
                  <option value="audi">Woodbridge Academy</option>
                </select>

                <input className = "input-button" type="submit" value="Create Account"/>
              </form>
              
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login