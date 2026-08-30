import json
import os
from datetime import datetime
import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Salman Kiryana Store - POS", page_icon="🛍️", layout="wide")

CONFIG_FILE = "config.json"
STOCK_FILE = "stock.json"
HISTORY_FILE = "sales_history.json"

# Default Data
default_config = {
    "store_name": "SALMAN KIRYANA STORE",
    "password": "salman123",
    "address": "Main Bazaar, Gujrat, Pakistan",
    "phone": "0300-0000000"
}

default_inventory = {
    "101": {"barcode": "101", "name": "Sugar 1kg", "price": 150, "stock": 20},
    "102": {"barcode": "102", "name": "Flour 10kg", "price": 1250, "stock": 4},
    "103": {"barcode": "103", "name": "Cooking Oil 1L", "price": 520, "stock": 5},
    "104": {"barcode": "104", "name": "Tea 400g", "price": 750, "stock": 25}
}

def load_json(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State
if "config" not in st.session_state:
    st.session_state.config = load_json(CONFIG_FILE, default_config)

if "inventory" not in st.session_state:
    st.session_state.inventory = load_json(STOCK_FILE, default_inventory)

if "history" not in st.session_state:
    st.session_state.history = load_json(HISTORY_FILE, [])

if "cart" not in st.session_state:
    st.session_state.cart = []

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Custom CSS & Thermal Print Styling
st.markdown("""
<style>
    .receipt-box {
        background-color: #ffffff;
        border: 2px dashed #333333;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace;
        color: #000000;
        max-width: 350px;
        margin: auto;
    }
    .receipt-header {
        text-align: center;
        border-bottom: 1px dashed #000;
        padding-bottom: 8px;
        margin-bottom: 10px;
    }
    .receipt-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .receipt-total {
        border-top: 1px dashed #000;
        margin-top: 10px;
        padding-top: 8px;
        text-align: right;
        font-weight: bold;
    }
    @media print {
        body * { visibility: hidden; }
        #printable-bill, #printable-bill * { visibility: visible; }
        #printable-bill { position: absolute; left: 0; top: 0; width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# Login Screen
if not st.session_state.authenticated:
    st.title(f"🔒 {st.session_state.config['store_name']} - Secure Login")
    pwd_input = st.text_input("🔑 Enter Access Password:", type="password")
    if st.button("🚀 Login"):
        if pwd_input == st.session_state.config["password"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid Password!")
    st.stop()

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; border-radius: 10px; margin-bottom: 15px;">
            <div style="font-size: 42px;">🧺🛒</div>
            <h3 style="margin: 5px 0 0 0; color: white;">SALMAN KIRYANA</h3>
            <small>✨ Smart POS System</small>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio(
        "📌 Menu Select:",
        [
            "🖥️ Main Desktop Dashboard", 
            "🖨️ Billing & Print Receipt", 
            "➕ Add New Product (Barcode Auto)", 
            "📜 Sales History Log", 
            "⚙️ Store Settings"
        ]
    )
    st.divider()
    if st.button("🔒 Logout System"):
        st.session_state.authenticated = False
        st.rerun()

# Header
st.title(f"🏬 {st.session_state.config['store_name']}")
st.caption("⚡ Live Point of Sale & Barcode System")
st.divider()

# 1. MAIN DESKTOP DASHBOARD
if menu == "🖥️ Main Desktop Dashboard":
    st.subheader("🖥️ Main Desktop Overview")
    
    total_products = len(st.session_state.inventory)
    total_investment = sum(item["price"] * item["stock"] for item in st.session_state.inventory.values())
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_sales = sum(
        sale["grand_total"] 
        for sale in st.session_state.history 
        if sale.get("date", "").startswith(today_str)
    )
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Today's Sales", f"Rs. {today_sales:,}")
    col2.metric("📦 Total Stock Value", f"Rs. {total_investment:,}")
    col3.metric("🏷️ Total Products", f"{total_products} Items")
    
    st.markdown("---")
    st.subheader("📦 Live Stock & Quick Direct Edit")
    
    for item_id, item_data in list(st.session_state.inventory.items()):
        bcode = item_data.get('barcode', item_id)
        with st.expander(f"🛍️ {item_data['name']} — (Barcode: {bcode} | Price: Rs.{item_data['price']} | Stock: {item_data['stock']})"):
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 2])
            u_bcode = c1.text_input("Barcode", value=bcode, key=f"code_{item_id}")
            u_name = c2.text_input("Item Name", value=item_data['name'], key=f"name_{item_id}")
            u_price = c3.number_input("Price (PKR)", value=int(item_data['price']), min_value=1, key=f"price_{item_id}")
            u_stock = c4.number_input("Stock Qty", value=int(item_data['stock']), min_value=0, key=f"stock_{item_id}")
            
            if c5.button("💾 Save", key=f"btn_{item_id}", type="primary"):
                st.session_state.inventory[item_id] = {
                    "barcode": u_bcode,
                    "name": u_name, 
                    "price": u_price, 
                    "stock": u_stock
                }
                save_json(STOCK_FILE, st.session_state.inventory)
                st.success("Item Updated Successfully!")
                st.rerun()

# 2. BILLING & PRINT RECEIPT
elif menu == "🖨️ Billing & Print Receipt":
    col_pos1, col_pos2 = st.columns([1.1, 1])
    
    with col_pos1:
        st.subheader("🛒 Customer Billing Counter")
        
        # BARCODE SCANNER INPUT WITH AUTO FOCUS
        scanned_barcode = st.text_input("🔍 Click Here & Scan Barcode (اسکینر سے بارکوڈ اسکین کریں):", key="barcode_input")
        
        selected_id = None
        
        if scanned_barcode:
            for k, v in st.session_state.inventory.items():
                if str(v.get("barcode", "")) == scanned_barcode.strip() or k == scanned_barcode.strip():
                    selected_id = k
                    break
            if not selected_id:
                st.warning("⚠️ No Item Found with this Barcode!")
        
        item_opts = {k: f"{v['name']} (Barcode: {v.get('barcode', k)} | Rs.{v['price']})" for k, v in st.session_state.inventory.items()}
        if not selected_id:
            selected_id = st.selectbox("Or Select Item from List:", options=list(item_opts.keys()), format_func=lambda x: item_opts[x])
        else:
            st.info(f"✅ Selected Item: **{st.session_state.inventory[selected_id]['name']}**")
            
        order_qty = st.number_input("🔢 Quantity:", min_value=1, value=1)
        
        if st.button("➕ Add To Cart", type="primary"):
            if selected_id:
                item_info = st.session_state.inventory[selected_id]
                if order_qty > item_info['stock']:
                    st.error("⚠️ Not enough stock available!")
                else:
                    st.session_state.inventory[selected_id]['stock'] -= order_qty
                    st.session_state.cart.append({
                        "id": selected_id,
                        "name": item_info['name'],
                        "price": item_info['price'],
                        "qty": order_qty,
                        "total": order_qty * item_info['price']
                    })
                    save_json(STOCK_FILE, st.session_state.inventory)
                    st.success(f"✅ Added {item_info['name']} to Cart!")
                    st.rerun()
                
        if st.button("🗑️ Clear Cart"):
            st.session_state.cart = []
            st.rerun()

    with col_pos2:
        st.subheader("🖨️ Printable Clean English Receipt")
        if st.session_state.cart:
            grand_total = sum(i['total'] for i in st.session_state.cart)
            now_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            
            # CLEAN ENGLISH RECEIPT (NO HTML CODES IN TEXT)
            st.markdown(f"""
            <div class="receipt-box" id="printable-bill">
                <div class="receipt-header">
                    <h2 style="margin:0;">{st.session_state.config['store_name']}</h2>
                    <small>{st.session_state.config['address']}</small><br>
                    <small>Phone: {st.session_state.config['phone']}</small><br>
                    <small>Date: {now_time}</small>
                </div>
                <div class="receipt-row" style="font-weight:bold; border-bottom:1px solid #000; padding-bottom:3px;">
                    <span style="width:40%;">ITEM</span>
                    <span style="width:20%; text-align:center;">QTY</span>
                    <span style="width:20%; text-align:right;">RATE</span>
                    <span style="width:20%; text-align:right;">TOTAL</span>
                </div>
            """, unsafe_allow_html=True)
            
            for item in st.session_state.cart:
                st.markdown(f"""
                <div class="receipt-row">
                    <span style="width:40%;">{item['name']}</span>
                    <span style="width:20%; text-align:center;">{item['qty']}</span>
                    <span style="width:20%; text-align:right;">{item['price']}</span>
                    <span style="width:20%; text-align:right;">{item['total']}</span>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
                <div class="receipt-total">
                    <h3 style="margin:0;">GRAND TOTAL: Rs. {grand_total}</h3>
                </div>
                <div style="text-align:center; margin-top:12px; font-size:11px;">
                    Thank You For Shopping With Us!
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.markdown("""
                <button onclick="window.print()" style="background-color: #2e7d32; color: white; padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">
                    🖨️ PRINT RECEIPT NOW
                </button>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button("✅ Complete Sale & Clear", type="primary"):
                new_sale = {
                    "receipt_id": len(st.session_state.history) + 1,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": st.session_state.cart,
                    "grand_total": grand_total
                }
                st.session_state.history.append(new_sale)
                save_json(HISTORY_FILE, st.session_state.history)
                st.session_state.cart = []
                st.success("🎉 Order Saved Successfully!")
                st.rerun()
        else:
            st.info("🛒 Cart is empty. Scan barcode or select items.")

# 3. ADD NEW PRODUCT WITH BARCODE
elif menu == "➕ Add New Product (Barcode Auto)":
    st.subheader("➕ Add New Item with Barcode Scanner")
    
    st.info("📌 **بارکوڈ کا طریقہ:** پہلے 'Barcode' کے خانے پر کلک کریں اور سامان کا بارکوڈ اسکین کریں، کوڈ خود ہی یہاں لکھا آ جائے گا۔")
    
    n_barcode = st.text_input("🔍 Click & Scan Barcode (بارکوڈ اسکین کریں):")
    n_name = st.text_input("🏷️ Item Name (سامان کا نام English میں):")
    n_price = st.number_input("💵 Price (PKR):", min_value=1, value=100)
    n_stock = st.number_input("📦 Stock Quantity:", min_value=0, value=10)
    
    if st.button("💾 Save Product To System", type="primary"):
        if n_name and n_barcode:
            new_id = str(n_barcode.strip())
            st.session_state.inventory[new_id] = {
                "barcode": new_id,
                "name": n_name, 
                "price": n_price, 
                "stock": n_stock
            }
            save_json(STOCK_FILE, st.session_state.inventory)
            st.success(f"✅ Product '{n_name}' saved with Barcode ({new_id})!")
            st.rerun()
        else:
            st.error("⚠️ Please enter Item Name and Barcode!")

# 4. SALES HISTORY
elif menu == "📜 Sales History Log":
    st.subheader("📜 Complete Sales History & Reports")
    if st.session_state.history:
        history_list = []
        for sale in reversed(st.session_state.history):
            history_list.append({
                "Receipt #": sale.get("receipt_id"),
                "Date & Time": sale.get("date"),
                "Total Amount (PKR)": sale.get("grand_total"),
                "Items Purchased": ", ".join([f"{i['name']} (x{i['qty']})" for i in sale.get("items", [])])
            })
        st.dataframe(pd.DataFrame(history_list), use_container_width=True)
    else:
        st.info("📜 No sales history available yet.")

# 5. STORE SETTINGS
elif menu == "⚙️ Store Settings":
    st.subheader("⚙️ Store Profile & Settings")
    
    new_store_name = st.text_input("🏪 Store Name:", value=st.session_state.config['store_name'])
    new_address = st.text_input("📍 Address:", value=st.session_state.config['address'])
    new_phone = st.text_input("📞 Phone:", value=st.session_state.config['phone'])
    new_pass = st.text_input("🔑 Login Password:", value=st.session_state.config['password'], type="password")
    
    if st.button("💾 Save Settings", type="primary"):
        st.session_state.config["store_name"] = new_store_name
        st.session_state.config["address"] = new_address
        st.session_state.config["phone"] = new_phone
        st.session_state.config["password"] = new_pass
        save_json(CONFIG_FILE, st.session_state.config)
        st.success("✅ Settings Updated Successfully!")
        st.rerun()