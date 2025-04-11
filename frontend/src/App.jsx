import { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const STATUS_COLORS = {
  "Sangat Baik": "#34D399",
  Baik: "#A78BFA",
  Cukup: "#60A5FA",
  Buruk: "#FBBF24",
  "Sangat Buruk": "#F87171",
};

const App = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchData = () => {
      axios
        .get("http://127.0.0.1:5000/api/network-status")
        .then((res) => {
          if (isMounted) {
            setData(res.data);
            setLoading(false);
            console.log("Data updated:", res.data);
          }
        })
        .catch((err) => {
          console.error("Error ambil data:", err);
          if (isMounted) setLoading(false);
        });
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const pieData = () => {
    const statusCounts = data.reduce((acc, curr) => {
      acc[curr.status] = (acc[curr.status] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(statusCounts).map(([name, value]) => ({
      name,
      value,
    }));
  };

  const getStatusBadge = (status) => {
    const baseStyle =
      "px-3 py-1 text-sm font-semibold rounded-full border shadow-md inline-block";

    switch (status) {
      case "Sangat Baik":
        return (
          <span
            className={`${baseStyle} bg-green-400 text-white border-green-500`}>
            {status}
          </span>
        );
      case "Baik":
        return (
          <span
            className={`${baseStyle} bg-purple-400 text-white border-purple-500`}>
            {status}
          </span>
        );
      case "Cukup":
        return (
          <span
            className={`${baseStyle} bg-blue-400 text-white border-blue-500`}>
            {status}
          </span>
        );
      case "Buruk":
        return (
          <span
            className={`${baseStyle} bg-yellow-300 text-black border-yellow-400`}>
            {status}
          </span>
        );
      case "Sangat Buruk":
        return (
          <span className={`${baseStyle} bg-red-500 text-white border-red-600`}>
            {status}
          </span>
        );
      default:
        return (
          <span
            className={`${baseStyle} bg-gray-300 text-black border-gray-400`}>
            {status}
          </span>
        );
    }
  };

  return (
    <section className="bg-white dark:bg-gray-900 min-h-screen">
      <div className="py-8 px-4 mx-auto max-w-screen-xl lg:py-16">
        {/* JUDUL */}
        <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 md:p-12 mb-8">
          <h1 className="text-gray-900 text-center dark:text-white text-3xl md:text-5xl font-extrabold mb-2">
            Identifikasi Peforma Jaringan Menggunakan Algorithma Naive Bayes
            Pada Hostpot UPI-YPTK Padang
          </h1>
        </div>

        {/* BAR CHART */}
        <div className="grid md:grid-cols-1 gap-8">
          <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 md:p-12">
            <a
              href="#"
              className="bg-green-100 text-green-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded-md dark:bg-gray-700 dark:text-green-400 mb-2">
              <svg
                className="w-2.5 h-2.5 me-1.5"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 18 18">
                <path d="M17 11h-2.722L8 17.278a5.512 5.512 0 0 1-.9.722H17a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1ZM6 0H1a1 1 0 0 0-1 1v13.5a3.5 3.5 0 1 0 7 0V1a1 1 0 0 0-1-1ZM3.5 15.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2ZM16.132 4.9 12.6 1.368a1 1 0 0 0-1.414 0L9 3.55v9.9l7.132-7.132a1 1 0 0 0 0-1.418Z" />
              </svg>
              Performa
            </a>
            <h2 className="text-gray-900 dark:text-white text-3xl font-extrabold mb-3 mt-2">
              Visual Performa Jaringan
            </h2>
            <div className="w-full h-[300px] mt-4">
              {!loading && data.length > 0 ? (
                <ResponsiveContainer>
                  <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="ip" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar
                      dataKey="throughput_mbps"
                      fill="#3B82F6"
                      name="Throughput"
                    />
                    <Bar dataKey="delay_ms" fill="#F59E0B" name="Delay" />
                    <Bar dataKey="jitter_ms" fill="#10B981" name="Jitter" />
                    <Bar
                      dataKey="packet_loss_percent"
                      fill="#EF4444"
                      name="Packet Loss"
                    />
                    <Bar
                      dataKey="availability_percent"
                      fill="#A78BFA"
                      name="Availability"
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-100 text-center">
                  🔄 Memuat grafik performa...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* PIE CHART */}
        <div className="grid md:grid-cols-1 gap-8 mt-10">
          <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 md:p-12">
            <a
              href="#"
              className="bg-green-100 text-green-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded-md dark:bg-gray-700 dark:text-green-400 mb-2">
              <svg
                className="w-2.5 h-2.5 me-1.5"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 18 18">
                <path d="M17 11h-2.722L8 17.278a5.512 5.512 0 0 1-.9.722H17a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1ZM6 0H1a1 1 0 0 0-1 1v13.5a3.5 3.5 0 1 0 7 0V1a1 1 0 0 0-1-1ZM3.5 15.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2ZM16.132 4.9 12.6 1.368a1 1 0 0 0-1.414 0L9 3.55v9.9l7.132-7.132a1 1 0 0 0 0-1.418Z" />
              </svg>
              Status
            </a>
            <h2 className="text-gray-900 dark:text-white text-3xl font-extrabold mb-3 mt-2">
              Visual Status Jaringan (Pie Chart)
            </h2>
            <div className="w-full h-[300px] mt-4">
              {!loading && data.length > 0 ? (
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={pieData()}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label>
                      {pieData().map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={STATUS_COLORS[entry.name]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-100 text-center">
                  🔄 Memuat grafik status...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* TABEL */}
        <div className="grid md:grid-cols-1 gap-8 mt-5">
          <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 md:p-12">
            <a
              href="#"
              className="bg-green-100 text-green-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded-md dark:bg-gray-700 dark:text-green-400 mb-2">
              <svg
                className="w-2.5 h-2.5 me-1.5"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 18 18">
                <path d="M17 11h-2.722L8 17.278a5.512 5.512 0 0 1-.9.722H17a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1ZM6 0H1a1 1 0 0 0-1 1v13.5a3.5 3.5 0 1 0 7 0V1a1 1 0 0 0-1-1ZM3.5 15.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2ZM16.132 4.9 12.6 1.368a1 1 0 0 0-1.414 0L9 3.55v9.9l7.132-7.132a1 1 0 0 0 0-1.418Z" />
              </svg>
              Identifikasi
            </a>
            <h2 className="text-gray-900 dark:text-white text-3xl font-extrabold mb-3 mt-2">
              Data Identifikasi Peforma Jaringan
            </h2>
            <div className="relative overflow-x-auto shadow-md sm:rounded-lg">
              {loading ? (
                <div className="text-center text-gray-100 py-10">
                  🔄 Memuat data...
                </div>
              ) : (
                <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
                  <thead className="text-xs text-center text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                    <tr>
                      <th className="px-6 py-3">No</th>
                      <th className="px-6 py-3">IP Address</th>
                      <th className="px-6 py-3">Throughput</th>
                      <th className="px-6 py-3">Delay</th>
                      <th className="px-6 py-3">Jitter</th>
                      <th className="px-6 py-3">Packet Loss</th>
                      <th className="px-6 py-3">Availability</th>
                      <th className="px-6 py-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((row, index) => (
                      <tr
                        key={index}
                        className="text-center bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                        <th className="px-6 py-4">{index + 1}</th>
                        <th className="px-6 py-4">{row.ip}</th>
                        <td className="px-6 py-4">
                          {row.throughput_kbps < 1000
                            ? row.throughput_kbps + " Kbps"
                            : row.throughput_mbps + " Mbps"}
                        </td>
                        <td className="px-6 py-4">{row.delay_ms} ms</td>
                        <td className="px-6 py-4">{row.jitter_ms} ms</td>
                        <td className="px-6 py-4">
                          {row.packet_loss_percent} %
                        </td>
                        <td className="px-6 py-4">
                          {row.availability_percent} %
                        </td>
                        <td className="px-6 py-4">
                          {getStatusBadge(row.status)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default App;
