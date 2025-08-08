# 🧪 Testing Setup Guide - Shared Folder Access

## **For Your Machine (Admin/IT):**

### **Step 1: Find Your IP Address**
```bash
# On Windows, open Command Prompt and run:
ipconfig

# Look for your IP address (usually starts with 192.168.x.x or 10.x.x.x)
# Example: 192.168.1.100
```

### **Step 2: Update index.html**
Replace `YOUR_MACHINE_IP` in `index.html` with your actual IP address:
```html
src="http://192.168.1.100:8501"  <!-- Replace with your actual IP -->
```

### **Step 3: Start Streamlit with Network Access**
```bash
# Run this command to allow network access:
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### **Step 4: Copy to Shared Folder**
- Copy the entire project folder to your shared network location
- Make sure staff have read access to the folder

---

## **For Staff Testing:**

### **Step 1: Access the File**
- Navigate to the shared folder
- Double-click `index.html`
- OR right-click → "Open with" → Choose your browser

### **Step 2: Test the Chatbot**
- The chatbot should appear at the bottom right
- Try asking: "How do I apply for a building permit?"
- Check if links work and open in new tabs

---

## **🔧 Troubleshooting:**

### **If Chatbot Doesn't Load:**
1. **Check your IP address** - Make sure it's correct in `index.html`
2. **Verify Streamlit is running** - Should show "Network URL: http://0.0.0.0:8501"
3. **Test locally first** - Try `http://localhost:8501` on your machine
4. **Check firewall** - Windows Firewall might block port 8501

### **If Staff Can't Access:**
1. **Network connectivity** - Staff must be on same network
2. **File permissions** - Ensure staff can read the shared folder
3. **Browser security** - Some browsers block local file access to network resources

### **Quick Test Commands:**
```bash
# Test if Streamlit is accessible from another machine:
curl http://YOUR_IP:8501

# Or open in browser on your machine:
http://YOUR_IP:8501
```

---

## **✅ Success Indicators:**
- ✅ Staff can open `index.html` in their browser
- ✅ Chatbot appears at bottom right corner
- ✅ Staff can type questions and get answers
- ✅ Links open in new tabs when clicked
- ✅ Follow-up questions work properly

---

## **📞 If Issues Occur:**
1. **Check the browser console** (F12) for error messages
2. **Verify network connectivity** between machines
3. **Test with a simple question** like "What is the planning department phone number?"
4. **Contact IT support** if network issues persist

*Remember: This is for testing only. For production, consider proper web hosting.* 