'use client';

import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function Home() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [instagramUrl, setInstagramUrl] = useState('');
  const [videoAData, setVideoAData] = useState<any>(null);
  const [videoBData, setVideoBData] = useState<any>(null);
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<{question: string, answer: string}[]>([]);

  const processVideo = async (url: string, platform: 'youtube' | 'instagram') => {
    const endpoint = platform === 'youtube' ? '/process-youtube' : '/process-instagram';
    try {
      const res = await axios.post(`${BACKEND_URL}${endpoint}`, { url });
      return res.data;
    } catch (err) {
      console.error(err);
      return null;
    }
  };

  const handleIngest = async () => {
    if (!youtubeUrl && !instagramUrl) {
      alert('Please enter at least one video URL');
      return;
    }
    
    setLoading(true);
    
    if (youtubeUrl) {
      const result = await processVideo(youtubeUrl, 'youtube');
      setVideoAData(result);
      
      if (result && result.transcript) {
        await axios.post(`${BACKEND_URL}/store`, {
          video_id: result.video_id,
          transcript: result.transcript,
          metadata: {
            title: result.title,
            creator: result.creator,
            views: result.views,
            engagement_rate: result.engagement_rate
          }
        });
      }
    }
    
    if (instagramUrl) {
      const result = await processVideo(instagramUrl, 'instagram');
      setVideoBData(result);
      
      if (result && result.transcript && !result.transcript.includes('mock')) {
        await axios.post(`${BACKEND_URL}/store`, {
          video_id: result.video_id,
          transcript: result.transcript,
          metadata: {
            title: result.title,
            creator: result.creator,
            views: result.views,
            engagement_rate: result.engagement_rate
          }
        });
      }
    }
    
    setLoading(false);
  };

  const handleAsk = async () => {
    if (!query) return;
    
    setLoading(true);
    try {
      const res = await axios.post(`${BACKEND_URL}/ask`, {
        query,
        video_a_id: videoAData?.video_id,
        video_b_id: videoBData?.video_id
      });
      
      setAnswer(res.data.answer);
      setSources(res.data.sources);
      setChatHistory(prev => [...prev, { question: query, answer: res.data.answer }]);
      setQuery('');
    } catch (err) {
      console.error(err);
      setAnswer('Error: Could not get response from server');
    }
    setLoading(false);
  };

  const clearChat = () => {
    setChatHistory([]);
    setAnswer('');
    setSources([]);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Animated background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse delay-1000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 backdrop-blur-sm border border-white/10 text-sm text-gray-400 mb-4">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            AI-Powered Analysis
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Creator Intelligence
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Compare YouTube and Instagram Reels performance with AI-powered insights and actionable recommendations
          </p>
        </div>

        {/* Video Input Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* YouTube Card */}
          <div className="group relative bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-blue-500/30 transition-all duration-300 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zM9.935 15.594v-7.188l6.234 3.594-6.234 3.594z"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">YouTube Video</h2>
              </div>
              
              <input
                type="text"
                placeholder="https://youtube.com/watch?v=..."
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:border-blue-500 focus:outline-none transition-all text-white placeholder:text-gray-500"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
              />
              
              {videoAData && (
                <div className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm text-gray-400">Title</p>
                      <p className="font-medium text-white text-sm line-clamp-2">{videoAData.title}</p>
                      <div className="grid grid-cols-2 gap-3 mt-3">
                        <div>
                          <p className="text-xs text-gray-500">Creator</p>
                          <p className="text-sm text-white">{videoAData.creator}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Views</p>
                          <p className="text-sm text-white">{videoAData.views?.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Engagement</p>
                          <p className="text-sm font-semibold text-green-400">{videoAData.engagement_rate}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Followers</p>
                          <p className="text-sm text-white">{videoAData.followers?.toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Instagram Card */}
          <div className="group relative bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-pink-500/30 transition-all duration-300 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-pink-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-pink-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2c2.717 0 3.056.01 4.122.06 1.065.05 1.79.217 2.428.465.66.254 1.216.598 1.772 1.153.509.5.902 1.105 1.153 1.772.247.637.415 1.363.465 2.428.047 1.066.06 1.405.06 4.122 0 2.717-.01 3.056-.06 4.122-.05 1.065-.218 1.79-.465 2.428-.254.66-.598 1.216-1.153 1.772-.5.509-1.105.902-1.772 1.153-.637.247-1.363.415-2.428.465-1.066.047-1.405.06-4.122.06-2.717 0-3.056-.01-4.122-.06-1.065-.05-1.79-.218-2.428-.465-.66-.254-1.216-.598-1.772-1.153-.509-.5-.902-1.105-1.153-1.772-.247-.637-.415-1.363-.465-2.428-.047-1.066-.06-1.405-.06-4.122 0-2.717.01-3.056.06-4.122.05-1.065.218-1.79.465-2.428.254-.66.598-1.216 1.153-1.772.5-.509 1.105-.902 1.772-1.153.637-.247 1.363-.415 2.428-.465C8.944 2.01 9.283 2 12 2zm0 5a5 5 0 100 10 5 5 0 000-10z"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">Instagram Reel</h2>
              </div>
              
              <input
                type="text"
                placeholder="https://instagram.com/reel/..."
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:border-pink-500 focus:outline-none transition-all text-white placeholder:text-gray-500"
                value={instagramUrl}
                onChange={(e) => setInstagramUrl(e.target.value)}
              />
              
              {videoBData && (
                <div className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm text-gray-400">Title</p>
                      <p className="font-medium text-white text-sm line-clamp-2">{videoBData.title}</p>
                      <div className="grid grid-cols-2 gap-3 mt-3">
                        <div>
                          <p className="text-xs text-gray-500">Creator</p>
                          <p className="text-sm text-white">{videoBData.creator}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Views</p>
                          <p className="text-sm text-white">{videoBData.views?.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Engagement</p>
                          <p className="text-sm font-semibold text-green-400">{videoBData.engagement_rate}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Hashtags</p>
                          <p className="text-sm text-white truncate">{videoBData.hashtags?.slice(0, 2).join(', ') || '—'}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Ingest Button */}
        <div className="flex justify-center mb-12">
          <button
            onClick={handleIngest}
            disabled={loading}
            className="relative px-8 py-4 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                🚀 Analyze Videos
              </span>
            )}
          </button>
        </div>

        {/* Chat Section */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden">
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">AI Conversation</h2>
              </div>
              {chatHistory.length > 0 && (
                <button
                  onClick={clearChat}
                  className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Clear
                </button>
              )}
            </div>
          </div>
          
          <div className="p-6">
            {/* Chat History */}
            <div className="space-y-4 mb-6 max-h-[400px] overflow-y-auto custom-scrollbar">
              {chatHistory.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <p className="text-gray-400">Ask questions about your videos</p>
                  <p className="text-sm text-gray-500 mt-1">Try: "Why did Video A perform better?"</p>
                </div>
              ) : (
                chatHistory.map((chat, idx) => (
                  <div key={idx} className="space-y-3">
                    <div className="flex justify-end">
                      <div className="max-w-[80%] bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl rounded-tr-sm px-4 py-3">
                        <p className="text-white text-sm">{chat.question}</p>
                      </div>
                    </div>
                    <div className="flex justify-start">
                      <div className="max-w-[80%] bg-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
                        <div className="text-sm text-gray-300 prose prose-invert max-w-none">
                          <ReactMarkdown>{chat.answer}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
              
              {/* Current Answer */}
              {answer && !chatHistory.some(c => c.answer === answer) && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] bg-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
                    <div className="text-sm text-gray-300 prose prose-invert max-w-none">
                      <ReactMarkdown>{answer}</ReactMarkdown>
                    </div>
                    {sources.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-white/10">
                        <p className="text-xs text-gray-500 mb-1">📎 Sources:</p>
                        <div className="flex flex-wrap gap-2">
                          {sources.map((s, i) => (
                            <span key={i} className="text-xs bg-white/5 px-2 py-1 rounded-md text-gray-400">
                              Video {s.video_id.slice(0, 8)} (Chunk {s.chunk_index})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            {/* Input Area */}
            <div className="flex gap-3">
              <input
                type="text"
                placeholder="Ask about your videos..."
                className="flex-1 px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:border-purple-500 focus:outline-none transition-all text-white placeholder:text-gray-500"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
              />
              <button
                onClick={handleAsk}
                disabled={loading || !query}
                className="px-6 py-3 rounded-xl font-semibold bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg hover:shadow-purple-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-xs text-gray-500">
          Powered by Groq LLM • ChromaDB • YouTube API
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </main>
  );
}