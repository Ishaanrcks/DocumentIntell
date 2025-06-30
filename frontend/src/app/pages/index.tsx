import DocumentUpload from  '../components/documentUpload';
import QueryInterface from '../components/queryInterface';

export default function Home() {
    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto">
                <h1 className="text-3xl font-bold text-center mb-8">
                    Document Intelligence Platform
                </h1>

                <div className="grid md:grid-cols-2 gap-8">
                    <DocumentUpload />
                    <QueryInterface />
                </div>
            </div>
        </div>
    );
}
