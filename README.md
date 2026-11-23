# 💎 Diamond ERP - Backend API Setup & Deployment Guide

This guide provides a direct, step-by-step walkthrough to configure, connect, and run the **FastAPI Backend Service** on an Ubuntu/Debian Linux VM (e.g., Azure VM, AWS EC2) without Docker, as well as on your local machine.

---

## 📁 Repository Structure

```
backend/python-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py             # Login, profile & JWT token generation
│   │       │   ├── diamonds.py         # Diamond inventory & parent-child split genealogy
│   │       │   ├── manufacturing.py    # Work orders & weight-loss audit tracking
│   │       │   └── dashboard.py        # CTO & Admin analytics KPIs
│   │       └── api_router.py           # Consolidated API v1 router
│   ├── core/
│   │   ├── config.py                   # Pydantic Settings & environment variables
│   │   ├── database.py                 # SQLAlchemy engine, connection pooling & get_db
│   │   └── security.py                 # Bcrypt password hashing & JWT token handling
│   ├── middleware/
│   │   └── rbac.py                     # Role-Based Access Control dependencies
│   ├── models/                         # SQLAlchemy 2.0 ORM models (Auth, Inventory, Manufacturing, Handovers)
│   ├── schemas/                        # Pydantic v2 schemas for request/response validation
│   └── main.py                         # FastAPI app factory, CORS & health checks
├── requirements.txt                    # Python dependencies
├── .env.example                        # Template environment configuration
└── README.md                           # This guide
```

---

## Step-by-Step Linux / Azure VM Deployment Guide

Follow these numbered steps to run the FastAPI backend service directly on your Linux VM:

### 1. Open Port 8000 in Azure NSG / Firewall

In the Azure Portal (or your cloud firewall console):
1. Navigate to your Virtual Machine > **Networking** > **Network settings** (or your **Network Security Group**).
2. Under **Inbound port rules**, click **Add inbound rule**:
   - **Destination port ranges**: `8000`
   - **Protocol**: `TCP`
   - **Action**: `Allow`
   - **Priority**: `1010`
   - **Name**: `Allow-Port-8000`
3. Ensure **Port 22 (SSH)** is also allowed.

---

### 2. Connect to the VM via SSH

Open your terminal or PowerShell and connect:

```bash
ssh azureuser@<YOUR_VM_PUBLIC_IP>
```

---

### 3. Install Python 3, Pip, Virtualenv & Git

Update package lists and install required runtime dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

Verify Python installation:
```bash
python3 --version
```

---

### 4. Clone Repository & Navigate to Backend

```bash
# Clone your project repository (or copy files)
git clone <YOUR_REPO_URL>

# Navigate into the python-api directory
cd dimand-erp/backend/python-api
```

---

### 5. Configure Database Connection (`.env`)

Create your `.env` configuration file from the template:

```bash
cp .env.example .env
nano .env
```

Configure your **`DATABASE_URL`** with your PostgreSQL connection details:

#### For Self-Managed PostgreSQL on VM (IaaS):
```env
DATABASE_URL=postgresql://postgres:<PASSWORD>@<DB_VM_PUBLIC_IP>:5432/diamond_erp_db
```
*(If PostgreSQL is running on the **same VM**, you can use `localhost`):*
```env
DATABASE_URL=postgresql://postgres:<PASSWORD>@localhost:5432/diamond_erp_db
```

#### For Azure Database for PostgreSQL Flexible Server (PaaS):
```env
DATABASE_URL=postgresql://diamondadmin:<PASSWORD>@<SERVER_NAME>.postgres.database.azure.com:5432/diamond_erp_db?sslmode=require
```

> **Important URL-Encoding Tip:** If your database password contains special characters (such as `@`, `#`, `:`, `/`), you must URL-encode them:
> - `@` becomes `%40`
> - `#` becomes `%23`
> - `:` becomes `%3A`
> - `/` becomes `%2F`

Save and exit `nano` (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

### 6. Create Virtual Environment & Install Dependencies

It is best practice to use a virtual environment to prevent package conflicts:

```bash
# Create virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

*(Note: If you are not using a virtual environment on Ubuntu 24.04+, append `--break-system-packages` to the pip install command).*

---

### 7. Run the Application with Uvicorn

Make sure your virtual environment is active (`(venv)` appears in prompt).

#### Option A: Run in Foreground (Testing & Debugging)
Use this to verify the application starts without errors and connects to PostgreSQL:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*(Press `Ctrl+C` to stop).*

#### Option B: Run in Background (Keeps running after SSH disconnect)
To keep the API running continuously in the background after you close your terminal:

```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

* **Check live logs:**
  ```bash
  tail -f app.log
  ```
* **Verify running process:**
  ```bash
  ps aux | grep uvicorn
  ```
* **Stop the background service:**
  ```bash
  pkill -f uvicorn
  ```

---

### 8. Test in Browser & Verify Endpoints

Open your browser and navigate to:

1. **Swagger Interactive API Documentation:**
   ```text
   http://<YOUR_VM_PUBLIC_IP>:8000/docs
   ```
2. **Health Check Endpoint:**
   ```text
   http://<YOUR_VM_PUBLIC_IP>:8000/health
   ```
   *Expected response:*
   ```json
   {
     "status": "healthy",
     "service": "Diamond Manufacturing & Business Management API",
     "environment": "development",
     "api_version": "v1"
   }
   ```
3. **Test Login via Swagger UI:**
   * Go to `http://<YOUR_VM_PUBLIC_IP>:8000/docs`.
   * Open `POST /api/v1/auth/login`.
   * Click **Try it out** and submit:
     ```json
     {
       "email": "admin@diamond-erp.local",
       "password": "Admin@123"
     }
     ```
   * Copy the returned `access_token` and click the green **Authorize** button at the top to test authenticated endpoints (such as `GET /api/v1/dashboard/stats`).

---

## 🔑 Default Seeded Accounts

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@diamond-erp.local` | `Admin@123` | Full access across all departments and portals |
| **Chief Technology Officer (CTO)** | `cto@diamond-erp.local` | `Admin@123` | Monitoring, logs, system analytics & configs |

---

## 💻 Quick Setup for Local Development (Windows / macOS)

If you are developing locally on your laptop:

```powershell
# Navigate to backend directory
cd backend/python-api

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
copy .env.example .env         # On Mac/Linux: cp .env.example .env

# Start dev server with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Local Swagger UI will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)
