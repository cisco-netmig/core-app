# Netmig – Automation Suite

Netmig is a powerful **graphical user interface (GUI)** tool designed to act as a centralized hub for **network migration automation**. It consolidates reusable tools and scripts into a unified platform, enabling seamless execution, monitoring, and management throughout every stage of the migration lifecycle.

With an emphasis on flexibility and ease of use, Netmig empowers engineers to integrate their own scripts alongside built-in automation capabilities — transforming manual, fragmented workflows into a streamlined, user-friendly automation suite.

---

🚀 Key Features

🖥 **Interactive GUI (Qt5)**
Simplifies script execution through an intuitive interface — no more terminal commands.

🧰 **Built-in Tools**
Comes with a growing collection of preloaded scripts designed for network discovery, configuration, verification, and troubleshooting.

➕ **Add Local Scripts**
Easily import and run your own Python scripts within Netmig's environment.

🌐 **Remote Script Execution**
Manage and execute scripts on remote devices directly from the UI.

📈 **Telemetry & Logging**
Full visibility into script usage, execution history, and user actions — great for debugging and optimization.

---

## 💡 Why Netmig?

Many engineers at Cisco and similar environments build individual automation scripts. However, these often remain:
- Isolated from broader teams
- Hard to share or reuse
- Complex to run from the command line

Netmig solves these problems by:
- Centralizing all scripts under a common GUI
- Enabling easier execution, even for non-technical users
- Improving team collaboration through a shared, managed platform

---

## 🧩 Challenges Solved

- ⏱ **Manual Effort**: Automates repetitive migration steps  
- 🔄 **Script Duplication**: Central repo prevents reinvention  
- ⚙️ **Complex CLI Execution**: Run everything through a simple UI  
- 🧭 **Dependency Chaos**: Easier deployment with minimal friction  
- 🔍 **Debugging**: Logging + telemetry provide real-time visibility

---

## ✅ Benefits & Outcomes

- ✔️ Reduces human effort
- ✔️ Unifies and streamlines script workflows[README.md](..%2F..%2F..%2F..%2FDownloads%2FREADME.md)
- ✔️ Simplifies management of multiple scripts and devices
- ✔️ Makes automation accessible to more team members
- ✔️ Provides insights for continuous improvement

---

## 🛠 Getting Started

## 📋 Prerequisites

1. **Python 3.7 or Above**  
   Check if Python is installed:  
   ```bash
   python --version
   ```  
   If not, download it from [python.org](https://www.python.org).

2. **pip (Python Package Manager)**  
   Verify installation:  
   ```bash
   pip --version
   ```  
   If missing, install it with:  
   ```bash
   python -m ensurepip --upgrade
   ```

---

## 🛠 Step-by-Step Installation

### 1. Set Up Directory Structure

Create the following folder layout:
```
Netmig/
└── app/
```

### 2. Download the Source Code

- Visit: [Netmig GitHub Repository](https://wwwin-github.cisco.com/sanjeekr/Netmig)  
- Click the green **Code** button → **Download ZIP**  
- Extract the ZIP contents into the `app/` directory

### 3. Set Up a Virtual Environment

Open a terminal and navigate to the `Netmig` directory:

```bash
python -m venv venv
```

Activate the virtual environment:

- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows:**
  ```cmd
  venv\Scripts\activate
  ```

Your directory structure should now look like:
```
Netmig/
├── app/
└── venv/
```

### 4. Install Dependencies

Install required Python packages:

```bash
pip install -r app/utils/requirements.txt
```

### 5. Run the Netmig Tool

Start the application:

```bash
python app
```

---

✅ **That's it!**  
You have successfully installed and launched the **Netmig** tool.

---

---

## 📬 Contributions

**Author:** Sanjeev Krishna  

Want to add a new script or tool? Fork the repo, or contact the admin team to publish a new module.

---


## 📄 License

MIT License © 2024 Sanjeev Krishna
