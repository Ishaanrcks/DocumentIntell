import DocumentUpload from './components/documentUpload';
import QueryInterface from './components/queryInterface';

export default function Home() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cg fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;%3E%3Cg fill=&quot;%239C92AC&quot; fill-opacity=&quot;0.05&quot;%3E%3Ccircle cx=&quot;30&quot; cy=&quot;30&quot; r=&quot;2&quot;/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50"></div>
            
            <div className="relative z-10 container mx-auto px-4 py-12">
                {/* Header */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl mb-6">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent mb-4">
                        Document Intelligence Platform
                    </h1>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        Upload your documents and unlock insights with AI-powered question answering
                    </p>
                </div>

                {/* Main Content */}
                <div className="grid lg:grid-cols-2 gap-12 max-w-7xl mx-auto">
                    <div className="space-y-6">
                        <DocumentUpload />
                        
                        {/* Features */}
                        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
                            <h3 className="text-lg font-semibold text-white mb-4">✨ Features</h3>
                            <ul className="space-y-2 text-gray-300 text-sm">
                                <li className="flex items-center">
                                    <span className="w-2 h-2 bg-blue-400 rounded-full mr-3"></span>
                                    Instant document processing
                                </li>
                                <li className="flex items-center">
                                    <span className="w-2 h-2 bg-purple-400 rounded-full mr-3"></span>
                                    AI-powered question answering
                                </li>
                                <li className="flex items-center">
                                    <span className="w-2 h-2 bg-pink-400 rounded-full mr-3"></span>
                                    Smart content analysis
                                </li>
                            </ul>
                        </div>
                    </div>
                    
                    <QueryInterface />
                </div>
            </div>
        </div>
    );
}
