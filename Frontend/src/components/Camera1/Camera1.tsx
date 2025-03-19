import { useEffect, useState } from "react";
import "./Camera1.css"

function Camera1() {
  const [imageSrc, setImageSrc] = useState("");

  useEffect(() => {
    const ws = new WebSocket("ws://localhost/ws/camera1"); 

    ws.onopen = () => {
      ws.send("frontend")
    }

    ws.onmessage = (event) => {

      try 
      {
        const data = JSON.parse(event.data);

        if (data.camera1) 
        {
          setImageSrc(`data:image/jpeg;base64,${data.camera1}`);
        }
      } 

      catch (error) 
      {
        console.error("Eroare la procesarea live-feed-ului de pe camera 1:", error);
      }

    };

    ws.onerror = (error) => console.error("Eroare Webbsocket:", error);
    ws.onclose = () => console.log("WebSocket-ul Camera 1 este inchisa");

    return () => ws.close();
  }, []);

  return (
    <div className="camera1-container">
      <h2>Camera 1 Live Feed</h2>
      {imageSrc ? (
        <img src={imageSrc} alt="Camera 1 Feed" />
      ) : (
        <p className="loading">Loading...</p> 
      )}    
      </div>
  );
}

export default Camera1;
