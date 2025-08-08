# CABQ Planning Chatbot - Deployment Options

## 🚀 **Recommended: Option 1 - Simple Web Access**

### **📋 For Staff - Super Easy Usage:**

#### **Step 1: Staff Opens the Page**
- **Double-click** `index.html` file
- **OR** open in browser: `file:///path/to/index.html`
- **Chatbot appears** automatically at bottom right corner

#### **Step 2: Start Using**
- **Type questions** in the input field
- **Press Enter** or click submit
- **Read answers** and click any provided links
- **Ask follow-up questions** as needed

### **🔧 For Admin/IT Setup:**

#### **Local Network Deployment:**
```bash
# 1. Start the Streamlit backend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# 2. Share the index.html file with staff
# 3. Staff opens index.html in their browsers
```

#### **File Server Deployment:**
```bash
# 1. Upload index.html to any web server
# 2. Update the iframe src in index.html to point to your server
# 3. Staff access via: https://your-domain.com/index.html
```

### **📁 File Structure for Staff:**
```
📁 CABQ Planning Chatbot/
├── 📄 index.html          ← Staff opens this
├── 📄 app.py              ← Admin runs this
├── 📄 requirements.txt    ← Admin manages
├── 📄 deployment_options.md ← This file
└── 🔒 .env               ← Admin manages
```

### **✅ Staff Benefits:**
- ✅ **No installation needed**
- ✅ **No technical knowledge required**
- ✅ **Works on any device with a browser**
- ✅ **Professional interface**
- ✅ **Always available**

### **🔧 Admin Management:**
- **Keep Streamlit running** on a server
- **Update `.env` file** as needed
- **Monitor usage** and performance
- **Backup conversation history** if needed

### **📞 Staff Training (5 minutes):**
1. **Open** `index.html`
2. **Type** your question
3. **Press Enter**
4. **Read** the answer
5. **Click** any links provided
6. **Ask** follow-up questions

---

## 🌐 **Option 2: Direct Streamlit Access**

### **For Technical Staff:**
1. **Open terminal/command prompt**
2. **Navigate to project folder**
3. **Run**: `streamlit run app.py`
4. **Open browser** to `http://localhost:8501`

### **Production Deployment:**
```bash
# Using Streamlit Cloud or similar
streamlit run app.py --server.port 8501
```

---

## 🏢 **Enterprise Deployment Options**

### **Internal Network Setup:**
```bash
# On the server/computer that will host the chatbot
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### **Web Server Deployment:**
- Upload `index.html` to any web server
- Staff access via URL: `https://your-domain.com/index.html`
- Chatbot embedded automatically

### **Streamlit Cloud Deployment:**
- Deploy `app.py` to Streamlit Cloud
- Staff access via: `https://your-app-name.streamlit.app`
- Professional hosting with updates

---

## 📋 **Staff Usage Guide**

### **Common Questions Staff Can Ask:**
- "How do I apply for a building permit?"
- "What's the contact information for code enforcement?"
- "Where is the planning department located?"
- "How do I file a complaint for a violation?"
- "What are the business license requirements?"
- "How do I contact AGIS division?"

### **Expected Responses:**
- **Direct answers** with relevant information
- **Clickable links** to specific services
- **Contact information** when appropriate
- **311 suggestions** when information isn't available

### **Chatbot Features:**
- **Conversation memory** - remembers previous questions
- **Direct links** - provides clickable service links
- **Professional responses** - no personal contact info exposed
- **Mobile responsive** - works on phones and tablets

---

## 🔒 **Security & Access Control**

### **Environment Variables:**
- Staff don't need to see `.env` file
- Admin manages API keys and URLs
- Staff just use the interface

### **Access Control:**
- Deploy on internal network for staff-only access
- Use VPN if remote access needed
- Regular staff don't need admin privileges

### **Data Privacy:**
- No personal information stored permanently
- Conversation history can be cleared
- API keys secured in environment variables

---

## 📞 **Support & Troubleshooting**

### **For Staff Issues:**
1. **Check internet connection**
2. **Refresh the webpage**
3. **Contact IT support** if chatbot doesn't load
4. **Use 311 as backup** if chatbot is down

### **For Admin Issues:**
1. **Check Streamlit is running**: `streamlit run app.py`
2. **Verify environment variables** in `.env` file
3. **Check network connectivity**
4. **Monitor system resources**

### **Backup Options:**
- **311 Service**: 505-768-2000
- **Planning Department**: 505-924-3860
- **Direct website access**: https://www.cabq.gov/planning

---

## 🎯 **Quick Start Checklist**

### **For Administrators:**
- [ ] Set up `.env` file with API keys
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Test locally: `streamlit run app.py`
- [ ] Deploy to server or cloud
- [ ] Share `index.html` with staff
- [ ] Provide staff training

### **For Staff:**
- [ ] Open `index.html` in browser
- [ ] Test with a simple question
- [ ] Try clicking provided links
- [ ] Ask follow-up questions
- [ ] Report any issues to IT

---

## 📊 **Monitoring & Maintenance**

### **Regular Tasks:**
- **Monitor chatbot performance**
- **Update website content** as needed
- **Review conversation logs** for improvements
- **Update API keys** if necessary
- **Backup configuration** files

### **Performance Metrics:**
- **Response time** - should be under 5 seconds
- **User satisfaction** - track common questions
- **Error rates** - monitor for issues
- **Usage patterns** - identify popular topics

---

## 🔄 **Updates & Improvements**

### **Content Updates:**
- **Add new services** to `get_service_links()`
- **Update contact information** as needed
- **Add new URLs** to scraping list
- **Improve response filtering** based on usage

### **Technical Updates:**
- **Update dependencies** in `requirements.txt`
- **Improve conversation memory** handling
- **Add new features** as requested
- **Optimize performance** based on usage

---

*Last Updated: January 2025*
*Version: 1.0*
*Contact: IT Department for technical support* 