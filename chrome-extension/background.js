// Background service worker
console.log('Ghost Note extension background service worker loaded');

// Listen for installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Ghost Note extension installed');
    
    // Set default settings
    chrome.storage.sync.set({
      ghostNoteUrl: 'http://localhost:8000'
    });
    
    // Open welcome page (optional)
    // chrome.tabs.create({ url: 'welcome.html' });
  } else if (details.reason === 'update') {
    console.log('Ghost Note extension updated');
  }
});

// Listen for messages from content script (if needed for future features)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openGhostNote') {
    chrome.tabs.create({ url: request.url });
    sendResponse({ success: true });
  }
  return true;
});
