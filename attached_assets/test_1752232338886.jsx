import React, { useState, useEffect } from 'react';
import { Search, Filter, DollarSign, Briefcase, TrendingUp, Info, Clock, ExternalLink } from 'lucide-react';

// Mock data to simulate deals coming from a Google Sheet
const mockDeals = [
  {
    id: 'deal-001',
    title: 'Innovative AI Startup - Series A',
    description: 'Leading AI company developing next-gen natural language processing solutions for enterprise clients. Strong management team and significant market traction.',
    industry: 'Technology',
    targetAmount: 5000000,
    raisedAmount: 3500000,
    status: 'Open',
    minInvestment: 50000,
    imageUrl: 'https://placehold.co/600x400/007bff/ffffff?text=AI+Tech',
    dueDate: '2025-08-15',
    documentsLink: '#', // Placeholder for actual document link
  },
  {
    id: 'deal-002',
    title: 'Sustainable Energy Project - Solar Farm',
    description: 'Investment opportunity in a large-scale solar farm project in the Southwest. Long-term power purchase agreements in place.',
    industry: 'Renewable Energy',
    targetAmount: 10000000,
    raisedAmount: 8000000,
    status: 'Due Diligence',
    minInvestment: 100000,
    imageUrl: 'https://placehold.co/600x400/28a745/ffffff?text=Solar+Farm',
    dueDate: '2025-09-01',
    documentsLink: '#',
  },
  {
    id: 'deal-003',
    title: 'Boutique Hotel Acquisition - City Center',
    description: 'Acquisition of a charming boutique hotel in a prime tourist location. Significant upside potential through renovation and rebranding.',
    industry: 'Real Estate',
    targetAmount: 7500000,
    raisedAmount: 7500000,
    status: 'Closed',
    minInvestment: 75000,
    imageUrl: 'https://placehold.co/600x400/ffc107/333333?text=Boutique+Hotel',
    dueDate: '2025-06-30',
    documentsLink: '#',
  },
  {
    id: 'deal-004',
    title: 'HealthTech Innovation - Telemedicine Platform',
    description: 'Investing in a rapidly growing telemedicine platform connecting patients with specialists. Addressing critical healthcare access gaps.',
    industry: 'Healthcare',
    targetAmount: 3000000,
    raisedAmount: 1500000,
    status: 'Open',
    minInvestment: 25000,
    imageUrl: 'https://placehold.co/600x400/dc3545/ffffff?text=HealthTech',
    dueDate: '2025-08-01',
    documentsLink: '#',
  },
  {
    id: 'deal-005',
    title: 'Organic Food Production - Farm Expansion',
    description: 'Expansion of an established organic farm to meet increasing demand for sustainable produce. Focus on local distribution.',
    industry: 'Agriculture',
    targetAmount: 2000000,
    raisedAmount: 2000000,
    status: 'Closed',
    minInvestment: 20000,
    imageUrl: 'https://placehold.co/600x400/6f42c1/ffffff?text=Organic+Farm',
    dueDate: '2025-05-20',
    documentsLink: '#',
  },
];

// Helper function to format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

// DealCard Component
const DealCard = ({ deal }) => {
  const progress = (deal.raisedAmount / deal.targetAmount) * 100;

  let statusColor = '';
  switch (deal.status) {
    case 'Open':
      statusColor = 'bg-green-100 text-green-800';
      break;
    case 'Due Diligence':
      statusColor = 'bg-yellow-100 text-yellow-800';
      break;
    case 'Closed':
      statusColor = 'bg-red-100 text-red-800';
      break;
    default:
      statusColor = 'bg-gray-100 text-gray-800';
  }

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden flex flex-col h-full">
      <img
        src={deal.imageUrl}
        alt={deal.title}
        className="w-full h-48 object-cover rounded-t-xl"
        onError={(e) => { e.target.onerror = null; e.target.src = `https://placehold.co/600x400/cccccc/333333?text=${deal.industry.replace(/\s/g, '+')}`; }}
      />
      <div className="p-6 flex flex-col flex-grow">
        <div className="flex justify-between items-start mb-3">
          <h3 className="text-2xl font-semibold text-gray-900 leading-tight pr-4">{deal.title}</h3>
          <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusColor} whitespace-nowrap`}>
            {deal.status}
          </span>
        </div>
        <p className="text-gray-600 mb-4 text-sm flex-grow line-clamp-3">{deal.description}</p>

        <div className="space-y-3 mb-5">
          <div className="flex items-center text-gray-700 text-sm">
            <Briefcase className="w-4 h-4 mr-2 text-blue-500" />
            <span>Industry: <span className="font-medium">{deal.industry}</span></span>
          </div>
          <div className="flex items-center text-gray-700 text-sm">
            <DollarSign className="w-4 h-4 mr-2 text-green-500" />
            <span>Target: <span className="font-medium">{formatCurrency(deal.targetAmount)}</span></span>
          </div>
          <div className="flex items-center text-gray-700 text-sm">
            <TrendingUp className="w-4 h-4 mr-2 text-purple-500" />
            <span>Raised: <span className="font-medium">{formatCurrency(deal.raisedAmount)}</span></span>
          </div>
          <div className="flex items-center text-gray-700 text-sm">
            <Info className="w-4 h-4 mr-2 text-indigo-500" />
            <span>Min. Investment: <span className="font-medium">{formatCurrency(deal.minInvestment)}</span></span>
          </div>
          {deal.dueDate && (
            <div className="flex items-center text-gray-700 text-sm">
              <Clock className="w-4 h-4 mr-2 text-orange-500" />
              <span>Due Date: <span className="font-medium">{new Date(deal.dueDate).toLocaleDateString()}</span></span>
            </div>
          )}
        </div>

        {deal.status !== 'Closed' && (
          <div className="mb-5">
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div
                className="bg-blue-600 h-2.5 rounded-full"
                style={{ width: `${Math.min(100, progress)}%` }}
              ></div>
            </div>
            <p className="text-right text-sm text-gray-600 mt-1">{progress.toFixed(0)}% Raised</p>
          </div>
        )}

        <div className="mt-auto pt-4 border-t border-gray-100">
          <a
            href={deal.documentsLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center w-full px-5 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 transition ease-in-out duration-150 shadow-md"
          >
            View Details
            <ExternalLink className="w-4 h-4 ml-2" />
          </a>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [filteredDeals, setFilteredDeals] = useState(mockDeals);

  const industries = ['All', ...new Set(mockDeals.map(deal => deal.industry))];
  const statuses = ['All', ...new Set(mockDeals.map(deal => deal.status))];

  useEffect(() => {
    const applyFilters = () => {
      let tempDeals = mockDeals;

      // Filter by search term
      if (searchTerm) {
        tempDeals = tempDeals.filter(deal =>
          deal.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          deal.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }

      // Filter by industry
      if (selectedIndustry !== 'All') {
        tempDeals = tempDeals.filter(deal => deal.industry === selectedIndustry);
      }

      // Filter by status
      if (selectedStatus !== 'All') {
        tempDeals = tempDeals.filter(deal => deal.status === selectedStatus);
      }

      setFilteredDeals(tempDeals);
    };

    applyFilters();
  }, [searchTerm, selectedIndustry, selectedStatus]);

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-800 antialiased p-4 sm:p-6 lg:p-8">
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
          body {
            font-family: 'Inter', sans-serif;
          }
        `}
      </style>
      <script src="https://cdn.tailwindcss.com"></script>

      <header className="py-8 text-center">
        <h1 className="text-5xl font-extrabold text-gray-900 mb-4 leading-tight">
          Co-Investment Portal
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Explore exclusive investment opportunities tailored for our valued partners.
        </p>
      </header>

      <main className="max-w-7xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
          {/* Search Input */}
          <div className="relative flex-grow w-full sm:w-auto">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search deals by title or description..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Industry Filter */}
          <div className="relative w-full sm:w-auto">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full appearance-none bg-white focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
            >
              {industries.map(industry => (
                <option key={industry} value={industry}>{industry}</option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
            </div>
          </div>

          {/* Status Filter */}
          <div className="relative w-full sm:w-auto">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full appearance-none bg-white focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
            >
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
            </div>
          </div>
        </div>

        {filteredDeals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredDeals.map(deal => (
              <DealCard key={deal.id} deal={deal} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500 text-lg">
            No deals found matching your criteria.
          </div>
        )}
      </main>

      <footer className="py-8 text-center text-gray-500 text-sm mt-12">
        &copy; {new Date().getFullYear()} Co-Investment Portal. All rights reserved.
      </footer>
    </div>
  );
};