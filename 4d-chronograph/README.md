# 🕵️‍♂️ 4D Chronograph: Detective's Investigation Prototype

Welcome to the **4D Chronograph**. This tool is designed to help senior detectives sort through unstructured case data (CCTV logs, phone records, bank transfers) by visualizing them in a unified, time-based relationship graph.

Instead of a static "red string" board, this is a **4-dimensional interface** where the 4th dimension is **Time**.

## 🚀 Quick Start

### 1. Prerequisites
- [Node.js](https://nodejs.org/) (v18 or higher)
- npm (comes with Node)

### 2. Installation
Clone the repository (or navigate to the folder) and install dependencies:
```bash
npm install
```

### 3. Run the Prototype
Start the development server:
```bash
npm run dev
```
The application will be available at `http://localhost:5173`.

---

## 🛠 Features

### 1. The Evidence Board (Main View)
The central grid is your digital corkboard.
- **Nodes:** Represent entities discovered in the investigation.
    - 🔵 **Blue:** Persons of Interest (Suspects).
    - 🟢 **Green:** Locations (Crime scenes, hideouts).
    - 🟡 **Yellow:** Tangible Evidence (Phones, financial records).
- **Edges (The "Red Strings"):** Represent events or relationships. The label on the line tells you *what* happened (e.g., "Called", "Seen at", "Beneficiary").

### 2. The Chrono-Scrubber (Timeline)
Located at the bottom of the screen. 
- **Time Scrubbing:** Drag the slider to "move through time."
- **Dynamic Discovery:** As you move the slider forward, new entities and connections will appear on the board exactly when they were discovered or when the event occurred.
- **Rewind:** Move the slider back to clear the noise and see only the state of the investigation at an earlier hour.

### 3. The Dossier Panel (Side Panel)
Clicking on any node or connection on the board pulls up the **Dossier**.
- **Raw Evidence Transcript:** See the "unstructured" source data that generated the visual connection. This might be a snippet of a CCTV transcript, a row from a CSV phone log, or a digital bank ledger entry.

---

## 📂 Mock Case: "Operation Midnight Shadow"

The prototype comes pre-loaded with a simulated investigation to demonstrate the workflow:

1.  **20:00:** The investigation begins with two primary suspects: **Victor Vance** and **Elena Rostova**.
2.  **22:00:** Vance is spotted at **Pier 42** (Source: CCTV Log).
3.  **23:00:** A **Burner Phone** is recovered. Fingerprint analysis links it to Vance.
4.  **23:15:** Telecom records show the burner phone was used to call **Elena Rostova**.
5.  **01:00:** A **$2M transfer** is flagged at the **Downtown Bank**.
6.  **01:30:** The money is traced to a proxy account controlled by **Rostova**.

---

## 🏗 Technical Stack
- **Framework:** React + TypeScript (Vite)
- **Visualization:** `vis-network` (Graph rendering)
- **Icons:** `lucide-react`
- **Styling:** Vanilla CSS (Dark-themed "Detective UI")

---

## 📝 License
This is a functional prototype created for the AIVENTRA Visualisation project.
