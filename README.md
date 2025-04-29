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
- ✔️ Unifies and streamlines script workflows  
- ✔️ Simplifies management of multiple scripts and devices  
- ✔️ Makes automation accessible to more team members  
- ✔️ Provides insights for continuous improvement

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

## 📬 Contributions

**Author:** Sanjeev Krishna  

Want to add a new script or tool? Fork the repo, or contact the admin team to publish a new module.

---

## 📄 License

MIT License © 2024 Sanjeev Krishna
