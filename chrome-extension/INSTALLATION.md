# Ghost Note Chrome Extension - Installation Guide

## 📦 Installation Steps

### 1. Download the Extension
The extension files are located in:
```
/Users/connorhaley/CascadeProjects/executive-note-gen/chrome-extension/
```

### 2. Create Icons (Temporary)
Since we don't have custom icons yet, create simple placeholder icons:

**Option A: Use online icon generator**
- Go to https://www.favicon-generator.org/
- Upload a simple "G" logo or Ghost icon
- Generate 16x16, 48x48, and 128x128 sizes
- Save as `icon16.png`, `icon48.png`, `icon128.png` in the `icons/` folder

**Option B: Use emoji as icon (quick)**
- Take screenshots of 👻 emoji at different sizes
- Save as PNG files in `icons/` folder

### 3. Load Extension in Chrome

1. **Open Chrome Extensions Page**
   - Go to `chrome://extensions/`
   - Or: Menu → More Tools → Extensions

2. **Enable Developer Mode**
   - Toggle "Developer mode" switch in top-right corner

3. **Load Unpacked Extension**
   - Click "Load unpacked" button
   - Navigate to: `/Users/connorhaley/CascadeProjects/executive-note-gen/chrome-extension/`
   - Click "Select"

4. **Verify Installation**
   - You should see "Ghost Note - LinkedIn Sales Nav Integration" in your extensions list
   - Pin the extension to your toolbar (optional)

### 4. Configure Settings

1. **Click Extension Icon**
   - Click the Ghost Note icon in Chrome toolbar
   - Or: Click puzzle piece icon → Ghost Note

2. **Set Ghost Note URL**
   - Default: `http://localhost:8000`
   - Change if running on different port/domain
   - Click "Save Settings"

### 5. Test the Extension

1. **Start Ghost Note Server**
   ```bash
   cd /Users/connorhaley/CascadeProjects/executive-note-gen
   source venv/bin/activate
   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Go to LinkedIn Sales Navigator**
   - Navigate to: https://www.linkedin.com/sales/
   - Open any prospect profile

3. **Look for the Button**
   - You should see a floating "Send to Ghost Note" button (bottom-right)
   - If not, refresh the page

4. **Click the Button**
   - Data should be extracted
   - New tab opens with Ghost Note
   - Form should be pre-filled

## 🎯 Usage

### On Sales Navigator Profile Pages:
1. Browse to any prospect profile
2. Click "Send to Ghost Note" button (bottom-right)
3. Review auto-filled data in Ghost Note
4. Select message type
5. Generate email

### Supported Data:
- ✅ Prospect Name
- ✅ Job Title
- ✅ Company Name
- ✅ Profile Summary (as unique fact)
- ✅ LinkedIn URL (for reference)

## 🔧 Troubleshooting

### Button Not Appearing
- **Check URL**: Make sure you're on `linkedin.com/sales/*`
- **Refresh Page**: Hard refresh (Cmd+Shift+R on Mac)
- **Check Console**: Open DevTools → Console for errors
- **Reinstall**: Remove and reload extension

### Data Not Extracted
- **LinkedIn Layout**: Sales Nav has multiple layouts
- **Wait for Page Load**: Let page fully load before clicking
- **Manual Entry**: Fall back to manual entry if needed

### Extension Not Loading
- **Developer Mode**: Ensure it's enabled
- **Manifest Errors**: Check for red errors in extensions page
- **Permissions**: Extension needs LinkedIn access

### Ghost Note Not Opening
- **Check URL**: Verify URL in extension settings
- **Server Running**: Make sure Ghost Note server is running
- **Port**: Confirm correct port (default 8000)
- **Pop-up Blocker**: Allow pop-ups from LinkedIn

## 🔄 Updates

### To Update Extension:
1. Make changes to extension files
2. Go to `chrome://extensions/`
3. Click refresh icon on Ghost Note extension
4. Test changes

### Auto-Reload During Development:
- Chrome will auto-reload content scripts on page refresh
- Background worker requires manual extension reload
- Popup changes require closing/reopening popup

## 🚀 Next Steps

1. **Create Custom Icons**
   - Design proper 16x16, 48x48, 128x128 icons
   - Use Ghost Note branding colors

2. **Test on Multiple Profiles**
   - Different Sales Nav layouts
   - Various profile types
   - Edge cases (missing data)

3. **Gather Feedback**
   - Track extraction accuracy
   - Note any layout issues
   - Collect user suggestions

4. **Iterate**
   - Improve selectors based on failures
   - Add more data fields
   - Enhance UI/UX

## 📝 Notes

- Extension only works on Sales Navigator pages
- Requires active LinkedIn session
- Data extraction is client-side only
- No data sent to external servers (except Ghost Note)
- Respects LinkedIn's terms of service

## 🆘 Support

If you encounter issues:
1. Check browser console for errors
2. Verify all files are present
3. Ensure Ghost Note server is running
4. Review this guide for troubleshooting steps

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-09
