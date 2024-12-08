import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const LoginForm = ({}) => {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const navigate = useNavigate()

    const onSubmit = async (e) => {
        e.preventDefault()
        const data = {
            username,
            password
        }
        const path = "https://75ny89k623.execute-api.eu-central-1.amazonaws.com/dev/login"
        const options = {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: 'include',
            body: JSON.stringify(data)
        }
        const response = await fetch(path, options)
        if (response.status !== 201 && response.status !== 200) {
            const data = await response.json()
            alert(data.body)
        } else {
            navigate('../allcities')
        }

    }

    return (
        <form onSubmit={onSubmit}>
            <div>
                <label htmlFor="username">Username:</label>
                <input 
                    type="text" 
                    id="username" 
                    value={username} 
                    onChange={(e) => setUsername(e.target.value)}
                />
            </div>
            <div>
                <label htmlFor="password">Password:</label>
                <input 
                    type="password" 
                    id="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)}
                />
            </div>
            <button type="submit">Login</button>
        </form>
    )
}

export default LoginForm