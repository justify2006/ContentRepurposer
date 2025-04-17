'use client';

import { useState, useEffect, FormEvent } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const YOUTUBE_REGEX = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;

export default function Home() {
  // Input
  const [inputText, setInputText] = useState('');
  const [isYouTubeUrl, setIsYouTubeUrl] = useState(false);
  
  // Output
  const [outputText, setOutputText] = useState('');
  const [outputImages, setOutputImages] = useState<string[]>([]);
  
  // UI
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summarize');
  
  // Settings
  const [summaryLength, setSummaryLength] = useState('medium');
  const [summaryTone, setSummaryTone] = useState('neutral');
  const [platform, setPlatform] = useState('linkedin');
  const [postTone, setPostTone] = useState('professional');

  useEffect(() => {
    setIsYouTubeUrl(YOUTUBE_REGEX.test(inputText.trim()));
  }, [inputText]);

  const fetchYouTubeTranscript = async (url: string) => {
    const response = await fetch(`${API_URL}/api/youtube-transcript`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    
    if (!response.ok) throw new Error('Failed to fetch transcript');
    const data = await response.json();
    return data.transcript;
  };

  const resetOutput = () => {
    setError('');
    setOutputText('');
    setOutputImages([]);
  };

  const handleSummarize = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputText.trim()) {
      setError('Please enter content to summarize');
      return;
    }

    setLoading(true);
    resetOutput();
    
    try {
      const textToSummarize = isYouTubeUrl 
        ? await fetchYouTubeTranscript(inputText)
        : inputText;

      const response = await fetch(`${API_URL}/api/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: textToSummarize, 
          length: summaryLength, 
          tone: summaryTone 
        }),
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to generate summary');
      setOutputText(data.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialPost = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputText.trim()) {
      setError('Please enter content for social post');
      return;
    }

    setLoading(true);
    resetOutput();
    
    try {
      const textToPost = isYouTubeUrl 
        ? await fetchYouTubeTranscript(inputText)
        : inputText;

      const response = await fetch(`${API_URL}/api/social-post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: textToPost,
          platform,
          tone: postTone
        }),
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to create social post');
      setOutputText(data.post);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleVisualPost = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputText.trim()) {
      setError('Please enter content for visual post');
      return;
    }

    setLoading(true);
    resetOutput();

    try {
      const textToVisualize = isYouTubeUrl 
        ? await fetchYouTubeTranscript(inputText)
        : inputText;

      const response = await fetch(`${API_URL}/api/visual-post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToVisualize }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to generate visuals');
      
      if (!data.image_data_list?.length) {
        throw new Error('No visuals were generated');
      }
      
      setOutputImages(data.image_data_list);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };


  return (
    <main className="flex min-h-screen flex-col items-center p-8">
      <div className="w-full max-w-4xl">
        <h1 className="text-3xl font-bold mb-2 text-center">Content Repurposer</h1>
        <p className="text-center text-black mb-8">Transform your content into summaries, social media posts, and visual highlights with AI</p>
        
        {/*Input and output panels*/}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-2 text-black">Input Content</h2>
            <p className="text-sm text-black mb-4">
              Paste your article, blog post, or YouTube URL
              {isYouTubeUrl && <span className="ml-1 text-red-500">(YouTube URL)</span>}
            </p>
            <textarea
              rows={10}
              className="w-full p-3 border border-gray-300 rounded-md text-black"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your content or YouTube URL here..."
            />
          </div>
          
          <div className="bg-white p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-2 text-black">Generated Content</h2>
            <p className="text-sm text-black mb-4">Your repurposed content will appear here</p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                {error}
              </div>
            )}
            
            <div className="flex-grow mb-4 relative">
              {outputImages.length > 0 ? (
                <div className="space-y-2 overflow-auto h-full p-2">
                  {outputImages.map((imgSrc, index) => (
                    <img 
                      key={index}
                      src={imgSrc} 
                      alt={`Generated Visual ${index + 1}`}
                      className="max-w-full h-auto object-contain border border-gray-200 rounded"
                    />
                  ))}
                </div>
              ) : (
                <textarea
                  readOnly
                  rows={10}
                  className="w-full h-full p-3 border border-gray-300 rounded-md bg-gray-50 text-black"
                  value={outputText}
                  placeholder="Generated content will appear here..."
                />
              )}
            </div>
            
            {outputText && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigator.clipboard.writeText(outputText)} 
                  className="py-1 px-3 text-sm bg-gray-200 rounded-md hover:bg-gray-600 transition-colors text-black"
                >
                  Copy to Clipboard
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* controls*/}
        <div className="bg-white p-6 rounded-lg ">
          <h2 className="text-xl font-semibold mb-2 text-black">Content Transformation</h2>
          <p className="text-sm text-black mb-4">Choose how to repurpose your content</p>
          
          {/* tabs */}
          <div className="mb-6">
            <div className="flex border-b border-gray-200">
              <button
                className={`py-2 px-4 font-medium text-sm ${
                  activeTab === 'summarize'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-black hover:text-gray-700'
                }`}
                onClick={() => {setActiveTab('summarize'); setOutputImages([])}}
              >
                Generate Summary
              </button>
              <button
                className={`py-2 px-4 font-medium text-sm ${
                  activeTab === 'social'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-black hover:text-gray-700'
                }`}
                onClick={() => {setActiveTab('social'); setOutputImages([])}}
              >
                Create Social Post
              </button>
              <button
                className={`py-2 px-4 font-medium text-sm ${
                  activeTab === 'visual'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-black hover:text-gray-700'
                }`}
                onClick={() => {setActiveTab('visual'); setOutputText('')}}
              >
                Generate Visual Post
              </button>
            </div>
          </div>
          
          {/* summary tab*/}
          {activeTab === 'summarize' && (
            <form onSubmit={handleSummarize} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="summaryLength" className="block text-sm font-medium mb-2 text-black">
                    Summary Length:
                  </label>
                  <select
                    id="summaryLength"
                    className="w-full p-2 border border-gray-300 rounded-md text-black" 
                    value={summaryLength}
                    onChange={(e) => setSummaryLength(e.target.value)}
                  >
                    <option value="short">Short (2-3 sentences)</option>
                    <option value="medium">Medium (4-6 sentences)</option>
                    <option value="long">Long (7-10 sentences)</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="summaryTone" className="block text-sm font-medium mb-2 text-black">
                    Tone:
                  </label>
                  <select
                    id="summaryTone"
                    className="w-full p-2 border border-gray-300 rounded-md text-black"
                    value={summaryTone}
                    onChange={(e) => setSummaryTone(e.target.value)}
                  >
                    <option value="neutral">Neutral</option>
                    <option value="formal">Formal</option>
                    <option value="casual">Casual</option>
                  </select>
                </div>
              </div>
              
              <button
                type="submit"
                className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md"
                disabled={loading}
              >
                {loading ? 'Generating Summary...' : 'Generate Summary'}
              </button>
            </form>
          )}
          
          {/* social media tab info */}
          {activeTab === 'social' && (
            <form onSubmit={handleSocialPost} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="platform" className="block text-sm font-medium mb-2 text-black">
                    Platform:
                  </label>
                  <select
                    id="platform"
                    className="w-full p-2 border border-gray-300 rounded-md text-black"
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                  >
                    <option value="linkedin">LinkedIn</option>
                    <option value="twitter">Twitter</option>
                    <option value="facebook">Facebook</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="postTone" className="block text-sm font-medium mb-2 text-black">
                    Tone:
                  </label>
                  <select
                    id="postTone"
                    className="w-full p-2 border border-gray-300 rounded-md text-black"
                    value={postTone}
                    onChange={(e) => setPostTone(e.target.value)}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="enthusiastic">Enthusiastic</option>
                    <option value="informative">Informative</option>
                  </select>
                </div>
              </div>
              
              <button
                type="submit"
                className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md"
                disabled={loading}
              >
                {loading ? 'Generating Social Post...' : 'Generate Social Post'}
              </button>
            </form>
          )}

          {activeTab === 'visual' && (
            <form onSubmit={handleVisualPost} className="space-y-4">
              <div>
                 <p className="text-sm text-gray-600 mb-4">
                   Generate a simple infographic image highlighting the key points from your content.
                 </p>
              </div>
              <button
                type="submit"
                className="w-full py-2 px-4 bg-purple-600 text-white font-medium rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Generating Image...' : 'Generate Visual(s)'}
              </button>
            </form>
          )}
        </div>
      </div>
    </main>
  );
}