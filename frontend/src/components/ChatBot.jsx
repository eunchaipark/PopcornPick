import { useState, useRef, useEffect } from 'react'
import apiClient from '../api/apiClient'
import useAuthStore from '../store/authStore'
import styles from '../styles/ChatBot.module.css'

const ChatBot = () => {
    const { user, isLoggedIn } = useAuthStore()
    const [isOpen, setIsOpen] = useState(false)
    const [showHistory, setShowHistory] = useState(false)
    const [messages, setMessages] = useState([])
    const [sessions, setSessions] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    // 챗봇 열 때 오늘 대화 자동 로드
    useEffect(() => {
        if (isOpen && user) {
            loadTodaySession()
            loadSessions()
        }
    }, [isOpen])

    if (!isLoggedIn) return null

    const loadTodaySession = async () => {
        try {
            const res = await apiClient.get(`/chat/today/${user.user_id}`)
            if (res.data.session_id) {
                setSessionId(res.data.session_id)
                await loadSessionMessages(res.data.session_id)
            } else {
                // 오늘 대화 없으면 초기 메시지
                setMessages([{
                    role: 'assistant',
                    content: '안녕하세요! 영화 추천 챗봇입니다 🎬\n어떤 영화를 찾고 계신가요?'
                }])
            }
        } catch {
            setMessages([{
                role: 'assistant',
                content: '안녕하세요! 영화 추천 챗봇입니다 🎬\n어떤 영화를 찾고 계신가요?'
            }])
        }
    }

    const loadSessions = async () => {
        try {
            const res = await apiClient.get(`/chat/sessions/${user.user_id}`)
            setSessions(res.data)
        } catch {
            setSessions([])
        }
    }

    const loadSessionMessages = async (sid) => {
        try {
            const res = await apiClient.get(`/chat/history/${sid}`)
            if (res.data.messages.length > 0) {
                setMessages(res.data.messages)
            } else {
                setMessages([{
                    role: 'assistant',
                    content: '안녕하세요! 영화 추천 챗봇입니다 🎬\n어떤 영화를 찾고 계신가요?'
                }])
            }
        } catch {
            setMessages([])
        }
    }

    const handleSelectSession = async (sid) => {
        setSessionId(sid)
        await loadSessionMessages(sid)
        setShowHistory(false)
    }

    const handleNewChat = () => {
        setMessages([{
            role: 'assistant',
            content: '안녕하세요! 영화 추천 챗봇입니다 🎬\n어떤 영화를 찾고 계신가요?'
        }])
        setSessionId(null)
        setShowHistory(false)
    }

    const handleSend = async () => {
        if (!input.trim() || loading) return

        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setLoading(true)

        try {
            const res = await apiClient.post('/chat', {
                user_id:    user.user_id,
                message:    userMessage,
                session_id: sessionId,
            })
            setSessionId(res.data.session_id)
            setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply }])
            // 세션 목록 갱신
            loadSessions()
        } catch {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '죄송해요, 오류가 발생했어요. 다시 시도해주세요.'
            }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    // 날짜별 세션 그룹핑
    const groupedSessions = sessions.reduce((acc, s) => {
        const date = s.date
        if (!acc[date]) acc[date] = []
        acc[date].push(s)
        return acc
    }, {})

    const formatDate = (dateStr) => {
        const today = new Date().toISOString().slice(0, 10)
        const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10)
        if (dateStr === today) return '오늘'
        if (dateStr === yesterday) return '어제'
        return dateStr
    }

    return (
        <>
            {/* 플로팅 버튼 */}
            <button
                className={styles.floatBtn}
                onClick={() => setIsOpen(prev => !prev)}
                aria-label="챗봇 열기"
            >
                {isOpen ? '✕' : '🎬'}
            </button>

            {/* 채팅창 */}
            {isOpen && (
                <div className={styles.chatWindow}>

                    {/* 헤더 */}
                    <div className={styles.header}>
                        <span className={styles.headerTitle}>🎬 영화 추천 챗봇</span>
                        <div className={styles.headerBtns}>
                            <button
                                className={styles.historyBtn}
                                onClick={() => setShowHistory(prev => !prev)}
                            >
                                {showHistory ? '채팅' : '기록'}
                            </button>
                            <button className={styles.resetBtn} onClick={handleNewChat}>
                                새 대화
                            </button>
                        </div>
                    </div>

                    {/* 대화 기록 패널 */}
                    {showHistory ? (
                        <div className={styles.historyPanel}>
                            {Object.keys(groupedSessions).length === 0 ? (
                                <p className={styles.emptyHistory}>대화 기록이 없어요</p>
                            ) : (
                                Object.entries(groupedSessions).map(([date, list]) => (
                                    <div key={date} className={styles.dateGroup}>
                                        <p className={styles.dateLabel}>{formatDate(date)}</p>
                                        {list.map(s => (
                                            <button
                                                key={s.session_id}
                                                className={`${styles.sessionItem} ${s.session_id === sessionId ? styles.activeSession : ''}`}
                                                onClick={() => handleSelectSession(s.session_id)}
                                            >
                                                <span className={styles.sessionPreview}>{s.preview}</span>
                                                <span className={styles.sessionTime}>
                                                    {s.started_at.slice(11, 16)}
                                                </span>
                                            </button>
                                        ))}
                                    </div>
                                ))
                            )}
                        </div>
                    ) : (
                        <>
                            {/* 메시지 목록 */}
                            <div className={styles.messageList}>
                                {messages.map((msg, idx) => (
                                    <div
                                        key={idx}
                                        className={`${styles.message} ${msg.role === 'user' ? styles.userMsg : styles.assistantMsg}`}
                                    >
                                        <div className={styles.bubble}>
                                            {msg.content.split('\n').map((line, i) => (
                                                <span key={i}>{line}<br /></span>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                                {loading && (
                                    <div className={`${styles.message} ${styles.assistantMsg}`}>
                                        <div className={styles.bubble}>
                                            <span className={styles.typing}>●●●</span>
                                        </div>
                                    </div>
                                )}
                                <div ref={bottomRef} />
                            </div>

                            {/* 입력창 */}
                            <div className={styles.inputArea}>
                                <textarea
                                    className={styles.input}
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="영화 추천을 요청해보세요..."
                                    rows={1}
                                />
                                <button
                                    className={styles.sendBtn}
                                    onClick={handleSend}
                                    disabled={loading || !input.trim()}
                                >
                                    ↑
                                </button>
                            </div>
                        </>
                    )}
                </div>
            )}
        </>
    )
}

export default ChatBot