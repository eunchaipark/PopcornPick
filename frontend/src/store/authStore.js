import {create} from 'zustand'

const useAuthStore = create((set) => ({
    user: null,
    isLoggedIn: false,
    isInitialized: false,  // ← 추가

    login: (userData, token) => {
        localStorage.setItem('access_token', token)
        set({user: userData, isLoggedIn: true, isInitialized: true})
    },

    logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        set({user: null, isLoggedIn: false, isInitialized: true})
    },

    initAuth: () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
            set({isInitialized: true})
            return
        }
        const user = JSON.parse(localStorage.getItem('user') || 'null')
        if (user) {
            set({user, isLoggedIn: true, isInitialized: true})
        } else {
            set({isInitialized: true})
        }
    },
}))

export default useAuthStore