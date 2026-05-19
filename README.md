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
git clone https://github.com/你的用户名/car-maintenance-assistant.git
cd car-maintenance-assistant
```

**2. 安装依赖**
```bash
pip install flask
```

**3. 启动服务**
```bash
python app.py
```

**4. 访问**
打开浏览器访问：`http://localhost:5000`

---

## 📁 项目结构

```
car-maintenance-assistant/
├── app.py          # 主程序（包含后端 + 前端 + 数据库）
├── index.html      # 前端页面（备用）
├── requirements.txt # Python依赖
└── README.md       # 说明文档
```

---

## 🔧 部署方式

### 方式一：本地运行（适合尝鲜）

```bash
python app.py
```

### 方式二：后台运行 + 自动重启

```bash
# 使用 nohup 后台运行
nohup python app.py > app.log 2>&1 &

# 查看进程
ps aux | grep app.py

# 重启
pkill -f app.py && nohup python app.py > app.log 2>&1 &
```

### 方式三：使用 systemd 服务（Linux）

创建服务文件 `/etc/systemd/system/car-maintenance.service`：

```ini
[Unit]
Description=Car Maintenance Assistant
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/path/to/car-maintenance-assistant
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

然后：
```bash
sudo systemctl daemon-reload
sudo systemctl enable car-maintenance
sudo systemctl start car-maintenance
```

### 方式四：Nginx 反向代理（远程访问）

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

## 🚀 使用说明

### 添加车辆
1. 点击「添加车辆」按钮
2. 填写品牌、型号、车牌等信息
3. 填写购车日期和当前里程

### 记录保养
1. 选择车辆
2. 点击「记录保养」
3. 选择保养项目，填写日期和里程
4. 可选记录费用和备注

### 查看保养状态
- 🔴 **红色** - 已超过保养周期，需要保养
- 🟡 **黄色** - 即将到达保养周期（剩余 < 500km 或 < 30天）
- 🟢 **绿色** - 正常，在保养周期内

---

## ⚙️ 自定义配置

编辑 `app.py` 开头的配置：

```python
app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'car_maintenance.db')

# 修改默认端口
# app.run(host='0.0.0.0', port=5000)
```

---

## ❓ 常见问题

**Q: 启动报错 `Module not found: flask`**
```bash
pip install flask
```

**Q: 数据存在哪里？**
数据库文件在同目录下的 `car_maintenance.db`

**Q: 如何备份数据？**
```bash
# 复制数据库文件即可
cp car_maintenance.db car_maintenance.db.backup
```

**Q: 如何重置数据？**
```bash
rm car_maintenance.db
python app.py  # 会自动创建新的空数据库
```

---

## 📝 License

MIT License - 随便用，随便改 😄

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**有问题？联系作者或提交 Issue**