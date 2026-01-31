# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (One Time)

```bash
pip install -r requirements.txt
```

### Step 2: Start Backend Server

Double-click `run_backend.bat` or run:
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Wait until you see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 3: Start Frontend Dashboard

**In a NEW terminal**, double-click `run_frontend.bat` or run:
```bash
streamlit run frontend/app.py --server.port 8501
```

Your browser will automatically open to: http://localhost:8501

---

## 📋 First Upload

1. Click **Upload** page (📤)
2. Upload file: `IncentiveWorking_Krishiv.xlsx`
3. Click **Process File**
4. Wait for completion (~10-30 seconds)
5. Download results or view in Dashboard

---

## ✅ Verify Setup

Run verification script:
```bash
python verify_setup.py
```

This checks:
- ✅ Python version (3.8+)
- ✅ All packages installed
- ✅ Files and directories present
- ✅ Database can be created

---

## 🆘 Troubleshooting

### "Python was not found"
➡️ Install Python from https://python.org (check "Add to PATH")

### "Module not found"
➡️ Run: `pip install -r requirements.txt`

### "Cannot connect to backend"
➡️ Make sure backend is running first (step 2)

### "Port already in use"
➡️ Change ports in `.env` file

---

## 📚 More Help

- **Detailed Setup**: See `SETUP_GUIDE.md`
- **Project Docs**: See `README.md`
- **API Docs**: http://localhost:8000/docs (when backend is running)

---

## 🎯 Expected Results

When you process `IncentiveWorking_Krishiv.xlsx`:

- **Total Incentives**: ₹5,23,929.52
- **Transactions**: 8,535
- **Employees**: 147
- **Stores**: 14

If your results match these numbers, everything is working correctly! ✅
