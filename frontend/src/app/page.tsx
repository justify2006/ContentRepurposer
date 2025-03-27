'use client';

import { useState } from 'react';

export default function Home() {
  const [inputText, setText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summarize'); //summarize is default option
  


  // AI outputs given user selection that includes error catching
  // Summary options
  const [summaryLength, setSummaryLength] = useState('medium'); //base selections when user doesnt do anything
  const [summaryTone, setSummaryTone] = useState('neutral');
  
  // Social post options
  const [platform, setPlatform] = useState('linkedin');
  const [postTone, setPostTone] = useState('professional');

  const handleSummarize = async (e) => {
    e.preventDefault(); // Pretty much just makes sure the request gets sent straight to my API instead of gathering all the data and potentially making page reload
    
    if (!inputText.trim()) {
      setError('Please enter some text to summarize');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: inputText, 
          length: summaryLength, 
          tone: summaryTone 
        }),
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate summary');
      }
      
      setOutputText(data.summary);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialPost = async (e) => {
    e.preventDefault(); 
    
    if (!inputText.trim()) {
      setError('Please enter some text to convert to a social post');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/api/social-post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: inputText,
          platform: platform,
          tone: postTone
        }),
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate social post');
      }
      
      setOutputText(data.post);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // main body

  return (
    <main className="flex min-h-screen flex-col items-center p-8">
      <div className="w-full max-w-4xl">
        <h1 className="text-3xl font-bold mb-2 text-center">Content Repurposer</h1>
        <p className="text-center text-black mb-8">Transform your content into summaries and social media posts with AI</p>
        
        {/* two-column layout for input and output */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* input panel */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-2 text-black">Input Content</h2>
            <p className="text-sm text-black mb-4">Paste your article, blog post, or any text</p>
            <textarea
              rows={10}
              className="w-full p-3 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-black"
              value={inputText}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your content here..."
            /> {/* Discovered textarea pretty recently, just allows user to change the size of the text box to what they want and makes things easy for formatting*/}
          </div>
          
          {/* output Panel */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-2 text-black">Generated Content</h2>
            <p className="text-sm text-black mb-4">Your repurposed content will appear here</p>
            
            {/*throw error in front-end if something goes bad with API or backend */}
            {error && (
              <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                {error}
              </div>
            )}
            
            <div className="mb-4">
              <textarea
                readOnly
                rows={10}
                className="w-full p-3 border border-gray-300 rounded-md shadow-sm bg-gray-50 text-black"
                value={outputText}
                placeholder="Generated content will appear here..."
              />
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
        
        {/* controls  */}
        <div className="bg-white p-6 rounded-lg shadow-md">
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
                onClick={() => setActiveTab('summarize')}
              >
                Generate Summary
              </button>
              <button
                className={`py-2 px-4 font-medium text-sm ${
                  activeTab === 'social'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-black hover:text-gray-700'
                }`}
                onClick={() => setActiveTab('social')}
              >
                Create Social Post
              </button>
            </div>
          </div>
          
          {/* summary tab info */}
          {activeTab === 'summarize' && (
            <form onSubmit={handleSummarize} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="summaryLength" className="block text-sm font-medium mb-2 text-black">
                    Summary Length:
                  </label>
                  <select
                    id="summaryLength"
                    className="w-full p-2 border border-gray-300 rounded-md shadow-sm text-black" 
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
                    className="w-full p-2 border border-gray-300 rounded-md shadow-sm text-black"
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
                className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
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
                    className="w-full p-2 border border-gray-300 rounded-md shadow-sm text-black"
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
                    className="w-full p-2 border border-gray-300 rounded-md shadow-sm text-black"
                    value={postTone}
                    onChange={(e) => setPostTone(e.target.value)}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="enthusiastic">Enthusiastic</option>
                  </select>
                </div>
              </div>
              
              <button
                type="submit"
                className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                disabled={loading}
              >
                {loading ? 'Generating Post...' : 'Generate Social Post'}
              </button>
            </form>
          )}
        </div>
      </div>
    </main>
  );
}