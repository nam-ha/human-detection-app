"use client";

import { useState } from "react";
import Image from 'next/image';

interface ErrorDetail {
  msg: string;
}

interface ErrorResponse {
  detail: ErrorDetail[];
}

function Home() {
  const [preview, setPreview] = useState<string | null>(null);
  const [outputImage, setOutputImage] = useState<string | null>(null);
  const [numHumans, setNumHumans] = useState<number | null>(null);
  const [confidence_threshold, setConfidenceThreshold] = useState<number>(0.5)

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) 
  {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      const reader = new FileReader();

      reader.onloadend = () => {
        setPreview(reader.result as string);
      };

      reader.readAsDataURL(file);
    }
  }

  function handleConfidenceThresholdChange(event: React.ChangeEvent<HTMLInputElement>) 
  {
    const threshold = event.target.value;
    
    if (threshold === "" || !isNaN(Number(threshold))) {
      setConfidenceThreshold(Number(threshold));
    }
  }

  async function handleDetect() {
    if (!preview) 
    {
      alert("Please select image first!");
      return;
    }

    const requestBody = {
      b64image: preview,
      confidence_threshold: confidence_threshold
    };

    try {
      const response = await fetch("http://localhost:8000/api/v1/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const result = await response.json();
        setOutputImage("data:image/png;base64," + result.b64image as string);
        setNumHumans(result.num_humans);
      } else {
        const error = await response.json() as ErrorResponse;
        const errorMessage = error.detail.map((err) => err.msg).join("\n");
        alert(errorMessage);
      }
    } catch (error) {
      console.error("Error while calling the API:", error);
    }
  }

  return (
    <div className="h-screen p-6">
      <main className="h-full flex w-full gap-6">

        {/* Input Column */}
        <div className="flex flex-col items-center w-full border border-gray-300 p-4 rounded-lg shadow-md">
          <div className="flex-col w-full mb-4">
            <h1 className="text-xl font-bold"> Upload Image </h1>
          </div>

          <div className = "flex-col h-full w-full flex">
            <div className = "h-full w-full flex-col"> 
              {preview && <Image src={preview} alt="Preview" style={{ maxWidth: "100%", height: "auto" }} />}
            </div>
            <div className = "flex-row justify-center">

            </div>
            <input type="file" accept="image/*" onChange={handleFileChange} />
          </div>

          <div>
            <label className = "text-lg font-bold"> Confidence Threshold: </label>
            <input className = "bg-black text-white" type = "number" step = {0.01} max={1.0} min={0.0} onChange = {handleConfidenceThresholdChange} value = {confidence_threshold}/>
            <button 
              onClick={handleDetect}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
              Detect
            </button>
          </div>
        </div>

        {/* Output Column */}
        <div className="flex flex-col items-center w-full border border-gray-300 p-4 rounded-lg shadow-md">
          <div className="flex-col w-full mb-4">
            <h1 className="text-xl font-bold"> Result </h1>
          </div>

          <div className="h-full w-full flex-col">
            {outputImage && <Image src={outputImage} alt="Result" style={{ maxWidth: "100%", height: "auto" }} />}
          </div>
          
          <p className="text-lg font-semibold"> Number of people in the image: <span className="text-lg">{numHumans}</span> </p>
          
        </div>
      </main>
    </div>
  );
}

export default Home;
