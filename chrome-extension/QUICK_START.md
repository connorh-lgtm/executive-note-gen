# 🚀 Quick Start Guide - Ghost Note Chrome Extension

## ⚡ 5-Minute Setup

### Step 1: Load Extension (2 minutes)
1. Open Chrome and go to: `chrome://extensions/`
2. Toggle **"Developer mode"** (top-right)
3. Click **"Load unpacked"**
4. Select folder: `/Users/connorhaley/CascadeProjects/executive-note-gen/chrome-extension/`
5. Done! ✓

### Step 2: Start Ghost Note Server (1 minute)
```bash
cd /Users/connorhaley/CascadeProjects/executive-note-gen
source venv/bin/activate
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Test It (2 minutes)
1. Go to LinkedIn Sales Navigator: https://www.linkedin.com/sales/
2. Open any prospect profile
3. Look for **"Send to Ghost Note"** button (bottom-right corner)
4. Click it!
5. Ghost Note opens with pre-filled data ✨

## 🎯 What Gets Auto-Filled?
- ✅ Prospect Name
- ✅ Job Title  
- ✅ Company Name
- ✅ Profile Summary (as unique fact)

## 🔧 Troubleshooting

**Button not showing?**
- Refresh the Sales Nav page
- Make sure you're on a profile page (not search results)

**Data not extracted?**
- LinkedIn layouts vary - some fields may be empty
- Manually fill in missing fields

**Extension not loading?**
- Check that Developer mode is ON
- Look for errors in `chrome://extensions/`

## 📝 Notes

- Icons are optional (extension works without them)
- Extension only works on Sales Navigator pages
- Data is sent directly to your local Ghost Note (no external servers)

## ✅ You're Ready!

The extension is now live. Every time you're on a Sales Nav profile, just click the button and your form is auto-filled!

---

**Need help?** Check the full INSTALLATION.md guide
