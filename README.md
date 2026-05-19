# 🚗 Car Maintenance Assistant / 汽车保养助手

<!-- 语言切换 -->
<div class="lang-switch" style="margin:20px 0;">
  <button onclick="switchLang('zh')" id="btn-zh" style="padding:8px 16px;margin-right:10px;cursor:pointer;">🇨🇳 中文</button>
  <button onclick="switchLang('en')" id="btn-en" style="padding:8px 16px;cursor:pointer;">🇺🇸 English</button>
</div>

<style>
.lang-switch button { border:1px solid #ccc; background:#fff; border-radius:4px; }
.lang-switch button.active { background:#007bff; color:#fff; border-color:#007bff; }
</style>

<!-- 中文内容 -->
<div id="zh-content">
  
# 🚗 汽车保养助手

一个简单实用的汽车保养记录管理工具，帮助你跟踪车辆保养历史，再也不会错过保养周期。

---

## ✨ 功能特性

- 🚙 **多车辆管理** - 支持添加和管理多辆汽车
- 📋 **保养项目追踪** - 内置常用保养项目，支持自定义
- ⏰ **智能提醒** - 根据公里数或时间自动计算下次保养时间
- 💰 **费用记录** - 记录每次保养的费用
- 📊 **统计报表** - 查看保养总支出和爱车的保养历程
- 🖥️ **简洁界面** - 单页面设计，无需复杂配置

---

## 🛠️ 快速部署

### 环境要求
- Python 3.7+
- pip

### 安装步骤

**1. 克隆项目**
```bash
git clone https://github.com/zhengxin-peng-rdsec/car-maintenance-assistant.git
cd car-maintenance-assistant
```

**2. 安装依赖**
```bash
pip install -r requirements.txt
```

**3. 启动服务**
```bash
python app.py
```

**4. 访问**
打开浏览器访问：`http://localhost:5000`

---

## 🔧 部署方式

### 方式一：本地运行
```bash
python app.py
```

### 方式二：后台运行
```bash
nohup python app.py > app.log 2>&1 &
```

### 方式三：systemd 服务（Linux）

创建服务文件 `/etc/systemd/system/car-maintenance.service`:

```ini
[Unit]
Description=Car Maintenance Assistant
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/car-maintenance-assistant
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```
然后:
```bash
sudo systemctl daemon-reload
sudo systemctl enable car-maintenance
sudo systemctl start car-maintenance
```

### 方式四：Nginx 反向代理
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

## ❓ 常见问题

**Q: 报错 `Module not found: flask`**
```bash
pip install flask
```

**Q: 数据存在哪里？**
`car_maintenance.db` 在同目录

**Q: 如何备份？**
```bash
cp car_maintenance.db backup.db
```

---

## 📝 License
MIT License

</div>

<!-- 英文内容 -->
<div id="en-content" style="display:none;">

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
git clone https://github.com/your-username/car-maintenance-assistant.git
cd car-maintenance-assistant
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Start the server**
```bash
python app.py
```

**4. Access**
Open browser: `http://localhost:5000`

---

## 🔧 Deployment

### Option 1: Local Run
```bash
python app.py
```

### Option 2: Background Run
```bash
nohup python app.py > app.log 2>&1 &
```

### Option 3: systemd Service (Linux)

Create service file `/etc/systemd/system/car-maintenance.service`:

```ini
[Unit]
Description=Car Maintenance Assistant
After=network.target

[Service]
Type=simple
User=your-username
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

### Option 4: Nginx Reverse Proxy
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

## ❓ FAQ

**Q: Error `Module not found: flask`**
```bash
pip install flask
```

**Q: Where is data stored?**
`car_maintenance.db` in same directory

**Q: How to backup?**
```bash
cp car_maintenance.db backup.db
```

---

## 📝 License
MIT License

</div>

<!-- 切换脚本 -->
<script>
// 默认显示英文
document.getElementById('en-content').style.display = 'block';
document.getElementById('zh-content').style.display = 'none';

function switchLang(lang) {
    if (lang === 'zh') {
        document.getElementById('zh-content').style.display = 'block';
        document.getElementById('en-content').style.display = 'none';
        document.getElementById('btn-zh').className = 'active';
        document.getElementById('btn-en').className = '';
    } else {
        document.getElementById('en-content').style.display = 'block';
        document.getElementById('zh-content').style.display = 'none';
        document.getElementById('btn-en').className = 'active';
        document.getElementById('btn-zh').className = '';
    }
}

// 默认选中英文
switchLang('en');
</script>
