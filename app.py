#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汽车保养助手 - Python 单文件版
一个文件包含：Flask后端 + SQLite数据库 + 前端页面
"""

from flask import Flask, render_template_string, request, jsonify
import sqlite3
from datetime import datetime
from contextlib import contextmanager
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'car_maintenance.db')

# ==================== 数据库部分 ====================

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    with get_db() as conn:
        c = conn.cursor()
        
        # 车辆表
        c.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT,
                plate TEXT,
                purchase_date TEXT,
                current_km INTEGER DEFAULT 0,
                total_maintenance INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 保养项目表
        c.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                icon TEXT DEFAULT '🔧',
                cycle_km INTEGER DEFAULT 0,
                cycle_days INTEGER DEFAULT 0,
                deleted INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 如果 deleted 列不存在，添加它
        try:
            c.execute('ALTER TABLE items ADD COLUMN deleted INTEGER DEFAULT 0')
        except:
            pass
        
        # 保养记录表
        c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                maintenance_date TEXT,
                maintenance_km INTEGER,
                cost REAL DEFAULT 0,
                note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        ''')
        
        # 插入默认保养项目（名称, 图标, 周期km, 周期天）
        # 只插入数据库中不存在的项目（不检查deleted，因为用户可能删除了）
        default_items = [
            ('机油保养', '🛢️', 7500, 365),
            ('机油滤芯', '🔧', 7500, 365),
            ('空气滤芯', '🌬️', 20000, 730),
            ('空调滤芯', '❄️', 20000, 730),
            ('刹车片', '🛑', 40000, 0),
            ('变速箱油', '⚙️', 80000, 0),
            ('火花塞', '⚡', 60000, 0),
            ('防冻液', '💧', 40000, 1095),
            ('刹车油', '🧴', 40000, 730),
            ('轮胎', '🛞', 80000, 0),
        ]
        
        for name, icon, km, days in default_items:
            c.execute('SELECT id FROM items WHERE name = ?', (name,))
            if not c.fetchone():
                c.execute('INSERT INTO items (name, icon, cycle_km, cycle_days, deleted) VALUES (?, ?, ?, ?, 0)', 
                         (name, icon, km, days))
        
        conn.commit()

# ==================== 前端页面 ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>汽车保养助手</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f6fa;
            min-height: 100vh;
            padding-bottom: 100px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header-content {
            max-width: 800px;
            margin: 0 auto;
        }
        .header h1 { font-size: 24px; margin-bottom: 8px; }
        .vehicle-info { font-size: 14px; opacity: 0.9; }
        .vehicle-info .plate { font-size: 18px; font-weight: 700; }
        
        .container {
            max-width: 800px;
            margin: 20px auto;
            padding: 0 15px;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }
        
        .card-title {
            font-size: 18px;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .vehicle-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .detail-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 10px;
        }
        
        .detail-label {
            font-size: 12px;
            color: #999;
            margin-bottom: 4px;
        }
        
        .detail-value {
            font-size: 16px;
            color: #333;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .km-value {
            justify-content: space-between;
        }
        
        .edit-km-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .edit-km-btn:hover {
            background: #e5e7eb;
        }
        
        .vehicle-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        
        .vehicle-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .edit-vehicle-btn {
            background: none;
            border: 1px solid #ddd;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: #666;
            transition: all 0.2s;
        }
        
        .edit-vehicle-btn:hover {
            background: #f5f5f5;
            border-color: #ccc;
        }
        
        /* 柱状图 */
        .progress-bar-container {
            margin-bottom: 16px;
        }
        
        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .progress-name {
            font-size: 15px;
            color: #333;
            font-weight: 500;
        }
        
        .progress-stats {
            font-size: 13px;
            color: #666;
        }
        
        .progress-stats .remaining {
            font-weight: 600;
        }
        
        .progress-stats .remaining.warning { color: #f59e0b; }
        .progress-stats .remaining.danger { color: #ef4444; }
        
        .progress-bar {
            height: 24px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            border-radius: 12px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            font-size: 12px;
            color: white;
            font-weight: 600;
            min-width: 40px;
        }
        
        .progress-fill.blue {
            background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
        }
        .progress-fill.yellow {
            background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
        }
        .progress-fill.red {
            background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        /* 按钮 */
        .bottom-actions {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 12px;
            z-index: 100;
        }
        
        .btn {
            padding: 12px 20px;
            border-radius: 25px;
            border: none;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        /* 模态框 */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal.active { display: flex; }
        
        .modal-content {
            background: white;
            border-radius: 16px;
            padding: 24px;
            width: 90%;
            max-width: 400px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h3 {
            font-size: 18px;
            color: #333;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #999;
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        .form-group label {
            display: block;
            font-size: 14px;
            color: #666;
            margin-bottom: 6px;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .btn-submit {
            width: calc(50% - 6px);
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        
        .form-actions {
            display: flex;
            gap: 12px;
        }
        
        .btn-delete {
            width: calc(50% - 6px);
            padding: 12px;
            background: #ef4444;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        
        /* 图标选择器 */
        .icon-selector {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .icon-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .icon-option {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            background: #f0f0f0;
            border-radius: 8px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .icon-option:hover {
            background: #e0e0e0;
        }
        
        .icon-option.selected {
            border-color: #667eea;
            background: #f0f4ff;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }
        
        /* 历史记录 */
        .record-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .record-info { flex: 1; }
        .record-name { font-weight: 600; color: #333; }
        .record-detail { font-size: 13px; color: #666; }
        
        .record-delete {
            background: #ef4444;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }
        
        /* 提示信息 */
        .toast {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            z-index: 2000;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .toast.show { opacity: 1; }
        
        /* 车辆选择器 */
        .vehicle-selector {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        .vehicle-selector select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .tab {
            flex: 1;
            padding: 10px;
            text-align: center;
            background: #f0f0f0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .tab.active {
            background: #667eea;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>🚗 汽车保养助手</h1>
            <div class="vehicle-info">
                <div class="plate" id="currentPlate">请添加车辆</div>
                <div id="currentVehicle">-</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <!-- 车辆信息 -->
        <div class="card" id="vehicleCard">
            <h2 class="card-title">📋 车辆信息</h2>
            <div id="vehicleDetails">
                <div class="empty-state">
                    <div class="icon">🚗</div>
                    <p>暂无车辆，请添加</p>
                </div>
            </div>
        </div>
        
        <!-- 保养提醒 -->
        <div class="card" id="maintenanceCard">
            <h2 class="card-title">🔧 保养提醒</h2>
            <div id="maintenanceList"></div>
        </div>
        
        <!-- 保养历史 -->
        <div class="card" id="historyCard">
            <h2 class="card-title">📜 保养历史</h2>
            <div class="tabs">
                <div class="tab active" onclick="switchTab('records')">保养记录</div>
                <div class="tab" onclick="switchTab('items')">保养项目</div>
            </div>
            <div id="recordsList" class="tab-content active"></div>
            <div id="itemsList" class="tab-content"></div>
        </div>
    </div>
    
    <div class="bottom-actions">
        <button class="btn btn-secondary" onclick="openModal('vehicleModal')">➕ 车辆</button>
        <button class="btn btn-secondary" onclick="openModal('itemModal')">🔧 项目</button>
        <button class="btn btn-primary" onclick="openModal('maintenanceModal')">📝 保养</button>
    </div>
    
    <!-- 车辆模态框 -->
    <div class="modal" id="vehicleModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>添加车辆</h3>
                <button class="modal-close" onclick="closeModal('vehicleModal')">×</button>
            </div>
            <form id="vehicleForm">
                <div class="form-group">
                    <label>品牌</label>
                    <input type="text" name="brand" placeholder="如：宝马" required>
                </div>
                <div class="form-group">
                    <label>车型</label>
                    <input type="text" name="model" placeholder="如：325Li">
                </div>
                <div class="form-group">
                    <label>车牌号</label>
                    <input type="text" name="plate" placeholder="如：苏C88888">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>当前里程(km)</label>
                        <input type="number" name="current_km" placeholder="60000">
                    </div>
                    <div class="form-group">
                        <label>购买日期</label>
                        <input type="date" name="purchase_date">
                    </div>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn-delete" onclick="deleteItem()">🗑️ 删除</button>
                    <button type="submit" class="btn-submit">保存</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- 项目模态框 -->
    <div class="modal" id="itemModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="itemModalTitle">添加保养项目</h3>
                <button class="modal-close" onclick="closeModal('itemModal')">×</button>
            </div>
            <form id="itemForm">
                <input type="hidden" name="id">
                <div class="form-group">
                    <label>项目名称</label>
                    <input type="text" name="name" placeholder="如：机油保养" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>周期(km)</label>
                        <input type="number" name="cycle_km" placeholder="7500">
                    </div>
                    <div class="form-group">
                        <label>周期(天)</label>
                        <input type="number" name="cycle_days" placeholder="365">
                    </div>
                </div>
                <div class="form-group">
                    <label>图标</label>
                    <div class="icon-selector">
                        <input type="hidden" name="icon" id="selectedIcon" value="🔧">
                        <div class="icon-grid" id="iconGrid">
                            <!-- 图标由JavaScript动态生成 -->
                        </div>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn-delete" onclick="deleteItem()">🗑️ 删除</button>
                    <button type="submit" class="btn-submit">保存</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- 保养记录模态框 -->
    <div class="modal" id="maintenanceModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>添加保养记录</h3>
                <button class="modal-close" onclick="closeModal('maintenanceModal')">×</button>
            </div>
            <form id="maintenanceForm">
                <div class="form-group">
                    <label>选择车辆</label>
                    <select name="vehicle_id" id="maintenanceVehicleSelect" required></select>
                </div>
                <div class="form-group">
                    <label>保养项目</label>
                    <select name="item_id" id="maintenanceItemSelect" required></select>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>保养日期</label>
                        <input type="date" name="maintenance_date" required>
                    </div>
                    <div class="form-group">
                        <label>保养时里程</label>
                        <input type="number" name="maintenance_km" placeholder="60000" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>备注</label>
                    <input type="text" name="note" placeholder="可选">
                </div>
                <div class="form-actions">
                    <button type="button" class="btn-delete" onclick="deleteItem()">🗑️ 删除</button>
                    <button type="submit" class="btn-submit">保存</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- 更新里程弹窗 -->
    <div class="modal" id="editKmModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>更新当前里程</h3>
                <button class="modal-close" onclick="closeModal('editKmModal')">×</button>
            </div>
            <form id="editKmForm">
                <input type="hidden" id="editKmVehicleId">
                <div class="form-group">
                    <label>当前里程 (km)</label>
                    <input type="number" id="editKmInput" placeholder="请输入当前里程" required>
                </div>
                <button type="button" onclick="updateKm()" class="btn-submit">保存</button>
            </form>
        </div>
    </div>
    
    <!-- 编辑车辆弹窗 -->
    <div class="modal" id="editVehicleModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>编辑车辆信息</h3>
                <button class="modal-close" onclick="closeModal('editVehicleModal')">×</button>
            </div>
            <form id="editVehicleForm">
                <input type="hidden" id="editVehicleId">
                <div class="form-group">
                    <label>品牌</label>
                    <input type="text" id="editVehicleBrand" required>
                </div>
                <div class="form-group">
                    <label>车型</label>
                    <input type="text" id="editVehicleModel">
                </div>
                <div class="form-group">
                    <label>车牌号</label>
                    <input type="text" id="editVehiclePlate">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>当前里程 (km)</label>
                        <input type="number" id="editVehicleKm">
                    </div>
                    <div class="form-group">
                        <label>购买日期</label>
                        <input type="date" id="editVehiclePurchaseDate">
                    </div>
                </div>
                <button type="button" onclick="saveEditVehicle()" class="btn-submit">保存</button>
            </form>
        </div>
    </div>
    
    <!-- 提示 -->
    <div class="toast" id="toast"></div>
    
    <script>
        let currentVehicleId = null;
        
        // 初始化
        document.addEventListener('DOMContentLoaded', () => {
            loadData();
            
            // 表单提交
            document.getElementById('vehicleForm').addEventListener('submit', saveVehicle);
            document.getElementById('itemForm').addEventListener('submit', saveItem);
            document.getElementById('maintenanceForm').addEventListener('submit', saveMaintenance);
        });
        
        // 加载数据
        async function loadData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            
            if (data.vehicles && data.vehicles.length > 0) {
                currentVehicleId = data.vehicles[0].id;
                renderVehicle(data.vehicles[0]);
                renderMaintenance(data.vehicles[0]);
                renderRecords(data.records);
                renderItems(data.items);
                updateVehicleSelect(data.vehicles);
                updateItemSelect(data.items);
            } else {
                document.getElementById('vehicleDetails').innerHTML = `
                    <div class="empty-state">
                        <div class="icon">🚗</div>
                        <p>暂无车辆，请添加</p>
                    </div>
                `;
                document.getElementById('maintenanceList').innerHTML = '<div class="empty-state"><p>请先添加车辆</p></div>';
                document.getElementById('recordsList').innerHTML = '<div class="empty-state"><p>暂无记录</p></div>';
            }
        }
        
        // 渲染车辆
        function renderVehicle(v) {
            document.getElementById('currentPlate').textContent = v.plate || '未设置车牌';
            document.getElementById('currentVehicle').textContent = `${v.brand} ${v.model || ''}`.trim();
            document.getElementById('vehicleDetails').innerHTML = `
                <div class="vehicle-header">
                    <div class="vehicle-title">${v.brand} ${v.model || ''}</div>
                    <button class="edit-vehicle-btn" onclick="openEditVehicleModal(${v.id})" title="编辑车辆">✏️ 编辑</button>
                </div>
                <div class="vehicle-details">
                    <div class="detail-item">
                        <div class="detail-label">当前里程</div>
                        <div class="detail-value km-value">
                            ${v.current_km.toLocaleString()} km
                            <button class="edit-km-btn" onclick="openEditKmModal(${v.id}, ${v.current_km})" title="更新里程">✏️</button>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">累计保养</div>
                        <div class="detail-value">${v.total_maintenance} 次</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">购买日期</div>
                        <div class="detail-value">${v.purchase_date || '-'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">车牌号</div>
                        <div class="detail-value">${v.plate || '-'}</div>
                    </div>
                </div>
            `;
            // 保存车辆ID供更新使用
            window.currentVehicle = v;
        }
        
        // 打开编辑车辆弹窗
        function openEditVehicleModal(vehicleId) {
            const v = window.currentVehicle;
            document.getElementById('editVehicleId').value = vehicleId;
            document.getElementById('editVehicleBrand').value = v.brand;
            document.getElementById('editVehicleModel').value = v.model || '';
            document.getElementById('editVehiclePlate').value = v.plate || '';
            document.getElementById('editVehiclePurchaseDate').value = v.purchase_date || '';
            document.getElementById('editVehicleKm').value = v.current_km;
            document.getElementById('editVehicleModal').classList.add('active');
        }
        
        // 保存车辆编辑
        async function saveEditVehicle() {
            const vehicleId = document.getElementById('editVehicleId').value;
            const data = {
                brand: document.getElementById('editVehicleBrand').value,
                model: document.getElementById('editVehicleModel').value,
                plate: document.getElementById('editVehiclePlate').value,
                purchase_date: document.getElementById('editVehiclePurchaseDate').value,
                current_km: parseInt(document.getElementById('editVehicleKm').value) || 0
            };
            
            await fetch('/api/vehicle/' + vehicleId, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            document.getElementById('editVehicleModal').classList.remove('active');
            showToast('车辆已更新');
            loadData();
        }
        
        // 打开更新里程弹窗
        function openEditKmModal(vehicleId, currentKm) {
            document.getElementById('editKmVehicleId').value = vehicleId;
            document.getElementById('editKmInput').value = currentKm;
            document.getElementById('editKmModal').classList.add('active');
        }
        
        // 更新里程
        async function updateKm() {
            const vehicleId = document.getElementById('editKmVehicleId').value;
            const newKm = parseInt(document.getElementById('editKmInput').value) || 0;
            
            await fetch('/api/vehicle/' + vehicleId, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({current_km: newKm})
            });
            
            document.getElementById('editKmModal').classList.remove('active');
            showToast('里程已更新');
            loadData();
        }
        
        // 渲染保养提醒
        function renderMaintenance(vehicle) {
            fetch(`/api/maintenance/${vehicle.id}`)
                .then(r => r.json())
                .then(data => {
                    if (data.length === 0) {
                        document.getElementById('maintenanceList').innerHTML = '<div class="empty-state"><p>暂无保养项目</p></div>';
                        return;
                    }
                    
                    // 按剩余里程排序
                    data.sort((a, b) => a.remaining_km - b.remaining_km);
                    
                    document.getElementById('maintenanceList').innerHTML = data.map(item => {
                        let colorClass = 'blue';
                        let statusClass = '';
                        
                        if (item.remaining_km < 500) {
                            colorClass = 'red';
                            statusClass = 'danger';
                        } else if (item.remaining_km < 2000) {
                            colorClass = 'yellow';
                            statusClass = 'warning';
                        }
                        
                        const percent = Math.min(100, Math.max(5, (item.remaining_km / item.cycle_km) * 100));
                        
                        return `
                            <div class="progress-bar-container">
                                <div class="progress-header">
                                    <span class="progress-name">${item.icon} ${item.name}</span>
                                    <span class="progress-stats">
                                        剩余 <span class="remaining ${statusClass}">${item.remaining_km.toLocaleString()} km</span>
                                    </span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill ${colorClass}" style="width: ${percent}%">
                                        ${percent.toFixed(0)}%
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');
                });
        }
        
        // 渲染保养记录
        function renderRecords(records) {
            if (!records || records.length === 0) {
                document.getElementById('recordsList').innerHTML = '<div class="empty-state"><p>暂无记录</p></div>';
                return;
            }
            
            document.getElementById('recordsList').innerHTML = records.map(r => `
                <div class="record-item">
                    <div class="record-info">
                        <div class="record-name">${r.item_name}</div>
                        <div class="record-detail">${r.maintenance_date} · ${r.maintenance_km.toLocaleString()} km</div>
                    </div>
                    <button class="record-delete" onclick="deleteRecord(${r.id})">删除</button>
                </div>
            `).join('');
        }
        
        // 渲染保养项目
        function renderItems(items) {
            document.getElementById('itemsList').innerHTML = items.map(item => `
                <div class="record-item">
                    <div class="record-info">
                        <div class="record-name">${item.icon} ${item.name}</div>
                        <div class="record-detail">每 ${item.cycle_km.toLocaleString()} km ${item.cycle_days > 0 ? '或 ' + item.cycle_days + ' 天' : ''}</div>
                    </div>
                    <button class="record-delete" onclick="editItem(${item.id})">编辑</button>
                </div>
            `).join('');
        }
        
        // 更新车辆选择器
        function updateVehicleSelect(vehicles) {
            const select = document.getElementById('maintenanceVehicleSelect');
            select.innerHTML = vehicles.map(v => 
                `<option value="${v.id}">${v.brand} ${v.model} (${v.plate})</option>`
            ).join('');
            if (currentVehicleId) {
                select.value = currentVehicleId;
            }
        }
        
        // 更新项目选择器
        function updateItemSelect(items) {
            const select = document.getElementById('maintenanceItemSelect');
            select.innerHTML = items.map(item => 
                `<option value="${item.id}">${item.name}</option>`
            ).join('');
        }
        
        // 保存车辆
        async function saveVehicle(e) {
            e.preventDefault();
            const form = e.target;
            const data = Object.fromEntries(new FormData(form));
            data.current_km = parseInt(data.current_km) || 0;
            
            await fetch('/api/vehicle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            closeModal('vehicleModal');
            form.reset();
            showToast('保存成功');
            loadData();
        }
        
        // 保存保养项目
        async function saveItem(e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const data = {
                id: formData.get('id') || null,
                name: formData.get('name'),
                icon: document.getElementById('selectedIcon').value,
                cycle_km: parseInt(formData.get('cycle_km')) || 0,
                cycle_days: parseInt(formData.get('cycle_days')) || 0
            };
            
            await fetch('/api/item', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            closeModal('itemModal');
            form.reset();
            showToast('保存成功');
            loadData();
        }
        
        // 保存保养记录
        async function saveMaintenance(e) {
            e.preventDefault();
            const form = e.target;
            const data = Object.fromEntries(new FormData(form));
            data.maintenance_km = parseInt(data.maintenance_km) || 0;
            
            await fetch('/api/maintenance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            closeModal('maintenanceModal');
            form.reset();
            showToast('保存成功');
            loadData();
        }
        
        // 删除记录
        async function deleteRecord(id) {
            if (!confirm('确定删除这条记录？')) return;
            
            await fetch(`/api/record/${id}`, {method: 'DELETE'});
            showToast('已删除');
            loadData();
        }
        
        // 编辑项目
        async function editItem(id) {
            const res = await fetch('/api/item/' + id);
            const item = await res.json();
            
            const form = document.getElementById('itemForm');
            form.elements.id.value = item.id;
            form.elements.name.value = item.name;
            form.elements.cycle_km.value = item.cycle_km;
            form.elements.cycle_days.value = item.cycle_days;
            
            // 设置图标
            document.getElementById('selectedIcon').value = item.icon || '🔧';
            updateIconSelection(item.icon || '🔧');
            
            document.getElementById('itemModalTitle').textContent = '编辑保养项目';
            document.getElementById('itemForm').dataset.itemId = id;
            openModal('itemModal');
        }
        
        // 更新图标选中状态
        function updateIconSelection(selected) {
            document.querySelectorAll('.icon-option').forEach(opt => {
                if (opt.dataset.icon === selected) {
                    opt.classList.add('selected');
                } else {
                    opt.classList.remove('selected');
                }
            });
        }
        
        // 初始化图标选择器
        document.addEventListener('DOMContentLoaded', () => {
            // 汽车保养相关的图标
            const icons = ['🔧', '🛠️', '⚙️', '🛢️', '🛞', '🛑', '⚡', '💧', '❄️', '🌬️', '🔩', '🧴', '🔋', '🚗', '⛽', '🔥', '💨', '🧽', '🧤', '📋'];
            const iconGrid = document.querySelector('.icon-grid');
            if (iconGrid) {
                iconGrid.innerHTML = icons.map(icon => 
                    `<div class="icon-option${icon === '🔧' ? ' selected' : ''}" data-icon="${icon}" onclick="selectIcon(this)">${icon}</div>`
                ).join('');
            }
            
            // 绑定图标选择
            document.querySelector('.icon-grid')?.addEventListener('click', (e) => {
                const opt = e.target.closest('.icon-option');
                if (opt) {
                    selectIcon(opt);
                }
            });
        });
        
        // 选择图标
        function selectIcon(el) {
            document.querySelectorAll('.icon-option').forEach(o => o.classList.remove('selected'));
            el.classList.add('selected');
            document.getElementById('selectedIcon').value = el.dataset.icon;
        }
        
        // 删除项目
        async function deleteItem() {
            const id = document.getElementById('itemForm').dataset.itemId;
            if (!id) return;
            
            if (!confirm('确定删除该项目？删除后相关保养记录也会被删除。')) return;
            
            await fetch('/api/item/' + id, {method: 'DELETE'});
            closeModal('itemModal');
            showToast('已删除');
            loadData();
        }
        
        // Tab切换
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + 'List').classList.add('active');
        }
        
        // 模态框
        function openModal(id) {
            document.getElementById(id).classList.add('active');
        }
        
        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
            // 重置表单
            const form = document.getElementById(id).querySelector('form');
            if (form) form.reset();
          document.getElementById('itemModalTitle').textContent = '添加保养项目';
        }
        
        // 提示
        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }
    </script>
</body>
</html>
'''

# ==================== API 路由 ====================

@app.route('/')
def index():
    """首页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    """获取所有数据"""
    with get_db() as conn:
        c = conn.cursor()
        
        # 车辆
        vehicles = c.execute('SELECT * FROM vehicles ORDER BY id DESC').fetchall()
        vehicles = [dict(v) for v in vehicles]
        
        # 项目（只查询未删除的）
        items = c.execute('SELECT * FROM items WHERE deleted=0 ORDER BY name').fetchall()
        items = [dict(v) for v in items]
        
        # 保养记录
        records = c.execute('''
            SELECT r.*, i.name as item_name 
            FROM records r 
            JOIN items i ON r.item_id = i.id 
            ORDER BY r.maintenance_date DESC
        ''').fetchall()
        records = [dict(r) for r in records]
        
        return jsonify({
            'vehicles': vehicles,
            'items': items,
            'records': records
        })

@app.route('/api/vehicle', methods=['POST'])
def add_vehicle():
    """添加车辆"""
    data = request.json
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO vehicles (brand, model, plate, purchase_date, current_km)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['brand'], data.get('model'), data.get('plate'), 
              data.get('purchase_date'), data.get('current_km', 0)))
        conn.commit()
        return jsonify({'id': c.lastrowid})

@app.route('/api/vehicle/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    """更新车辆"""
    data = request.json
    with get_db() as conn:
        c = conn.cursor()
        
        # 获取当前车辆信息
        vehicle = c.execute('SELECT * FROM vehicles WHERE id=?', (vehicle_id,)).fetchone()
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # 更新字段
        updates = []
        values = []
        
        if 'brand' in data:
            updates.append('brand=?')
            values.append(data['brand'])
        if 'model' in data:
            updates.append('model=?')
            values.append(data['model'])
        if 'plate' in data:
            updates.append('plate=?')
            values.append(data['plate'])
        if 'purchase_date' in data:
            updates.append('purchase_date=?')
            values.append(data['purchase_date'])
        if 'current_km' in data:
            updates.append('current_km=?')
            values.append(data['current_km'])
        
        if updates:
            values.append(vehicle_id)
            c.execute(f'UPDATE vehicles SET {", ".join(updates)} WHERE id=?', values)
            conn.commit()
        
        return jsonify({'success': True})

@app.route('/api/item', methods=['POST'])
def save_item():
    """保存保养项目"""
    data = request.json
    with get_db() as conn:
        c = conn.cursor()
        if data.get('id'):
            c.execute('UPDATE items SET name=?, icon=?, cycle_km=?, cycle_days=? WHERE id=?',
                     (data['name'], data.get('icon', '🔧'), data.get('cycle_km', 0), data.get('cycle_days', 0), data['id']))
        else:
            c.execute('INSERT INTO items (name, icon, cycle_km, cycle_days) VALUES (?, ?, ?, ?)',
                     (data['name'], data.get('icon', '🔧'), data.get('cycle_km', 0), data.get('cycle_days', 0)))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/item/<int:item_id>')
def get_item(item_id):
    """获取单个项目"""
    with get_db() as conn:
        c = conn.cursor()
        item = c.execute('SELECT * FROM items WHERE id=?', (item_id,)).fetchone()
        return jsonify(dict(item))

@app.route('/api/item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """删除保养项目（软删除）"""
    with get_db() as conn:
        c = conn.cursor()
        # 软删除：标记为deleted=1
        c.execute('UPDATE items SET deleted=1 WHERE id=?', (item_id,))
        # 删除相关记录
        c.execute('DELETE FROM records WHERE item_id=?', (item_id,))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/maintenance/<int:vehicle_id>')
def get_maintenance(vehicle_id):
    """获取车辆保养状态"""
    with get_db() as conn:
        c = conn.cursor()
        
        # 获取车辆信息
        vehicle = c.execute('SELECT * FROM vehicles WHERE id=?', (vehicle_id,)).fetchone()
        if not vehicle:
            return jsonify([])
        
        # 获取所有未删除的保养项目
        items = c.execute('SELECT * FROM items WHERE cycle_km > 0 AND deleted=0').fetchall()
        
        result = []
        for item in items:
            # 获取该项目最后一条保养记录
            record = c.execute('''
                SELECT * FROM records 
                WHERE vehicle_id=? AND item_id=? 
                ORDER BY maintenance_km DESC 
                LIMIT 1
            ''', (vehicle_id, item['id'])).fetchone()
            
            if record:
                last_km = record['maintenance_km']
                last_date = record['maintenance_date']
            else:
                last_km = 0
                last_date = vehicle['purchase_date'] or datetime.now().strftime('%Y-%m-%d')
            
            remaining_km = item['cycle_km'] - (vehicle['current_km'] - last_km)
            remaining_km = max(0, remaining_km)
            
            # 图标
            icons = {'机油': '🛢️', '空气': '🌬️', '空调': '❄️', '刹车': '🛑', '变速箱': '⚙️', 
                    '火花塞': '⚡', '防冻': '💧', '轮胎': '🛞', '滤芯': '🔧'}
            icon = '🔧'
            for k, v in icons.items():
                if k in item['name']:
                    icon = v
                    break
            
            result.append({
                'id': item['id'],
                'name': item['name'],
                'icon': icon,
                'cycle_km': item['cycle_km'],
                'cycle_days': item['cycle_days'],
                'last_km': last_km,
                'last_date': last_date,
                'remaining_km': remaining_km,
                'used_km': vehicle['current_km'] - last_km
            })
        
        return jsonify(result)

@app.route('/api/maintenance', methods=['POST'])
def add_maintenance():
    """添加保养记录"""
    data = request.json
    with get_db() as conn:
        c = conn.cursor()
        
        # 添加记录
        c.execute('''
            INSERT INTO records (vehicle_id, item_id, maintenance_date, maintenance_km, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['vehicle_id'], data['item_id'], data['maintenance_date'], 
              data['maintenance_km'], data.get('note')))
        
        # 注意：不再自动更新车辆里程，避免历史记录覆盖当前里程
        # 车辆里程由用户在车辆信息中手动维护
        
        # 增加保养次数
        c.execute('UPDATE vehicles SET total_maintenance = total_maintenance + 1 WHERE id=?',
                 (data['vehicle_id'],))
        
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除保养记录"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM records WHERE id=?', (record_id,))
        conn.commit()
        return jsonify({'success': True})

# ==================== 启动 ====================

if __name__ == '__main__':
    init_db()
    print('=' * 50)
    print('🚗 汽车保养助手')
    print('=' * 50)
    print('打开浏览器访问: http://localhost:5000')
    print('按 Ctrl+C 停止服务')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)