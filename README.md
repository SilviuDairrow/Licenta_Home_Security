#### English
# Bachelor's Thesis: Local Survelliance System based on Raspberry Pi 4
Developed an end-to-end on-premises surveillance system based on Raspberry Pi 4 to process real-time data from IoT sensors (temperature, humidity, distance) and HD cameras. This solution eliminates cloud dependencies, enhances the control over private data. The system features facial recognition for intruder detection, a secure React dashboard for live monitoring, and distributed storage for scalable data handling.

Core tehnologies:
- Hardware: Raspberry Pi 4 (8GB RAM), DHT11 & HC-SR04 sensors, Microsoft LifeCam HD-3000
- Backend: Dockerized microservices (FastAPI), Kafka for sensor data, WebSockets for video streaming
- AI/Storage: InsightFace facial recognition (98.5% accuracy), SeaweedFS (distributed storage), MongoDB
- Frontend: React + Vite dashboard for real-time visualisation of sensors data and video feed
- Security: JWT (HS512) authentication, NGINX reverse proxy, CORS policies

Key features:
- Real-Time Monitoring:
  1. Live video streaming via WebSockets 
  2. Kafka-based communication for the sensor data
  3. Dashboard displaying a gallery of all new detected faces, temperature, humidity, distance

- Facial Recognition:
  1. Implemented InsightFace model for detecting and classifying faces based on "known" vs. "unknown" ("jupani" vs "straini")
  2. All detected uknown faces are stored in SeaweedFS

- Security:
  1. Access control based on JWT tokens
  2. Modular design so new sensors and cameras can be integrated via GPIO/Kafka topic updates
  3. Self-healing: Auto-reconnect for Kafka (5s) and WebSockets (3s)





#### Română
# Lucrare de Licență: Sistem de supraveghere pe bază de Raspberry Pi 4

Am dezvoltat un sistem de supraveghere on-premises integral bazat pe Raspberry Pi 4 pentru procesarea datelor în timp real de la diferiți senzori IoT (temperatură, umiditate, distanță) și camere HD. Această Lucrare are ca scop eliminarea dependenței de cloud și oferă control total asupra datelor personale. Sistemul integrează un model de recunoaștere facială pentru detectarea persoanelor necunoscute, un dashboard React securizat pentru monitorizarea live, și stocare distribuită pentru gestionarea scalabilă a datelor.

Tehnologii cheie:

- Hardware: Raspberry Pi 4 (8GB RAM), senzori IoT DHT11 & HC-SR04, Microsoft LifeCam HD-3000
- Backend: Microservicii containerizate (FastAPI), Kafka pentru transmiterea datelor de pe senzori, WebSockets pentru streaming video
- AI/Stocare: Modelul de recunoaștere facială InsightFace (98.5% acuratețe), SeaweedFS (stocare distribuită), MongoDB
- Frontend: Dashboard React + Vite pentru vizualizarea live a datelor senzorilor și a fluxului video
- Securitate: Autentificare JWT (HS512), reverse proxy NGINX, CORS

Funcționalități:

- Monitorizarea datelor în timp real:
  1. Transmisie video live prin WebSockets
  2. Comunicarea datelor senzorilor se bazează pe topic-uri Kafka
  3. Dashboard cu galeria noilor fețe detectate, temperatură, umiditate și distanță

- Recunoaștere facială:
  1. Model InsightFace pentru clasificarea "cunoscuților" (jupâni) vs "necunoscuților" (străini)
  2. Stocare automată a fețelor necunoscute în SeaweedFS

- Securitate și modularitate:
  1. Control acces bazat pe token-uri JWT (HS512)
  2. Design modular astfel încât implementarea unor senzori/camere noi se poate realiza prin actualizarea GPIO și a topic-urilor Kafka
  3. Self-healing: Reconectare automată Kafka (5s) și WebSockets (3s)
