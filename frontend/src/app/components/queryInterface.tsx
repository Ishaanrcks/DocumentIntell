"use client"
import { useState, useEffect } from 'react';
import axios from 'axios';
import { MagnifyingGlassIcon, DocumentIcon, SparklesIcon, ClipboardDocumentIcon, EyeIcon } from '@heroicons/react/24/outline';

export default function QueryInterface() {
    const [documents, setDocuments] = useState([]);
    const [selectedDoc, setSelectedDoc] = useState('');
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/documents/');
            setDocuments(response.data);
        } catch (error) {
            console.error('Failed to fetch documents');
        }
    };

    const handleQuery = async () => {
        if (!question) return;

        setLoading(true);
        setAnswer(''); // Clear previous answer
        try {
            const response = await axios.post('http://localhost:8000/api/documents/query/', {
                document_id: selectedDoc || null,
                question
            });
            setAnswer(response.data.answer);
            console.log('Answer:', response.data.answer);
        } catch (error) {
            setAnswer('Failed to get answer. Please try again.');
        }
        setLoading(false);
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(answer);
        // You can add a toast notification here
        alert('Answer copied to clipboard!');
    };

    return (
        <div className="p-8 max-w-2xl mx-auto bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700">
            <div className="text-center mb-6">
                <SparklesIcon className="h-12 w-12 text-purple-400 mx-auto mb-3" />
                <h2 className="text-2xl font-bold text-white mb-2">AI Document Assistant</h2>
                <p className="text-gray-400 text-sm">Ask questions about your uploaded documents</p>
            </div>

            {/* Document Selector */}
            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                    <DocumentIcon className="h-4 w-4 inline mr-2" />
                    Select Document
                </label>
                <select
                    value={selectedDoc}
                    onChange={(e) => setSelectedDoc(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-600 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                >
                    <option value="">🌐 All Documents</option>
                    {documents.map((doc: any) => (
                        <option key={doc.id} value={doc.id}>📄 {doc.title}</option>
                    ))}
                </select>
            </div>

            {/* Question Input */}
            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                    Your Question
                </label>
                <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="What would you like to know about your documents? Ask anything..."
                    className="w-full p-4 bg-gray-800 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 resize-none h-32"
                />
            </div>

            {/* Search Button */}
            <button
                onClick={handleQuery}
                disabled={!question || loading}
                className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-300 transform ${!question || loading
                        ? 'bg-gray-600 cursor-not-allowed opacity-50'
                        : 'bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 hover:scale-105 shadow-lg hover:shadow-xl'
                    }`}
            >
                {loading ? (
                    <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Analyzing...</span>
                    </div>
                ) : (
                    <div className="flex items-center justify-center space-x-2">
                        <MagnifyingGlassIcon className="h-5 w-5" />
                        <span>Ask AI Assistant</span>
                    </div>
                )}
            </button>

            {/* Enhanced Answer Display */}
            {answer && (
                <div className="mt-8 bg-gradient-to-r from-gray-800 to-gray-700 rounded-2xl border border-gray-600 overflow-hidden">
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 bg-gray-800/50 border-b border-gray-600">
                        <div className="flex items-center">
                            <SparklesIcon className="h-5 w-5 text-purple-400 mr-2" />
                            <h3 className="font-bold text-white">AI Response</h3>
                        </div>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={() => setIsExpanded(!isExpanded)}
                                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-700"
                                title={isExpanded ? "Collapse" : "Expand"}
                            >
                                <EyeIcon className="h-4 w-4" />
                            </button>
                            <button
                                onClick={copyToClipboard}
                                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-700"
                                title="Copy to clipboard"
                            >
                                <ClipboardDocumentIcon className="h-4 w-4" />
                            </button>
                        </div>
                    </div>

                    {/* Answer Content */}
                    <div className="p-6">
                        <div
                            className={`bg-gray-900 rounded-xl border border-gray-600 transition-all duration-300 ${isExpanded ? 'max-h-none' : 'max-h-96 overflow-hidden'
                                }`}
                        >
                            <div className="p-6">
                                <pre className="text-gray-200 leading-relaxed whitespace-pre-wrap font-sans text-sm">
                                    {answer}
                                </pre>
                            </div>

                            {/* Gradient overlay for collapsed state */}
                            {!isExpanded && answer.length > 500 && (
                                <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-gray-900 to-transparent pointer-events-none"></div>
                            )}
                        </div>

                        {/* Expand/Collapse button for long answers */}
                        {answer.length > 500 && (
                            <button
                                onClick={() => setIsExpanded(!isExpanded)}
                                className="mt-4 w-full py-2 px-4 bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white rounded-lg transition-all duration-300 text-sm font-medium"
                            >
                                {isExpanded ? 'Show Less ↑' : 'Show More ↓'}
                            </button>
                        )}

                        {/* Answer metadata */}
                        <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
                            <span>Response generated in real-time</span>
                            <span>{answer.length} characters</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Loading state for answer */}
            {loading && (
                <div className="mt-8 p-6 bg-gradient-to-r from-gray-800 to-gray-700 rounded-2xl border border-gray-600">
                    <div className="flex items-center mb-3">
                        <SparklesIcon className="h-5 w-5 text-purple-400 mr-2" />
                        <h3 className="font-bold text-white">AI is thinking...</h3>
                    </div>
                    <div className="bg-gray-900 p-6 rounded-xl border border-gray-600">
                        <div className="animate-pulse space-y-3">
                            <div className="h-4 bg-gray-700 rounded w-3/4"></div>
                            <div className="h-4 bg-gray-700 rounded w-1/2"></div>
                            <div className="h-4 bg-gray-700 rounded w-5/6"></div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
