# 🚗 Car Maintenance Assistant

A simple and practical car maintenance tracking tool that helps you keep track of your vehicle's maintenance history, so you'll never miss a service interval again.

---

## ✨ Features

- 🚙 **Multi-vehicle support** - Add and manage multiple cars
- 📋 **Maintenance item tracking** - Built-in common items with custom support
- ⏰ **Smart reminders** - Auto-calculate next service based on km or time
- 💰 **Cost tracking** - Record expenses for each maintenance
- 📊 **Statistics** - View total spending and maintenance history
- 🖥️ **Clean interface** - Single page design, no complex setup

---

## 🛠️ Quick Start

### Requirements

- Python 3.7+
- pip

### Installation

**1. Clone the project**
```bash
git clone https://github.com/zhengxin-peng-rdsec/car-maintenance-assistant.git
cd car-maintenance-assistant
```

**2. Install dependencies**
```bash
pip install flask
```

**3. Start the server**
```bash
python app.py
```

**4. Access**
Open your browser: `http://localhost:5000`

---

## 📁 Project Structure

```
car-maintenance-assistant/
├── app.py              # Main program (backend + frontend + database)
├── index.html          # Frontend page (backup)
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## 🔧 Deployment Options

### Option 1: Local Run (quick try)

```bash
python app.py
```

### Option 2: Background Run + Auto-restart

```bash
# Run in background with nohup
nohup python app.py > app.log 2>&1 &

# Check process
ps aux | grep app.py

# Restart
pkill -f app.py && nohup python app.py > app.log 2>&1 &
```

### Option 3: systemd Service (Linux)

Create service file `/etc/systemd/system/car-maintenance.service`:

```ini
[Unit]
Description=Car Maintenance Assistant
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/car-maintenance-assistant
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable car-maintenance
sudo systemctl start car-maintenance
```

### Option 4: Nginx Reverse Proxy (remote access)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🚀 Usage Guide

### Add a vehicle
1. Click "Add Vehicle" button
2. Fill in brand, model, plate number, etc.
3. Enter purchase date and current mileage

### Record maintenance
1. Select a vehicle
2. Click "Record Maintenance"
3. Choose maintenance item, enter date and mileage
4. Optionally add cost and notes

### Service status colors
- 🔴 **Red** - Overdue, needs service
- 🟡 **Yellow** - Approaching service interval (< 500km or < 30 days remaining)
- 🟢 **Green** - Normal, within service interval

---

## ⚙️ Customization

Edit the configuration at the top of `app.py`:

```python
app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'car_maintenance.db')

# Change default port
# app.run(host='0.0.0.0', port=5000)
```

---

## ❓ FAQ

**Q: Error `Module not found: flask`**
```bash
pip install flask
```

**Q: Where is data stored?**
Database file: `car_maintenance.db` in the same directory

**Q: How to backup data?**
```bash
# Just copy the database file
cp car_maintenance.db car_maintenance.db.backup
```

**Q: How to reset data?**
```bash
rm car_maintenance.db
python app.py  # Will auto-create new empty database
```

---

## 📝 License

MIT License - Use and modify freely 😄

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**Questions? Open an Issue**
