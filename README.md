# Netmig Application

Netmig is a powerful **graphical user interface (GUI)** tool designed to act as a centralized hub for **network migration automation**. It consolidates reusable tools and scripts into a unified platform, enabling seamless execution, monitoring, and management throughout every stage of the migration lifecycle.

With an emphasis on flexibility and ease of use, Netmig empowers engineers to integrate their own scripts alongside built-in automation capabilities — transforming manual, fragmented workflows into a streamlined, user-friendly automation suite.

---

## 🚀 Key Features

🖥 **Interactive GUI (Qt5)**  
Simplifies script execution through an intuitive interface — no more terminal commands.

🧰 **Built-in Tools**  
Comes with a growing collection of preloaded scripts designed for network discovery, configuration, verification, and troubleshooting.

➕ **Add Local Scripts**  
Easily import and run your own Python scripts within Netmig's environment.

🌐 **Remote Script Execution**  
Manage and execute scripts on remote devices directly from the UI.

🔐 **Security**  
Netmig uses **Fernet symmetric encryption** (via the `cryptography` library) to securely store sensitive information like passwords, with encryption keys protected in the system keyring.

📈 **Telemetry & Logging**  
Full visibility into script usage, execution history, and user actions — great for debugging and optimization.

---

## 🛠 Getting Started

### 🔧 Installation (Quick Steps)

1. **Install Prerequisites**
   - Python 3.7+ → Check with `python --version`
   - pip → Check with `pip --version` or install:  
     ```bash
     python -m ensurepip --upgrade
     ```

2. **Clone and Set Up Project**
   ```bash
   mkdir Netmig && cd Netmig
   mkdir netmig-app
   # Download and extract source into app/
   ```

3. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Activate it:
   # macOS/Linux
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r netmig-app/requirements.txt
   ```

5. **Launch Netmig**
   ```bash
   python netmig-app
   ```

✅ That’s it! You’re ready to automate with Netmig.

---

## 📄 License

MIT License © 2024 Sanjeev Krishna

---