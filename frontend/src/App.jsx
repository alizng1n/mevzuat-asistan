import { useState, useRef, useEffect } from 'react';
import { 
  MessageSquare, History, Library, Settings, 
  Send, Search, Plus, CheckCircle2, AlertTriangle, 
  FileText, ArrowRight, User, Sparkles, Sun, Moon
} from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('applications');
  const [isChatMode, setIsChatMode] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [stats, setStats] = useState({ total: 0, ready: 0, review: 0, efficiency: 0 });
  const [drafts, setDrafts] = useState([]);
  const [sources, setSources] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, draftsRes, sourcesRes] = await Promise.all([
          axios.get('http://localhost:8000/api/stats'),
          axios.get('http://localhost:8000/api/drafts'),
          axios.get('http://localhost:8000/api/sources')
        ]);
        setStats(statsRes.data);
        setDrafts(draftsRes.data);
        setSources(sourcesRes.data);
      } catch (err) {
        console.error("Failed to fetch data", err);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.remove('light-theme');
    } else {
      document.body.classList.add('light-theme');
    }
  }, [isDarkMode]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleStartChat = (initialMessage = '') => {
    setIsChatMode(true);
    if (initialMessage) {
      handleSendMessage(initialMessage);
    }
  };

  const handleSendMessage = async (customMessage) => {
    const textToSend = typeof customMessage === 'string' ? customMessage : input;
    if (!textToSend.trim()) return;

    // Add user message
    const newMessages = [...messages, { role: 'user', content: textToSend }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: textToSend,
        history: messages
      });

      setMessages([...newMessages, { 
        role: 'assistant', 
        content: response.data.answer,
        sources: response.data.sources
      }]);
    } catch (error) {
      console.error(error);
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: "Üzgünüm, bir hata oluştu. Lütfen FastAPI sunucusunun çalıştığından emin olun." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <h1>Mevzuat AI</h1>
          <p>Akademik Asistan</p>
        </div>

        <button className="new-chat-btn" onClick={() => handleStartChat()}>
          <Plus size={18} />
          Yeni Analiz
        </button>

        <ul className="nav-links">
          <li className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} onClick={() => { setActiveTab('history'); setIsChatMode(false); }}>
            <History className="nav-icon" /> Geçmiş
          </li>
          <li className={`nav-item ${activeTab === 'library' ? 'active' : ''}`} onClick={() => { setActiveTab('library'); setIsChatMode(false); }}>
            <Library className="nav-icon" /> Kütüphane
          </li>
          <li className={`nav-item ${activeTab === 'applications' ? 'active' : ''}`} onClick={() => { setActiveTab('applications'); setIsChatMode(false); }}>
            <FileText className="nav-icon" /> Başvurularım
          </li>
          <li className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => { setActiveTab('settings'); setIsChatMode(false); }}>
            <Settings className="nav-icon" /> Ayarlar
          </li>
          <li className="nav-item" onClick={() => setIsDarkMode(!isDarkMode)} style={{ marginTop: 'auto' }}>
            {isDarkMode ? <Sun className="nav-icon" /> : <Moon className="nav-icon" />}
            {isDarkMode ? 'Açık Tema' : 'Koyu Tema'}
          </li>
        </ul>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {!isChatMode ? (
          <>
            <div className="topbar">
              <div className="search-bar">
                <Search size={16} color="#94A3B8" />
                <input type="text" placeholder="Mevzuatlarda ara..." onKeyDown={(e) => {
                  if(e.key === 'Enter') handleStartChat(e.target.value);
                }} />
              </div>
            </div>

            <div className="content-wrapper">
              <div className="page-header">
                <div>
                  <h2>Dilekçe Taslaklarım</h2>
                  <p>Mevzuat AI asistanı aracılığıyla hazırlanan akademik dilekçelerinizi yönetin.</p>
                </div>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-title">TOPLAM TASLAK</div>
                  <div className="stat-value white">{stats.total}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-title">DIŞA AKTARILMAYA HAZIR</div>
                  <div className="stat-value cyan">{stats.ready}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-title">İNCELEMEDE</div>
                  <div className="stat-value purple">{stats.review}</div>
                </div>
              </div>

              <div className="cards-grid">
                {drafts.slice(0, 2).map((draft, idx) => (
                  <div key={draft.id} className="dashboard-card" onClick={() => handleStartChat(`${draft.title} hakkında bilgi ver.`)}>
                    <div className="card-header">
                      {draft.status === 'ready' && <span className="tag ready"><CheckCircle2 size={12} /> Dışa Aktarıma Hazır</span>}
                      {draft.status === 'drafting' && <span className="tag drafting"><Sparkles size={12} /> Taslak Aşamasında</span>}
                      {draft.status === 'review' && <span className="tag" style={{background: 'rgba(236,72,153,0.1)', color: 'var(--accent-pink)'}}><AlertTriangle size={12} /> İncelemede</span>}
                      {draft.status === 'finalized' && <span className="tag" style={{background: 'rgba(0,229,255,0.1)', color: 'var(--accent-blue)'}}><CheckCircle2 size={12} /> Onaylandı</span>}
                      <span style={{ fontSize: 12, color: '#94A3B8' }}>{new Date(draft.updated_at).toLocaleDateString('tr-TR')}</span>
                    </div>
                    <div className="card-title" style={{ fontSize: idx === 0 ? 22 : 18 }}>{draft.title}</div>
                    <div className="card-desc" style={{ fontSize: idx === 0 ? 14 : 13 }}>{draft.description}</div>
                    
                    {idx === 0 ? (
                      <div className="card-actions">
                        <button className="btn-primary">PDF İndir</button>
                        <button className="btn-secondary">Taslağı Düzenle</button>
                      </div>
                    ) : (
                      <div className="progress-bar-container">
                        <div className="progress-track">
                          <div className="progress-fill" style={{ width: `${draft.progress}%` }}></div>
                        </div>
                        <div className="progress-text">{draft.progress}% Tamamlandı</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="cards-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
                {drafts.slice(2, 5).map((draft, idx) => {
                  let icon = <FileText size={20} />;
                  let bgColors = { bg: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)', border: 'var(--border-color)' };
                  
                  if (draft.status === 'finalized') {
                    icon = <CheckCircle2 size={20} />;
                    bgColors = { bg: 'rgba(0,229,255,0.1)', color: 'var(--accent-blue)', border: 'rgba(0,229,255,0.2)' };
                  } else if (draft.status === 'review') {
                    icon = <AlertTriangle size={20} />;
                    bgColors = { bg: 'rgba(236,72,153,0.1)', color: 'var(--accent-pink)', border: 'rgba(236,72,153,0.2)' };
                  }
                  
                  return (
                    <div key={draft.id} className="dashboard-card" style={{ padding: '20px', borderColor: bgColors.border }} onClick={() => handleStartChat(`${draft.title} hakkında`)}>
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <div style={{ background: bgColors.bg, color: bgColors.color, padding: '10px', borderRadius: '8px' }}>
                          {icon}
                        </div>
                        <div>
                          <h4 style={{ fontSize: 14 }}>{draft.title}</h4>
                          <p style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                            {draft.status === 'review' ? 'İnceleme Bekliyor' : new Date(draft.updated_at).toLocaleDateString('tr-TR')}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              <div className="dashboard-card" style={{ marginTop: '20px', background: isDarkMode ? 'linear-gradient(90deg, #181D2D 0%, #131622 100%)' : 'var(--bg-sidebar)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ background: 'rgba(0,229,255,0.1)', color: 'var(--accent-blue)', padding: '8px', borderRadius: '8px' }}>
                    <Library size={16} />
                  </div>
                  <h4 style={{ color: 'var(--accent-blue)', fontSize: '13px', letterSpacing: '1px' }}>YÜKLÜ KAYNAKLAR</h4>
                </div>
                <h3 style={{ fontSize: '24px', marginBottom: '12px' }}>Sistemdeki Mevzuatlar</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '16px' }}>
                  {sources.length > 0 ? sources.map((src, i) => (
                    <div key={i} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', padding: '8px 12px', borderRadius: '8px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FileText size={14} color="var(--text-secondary)" /> {src}
                    </div>
                  )) : (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Henüz sisteme yüklenmiş bir kaynak bulunmuyor.</p>
                  )}
                </div>
              </div>

            </div>
          </>
        ) : (
          /* Chat Interface */
          <div className="chat-container">
            <div className="messages-list">
              {messages.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '40px' }}>
                  <img src="/iste_logo.png" alt="İSTE Logo" style={{ width: '48px', height: '48px', opacity: 0.8, marginBottom: '16px' }} />
                  <h2>Size nasıl yardımcı olabilirim?</h2>
                  <p>Üniversite mevzuatları hakkında soru sorabilirsiniz.</p>
                </div>
              )}
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? <User size={18} /> : <img src="/iste_logo.png" alt="AI" style={{ width: '24px', height: '24px', objectFit: 'contain' }} />}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <div className="message-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources-container">
                        {msg.sources.map((src, i) => (
                          <div key={i} className="source-tag" title={src.content}>
                            📚 Kaynak: {src.source.split('\\').pop().split('/').pop()}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message assistant">
                  <div className="message-avatar"><img src="/iste_logo.png" alt="AI" style={{ width: '24px', height: '24px', objectFit: 'contain' }} /></div>
                  <div className="message-content">
                    <div className="typing-dots">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-wrapper">
              <input 
                type="text" 
                placeholder="Mevzuat asistanına sor..." 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                disabled={isLoading}
              />
              <button className="send-btn" onClick={handleSendMessage} disabled={isLoading || !input.trim()}>
                <Send size={16} />
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
