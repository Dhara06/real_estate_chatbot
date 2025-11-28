import React, { useState } from 'react';
import { LineChart, Line, Bar,BarChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Send, TrendingUp, MapPin } from 'lucide-react';

const RealEstateChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const sendQuery = async () => {
    if (!query.trim()) return;

    const userMessage = { type: 'user', text: query };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch('https://real-estate-chatbot-1-tp68.onrender.com/api/analyze/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      console.log("FULL API RESPONSE:", data);
console.log("chartData:", data.chartData);
console.log("areas:", data.areas);
      
      const botMessage = {
        type: 'bot',
        summary: data.summary,
        chartData: data.chartData,
        chartType: data.chartType,
        tableData: data.tableData,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'bot',
        summary: 'Error connecting to backend. Make sure Django server is running on port 8000.',
        chartData: [],
        tableData: [],
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setQuery('');
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendQuery();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-slate-50 to-white px-6 py-10">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-8 mb-8">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">
Real Estate Analysis Chatbot</h1>
              <p className="text-slate-500">Ask about property trends, prices, and demand</p>
            </div>
          </div>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-8 mb-8" style={{ minHeight: '500px', maxHeight: '700px', overflowY: 'auto' }}>
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <h2 className="text-xl font-semibold text-gray-600 mb-2">Start Your Analysis</h2>
              <p className="text-gray-500 mb-4">Try asking:</p>
              <div className="space-y-2">
                <button
                  onClick={() => setQuery("Analyze Wakad")}
                  className="block w-full max-w-md mx-auto bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl
 px-4 py-2 rounded-lg transition"
                >
                  "Analyze Wakad"
                </button>
                <button
                  onClick={() => setQuery("Show price growth for Akurdi")}
                  className="block w-full max-w-md mx-auto bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl
 px-4 py-2 rounded-lg transition"
                >
                  "Show price growth for Akurdi"
                </button>
                <button
                  onClick={() => setQuery("Compare demand trends of Aundh and Ambegaon Budruk")}
                  className="block w-full max-w-md mx-auto bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl
 px-4 py-2 rounded-lg transition"
                >
                  "Compare demand trends of Aundh and Ambegaon Budruk"
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div key={idx}>
                  {msg.type === 'user' ? (
                    <div className="flex justify-end">
                      <div className="bg-indigo-600 text-white px-4 py-2 rounded-lg max-w-lg">
                        {msg.text}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-slate-50 border border-slate-200 p-5 rounded-2xl shadow-sm">

                      {/* Summary */}
                      <div className="mb-4">
                        <h3 className="font-semibold text-gray-800 mb-2">Analysis Summary</h3>
                        <p className="text-gray-700">{msg.summary}</p>
                      </div>

                      {/* Chart */}
                      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">

                      {msg.chartData && msg.chartData.length > 0 && (
                      <div className="mb-4">
                        <h3 className="font-semibold text-gray-800 mb-2">
                          {msg.chartType === "bar" ? "Comparison Chart" : "Trend Analysis"}
                        </h3>

                        <ResponsiveContainer width="100%" height={300}>
      
                          {msg.chartType === "bar" ? (
                            <BarChart data={msg.chartData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="label" />
                              <YAxis />
                              <Tooltip />
                              <Legend />
                              <Bar dataKey="value" fill="#6366f1" name="Total Sales" />
                            </BarChart>
                          ) : (
                            <LineChart data={msg.chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="year" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line
                              type="monotone"
                              dataKey="totalSales"
                              stroke="#4f46e5"
                              strokeWidth={2}
                              name="Total Sales"
                            />
                            <Line
                              type="monotone"
                              dataKey="flatRate"
                              stroke="#10b981"
                              strokeWidth={2}
                              name="Flat Rate"
                            />
                          </LineChart>
                       )}

                    </ResponsiveContainer>
                  </div>
                )}
                      </div>

                    



                      {/* Table */}
                      {msg.tableData && msg.tableData.length > 0 && (
                        <div>
                          <h3 className="font-semibold text-gray-800 mb-2">Detailed Data</h3>
                          <div className="overflow-x-auto">
                            <table className="table table-striped table-bordered table-hover w-full">
                              <thead className="bg-indigo-600 text-white">
                                <tr>
                                  <th className="px-4 py-2">Year</th>
                                  <th className="px-4 py-2">Area</th>
                                  <th>Total Sales (₹)</th>
                                  <th>Flats Sold</th>
                                  <th>Avg Flat Rate</th>
                                  <th>Total Units</th>
                                  <th>Carpet Area (sqft)</th>

                                </tr>
                              </thead>
                              <tbody>
                                {msg.tableData.map((row, i) => (
                                  <tr key={i}>
                                    <td className="px-4 py-2">{row.year}</td>
                                    <td className="px-4 py-2">{row.final_location}</td>
                                    <td className="px-4 py-2">{row.total_sales_igr}</td>
                                    <td className="px-4 py-2">{row.flat_sold_igr}</td>
                                    <td className="px-4 py-2">{row.flat_weighted_avg_rate}</td>
                                    <td className="px-4 py-2">{row.total_units}</td>
                                    <td className="px-4 py-2">{row.total_carpet_area}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 px-4 py-2 rounded-lg">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about real estate trends..."
              className="flex-1 px-5 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              disabled={loading}
            />
            <button
              onClick={sendQuery}
              disabled={loading || !query.trim()}
              className="bg-blue-600 hover:bg-blue-400 disabled:bg-slate-600 text-white px-6 py-3 rounded-xl shadow-sm transition"

            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealEstateChatbot;