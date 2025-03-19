import { useEffect, useState } from "react";
import "./Camera2.css"

function Camera2() {
  const [imageSrc, setImageSrc] = useState("");

  useEffect(() => {
    const ws = new WebSocket("ws://localhost/ws/camera2"); 

    ws.onopen = () => {
      ws.send("frontend")
    }


    ws.onmessage = (event) => {
      
      try
      {
        const data = JSON.parse(event.data);

        setImageSrc(`data:image/jpeg;base64,${data.camera2}`); 
      }

      catch (error)
      {
        console.error("Eroare la procesarea live-feed-ului de pe camera 2:", error);
      }
    };

    ws.onerror = (error) => console.error("Eroare Webbsocket:", error);
    ws.onclose = () => console.log("WebSocket-ul Camera 2 este inchisa");

    return () => ws.close();
  }, []);

  return (
    <div className = "camera2-container">
      <h2>Camera 2 Live Feed</h2>
      {imageSrc ? (
        <img src={imageSrc} alt = "Camera 2 Feed" />
      ) : (
        <p className = "loading"> Loading...</p> 
      )}    
      </div>
  );

}

export default Camera2;
