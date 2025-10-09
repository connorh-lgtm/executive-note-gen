// Popup script for settings
document.addEventListener('DOMContentLoaded', () => {
  const urlInput = document.getElementById('ghostNoteUrl');
  const saveBtn = document.getElementById('saveBtn');
  const status = document.getElementById('status');

  // Load saved settings
  chrome.storage.sync.get(['ghostNoteUrl'], (result) => {
    if (result.ghostNoteUrl) {
      urlInput.value = result.ghostNoteUrl;
    }
  });

  // Save settings
  saveBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    
    // Validate URL
    if (!url) {
      showStatus('Please enter a URL', 'error');
      return;
    }
    
    try {
      new URL(url);
    } catch (e) {
      showStatus('Please enter a valid URL', 'error');
      return;
    }

    // Save to storage
    chrome.storage.sync.set({ ghostNoteUrl: url }, () => {
      showStatus('Settings saved successfully!', 'success');
      
      // Clear status after 3 seconds
      setTimeout(() => {
        status.style.display = 'none';
      }, 3000);
    });
  });

  function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
  }
});
