"use client";

import { useState, useEffect, FormEvent } from "react";

interface HistoryRecord {
  query_id: number;
  time: string;
  query_image_file: string;
  result_image_file: string;
  num_humans: number;
}

interface HistoryResponse {
  total: number;
  records: HistoryRecord[];
}

interface ErrorDetail {
  msg: string;
}

interface ErrorResponse {
  detail: ErrorDetail[];
}

function HistoryPage() {
  const [searchValue, setSearchValue] = useState<string>("");
  const [timeMin, setTimeMin] = useState<string>("");
  const [timeMax, setTimeMax] = useState<string>("");
  const [numHumansMin, setNumHumansMin] = useState<number | "">("");
  const [numHumansMax, setNumHumansMax] = useState<number | "">("");
  const [pageIndex, setPageIndex] = useState<number>(1);
  const [pageSize] = useState<number>(10);

  const [goToPageValue, setGoToPageValue] = useState<number>(1);

  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [total, setTotal] = useState<number>(0);

  async function fetchHistory() {
    const params = new URLSearchParams({
      query_id: searchValue,
      time_min: timeMin,
      time_max: timeMax,
      num_humans_min: String(numHumansMin),
      num_humans_max: String(numHumansMax),
      page_index: String(pageIndex),
      page_size: String(pageSize),
    });

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/history?${params.toString()}`,
        {
          method: "GET",
        }
      );

      if (response.ok) {
        const data: HistoryResponse = await response.json();
        setRecords(data.records);
        setTotal(data.total);
      } 
      else {
        const error = await response.json() as ErrorResponse;
        const errorMessage = error.detail.map((err) => err.msg).join("\n");
        alert(errorMessage);
      }
    }

    catch (error) {
      console.error("Error while calling the API:", error);
    };
  }

  async function handleSearch(e: FormEvent) {
    e.preventDefault();

    setPageIndex(1);
    setGoToPageValue(1);

    fetchHistory();
  };

  function handlePrevPage() {
    if (pageIndex > 1) setPageIndex(pageIndex - 1);
  };

  function handleNextPage() {
    if (pageIndex * pageSize < total) setPageIndex(pageIndex + 1);
  };

  function handleGoToPage() {
    if (goToPageValue >= 1 && goToPageValue <= Math.ceil(total / pageSize)) {
      setPageIndex(goToPageValue);
    }
  };

  useEffect(
    () => {
      fetchHistory();
    },
    [pageIndex]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  );
  
  return (
    <div className="h-screen p-6">
      <main className="">
        <h1 className="text-2xl font-bold mb-4"> 
          History
        </h1>

        {/* Search and Filter Section */}
        <form onSubmit={handleSearch} className="mb-6 space-y-4 grid grid-cols-2">
          <div className="grid grid-rows-2 items-center space-x-2 w-full col-span-1">
            <div className="grid grid-rows-2 items-center space-x-2 row-span-1">
              <label className="font-medium row-span-1">Search</label>
              <input
                type="text"
                value={searchValue}
                placeholder = "query_id"
                onChange={(e) => setSearchValue(e.target.value)}
                className="border rounded p-2 text-black w-1/2 row-span-1"
              />
            </div>
            
          </div>

          <div className="grid grid-cols-2 col-span-1 gap-4">
            <div className="grid grid-rows-2 items-center space-x-2 col-span-1">
              <label className="font-medium row-span-1">From Time</label>
              <input
                type="text"
                placeholder="YYYY-MM-DD_HH-MM-SS"
                value={timeMin}
                onChange={(e) => setTimeMin(e.target.value)}
                className="border rounded p-2 text-black w-3/4 row-span-1"
              />
            </div>

            <div className="grid grid-rows-2 items-center space-x-2 col-span-1">
              <label className="font-medium row-span-1">To Time</label>
              <input
                type="text"
                placeholder="YYYY-MM-DD_HH-MM-SS"
                value={timeMax}
                onChange={(e) => setTimeMax(e.target.value)}
                className="border rounded p-2 text-black w-3/4 row-span-1"
              />
            </div>

            <div className="grid grid-rows-2 items-center space-x-2">
              <label className="font-medium row-span-1">Min number of humans</label>
              <input
                type="number"
                value={numHumansMin}
                onChange={(e) =>
                  setNumHumansMin(
                    e.target.value === "" ? "" : parseInt(e.target.value)
                  )
                }
                className="border rounded p-2 text-black w-3/4 row-span-1"
              />
            </div>

            <div className="grid grid-rows-2 items-center space-x-2">
              <label className="font-medium row-span-1">Max number of humans</label>
              <input
                type="number"
                value={numHumansMax}
                onChange={(e) =>
                  setNumHumansMax(
                    e.target.value === "" ? "" : parseInt(e.target.value)
                  )
                }
                className="border rounded p-2 text-black w-3/4 row-span-1"
              />
            </div>
          </div>
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 col-start-2 col-span-1 w-1/2 h-10"
          >
            Search
          </button>
        </form>

        {/* Display Section*/}
        <div className="overflow-x-auto overflow-y-auto h-100">
          <table className="min-w-full border border-gray-200">
            <thead className="bg-black-100">
              <tr>
                <th className="px-4 py-2 border">ID</th>
                <th className="px-4 py-2 border">Time</th>
                <th className="px-4 py-2 border">Query Image File</th>
                <th className="px-4 py-2 border">Result Image File</th>
                <th className="px-4 py-2 border">
                  Number of Detected Humans
                </th>
              </tr>
            </thead>
            <tbody>
              {records.length > 0 ? (
                records.map((record) => (
                  <tr key={record.query_id} className="text-center">
                    <td className="px-4 py-2 border">{record.query_id}</td>
                    <td className="px-4 py-2 border">{record.time}</td>
                    <td className="px-4 py-2 border">{record.query_image_file}</td>
                    <td className="px-4 py-2 border">
                      {record.result_image_file}
                    </td>
                    <td className="px-4 py-2 border">{record.num_humans}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="text-center py-4">
                    No records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Navigation */}
        <div className="flex items-center justify-between mt-6">
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrevPage}
              disabled={pageIndex === 1}
              className="bg-gray-300 text-gray-700 px-3 py-1 rounded disabled:opacity-50"
            >
              Prev
            </button>
            <button
              onClick={handleNextPage}
              disabled={pageIndex * pageSize >= total}
              className="bg-gray-300 text-gray-700 px-3 py-1 rounded disabled:opacity-50"
            >
              Next
            </button>
            <span className="text-gray-700">
              Page {pageIndex} of {Math.ceil(total / pageSize)}
            </span>
          </div>

          {/* Go-to-Page Section */}
          <div className="flex items-center space-x-2">
            <input
              type="number"
              min={1}
              value={goToPageValue}
              onChange={(e) => setGoToPageValue(Number(e.target.value))}
              className="border rounded p-2 w-20 text-black text-center"
            />
            <button
              onClick={handleGoToPage}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Go
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default HistoryPage;
