// Content script for LinkedIn Sales Navigator
console.log('Ghost Note extension loaded on Sales Navigator');

// Function to extract prospect data from Sales Nav profile page
async function extractProspectData() {
  const data = {
    prospect_name: '',
    prospect_title: '',
    prospect_company: '',
    unique_fact: '',
    linkedin_url: window.location.href
  };

  try {
    console.log('Starting data extraction...');
    
    // First, try to expand "Show more" in About section
    const showMoreButtons = document.querySelectorAll('button, a');
    for (const button of showMoreButtons) {
      if (button.textContent.includes('Show more') || button.textContent.includes('see more')) {
        console.log('Clicking Show more button');
        button.click();
        // Wait a bit for content to expand
        await new Promise(resolve => setTimeout(resolve, 500));
        break;
      }
    }

    // Extract name - Sales Nav 2024/2025 layouts
    const nameSelectors = [
      // Sales Nav specific - near profile photo
      '.profile-topcard__name',
      '.profile-topcard-person-entity__name',
      'div.profile-topcard h1',
      'div[class*="profile-topcard"] h1',
      '.artdeco-entity-lockup__title',
      'h1.text-heading-xlarge',
      // More specific patterns
      'div.pv-top-card h1',
      'section[class*="profile"] h1'
    ];
    
    for (const selector of nameSelectors) {
      const elements = document.querySelectorAll(selector);
      for (const element of elements) {
        const text = element.textContent.trim();
        // Filter out page titles and navigation text
        if (text && text.length > 2 && text.length < 100 && 
            !text.includes('Sales Navigator') && 
            !text.includes('Page') &&
            !text.includes('LinkedIn')) {
          data.prospect_name = text;
          console.log('Found name:', text, 'using selector:', selector);
          break;
        }
      }
      if (data.prospect_name) break;
    }
    
    // If still not found, try page title as last resort but clean it
    if (!data.prospect_name) {
      const titleMatch = document.title.match(/^([^|]+)/);
      if (titleMatch) {
        const name = titleMatch[1].trim();
        if (name && !name.includes('Sales Navigator') && !name.includes('LinkedIn')) {
          data.prospect_name = name;
          console.log('Found name from title:', name);
        }
      }
    }

    // Extract title - look for headline/title patterns
    // First try standard selectors
    const titleSelectors = [
      '.profile-topcard__headline',
      '.profile-topcard-person-entity__headline',
      'div.profile-topcard div.text-body-medium',
      'div[class*="profile-topcard"] div[class*="headline"]',
      '[data-anonymize="title"]',
      '.artdeco-entity-lockup__subtitle',
      'div.pv-top-card div.text-body-medium',
      // Try elements near the name
      'div.profile-topcard span.text-body-medium',
      'div[class*="profile"] span.text-body-medium'
    ];
    
    for (const selector of titleSelectors) {
      const elements = document.querySelectorAll(selector);
      for (const element of elements) {
        const text = element.textContent.trim();
        // Filter out non-title text and buttons
        if (text && text.length > 5 && text.length < 200 && 
            !text.includes('Message') && 
            !text.includes('Connect') &&
            !text.includes('Follow') &&
            !text.includes('More') &&
            !text.includes('Sales Navigator') &&
            !text.toLowerCase().includes('button')) {
          data.prospect_title = text;
          console.log('Found title:', text, 'using selector:', selector);
          break;
        }
      }
      if (data.prospect_title) break;
    }
    
    // If title not found, try to find text BELOW/AFTER the name element
    if (!data.prospect_title && data.prospect_name) {
      console.log('Trying to find title below name element...');
      
      // Find the name element first
      const nameElement = Array.from(document.querySelectorAll('h1, div, span')).find(el => 
        el.textContent.trim() === data.prospect_name
      );
      
      if (nameElement) {
        // Look for next sibling or nearby elements
        let nextElement = nameElement.nextElementSibling;
        let attempts = 0;
        
        while (nextElement && attempts < 5) {
          const text = nextElement.textContent.trim();
          if (text && text.length > 5 && text.length < 200 && 
              text !== data.prospect_name &&
              !text.includes('Message') && 
              !text.includes('Connect') &&
              !text.includes('Follow') &&
              !text.includes('More')) {
            data.prospect_title = text;
            console.log('Found title below name:', text);
            break;
          }
          nextElement = nextElement.nextElementSibling;
          attempts++;
        }
        
        // If still not found, look in parent's next elements
        if (!data.prospect_title && nameElement.parentElement) {
          const parentNext = nameElement.parentElement.nextElementSibling;
          if (parentNext) {
            const text = parentNext.textContent.trim();
            if (text && text.length > 5 && text.length < 200 && 
                !text.includes('Message') && !text.includes('Connect')) {
              data.prospect_title = text;
              console.log('Found title in parent next:', text);
            }
          }
        }
      }
    }

    // Extract company - look for company mentions
    const companySelectors = [
      '.profile-topcard__company-name',
      '[data-anonymize="company-name"]',
      'button[aria-label*="Current company"]',
      'a[data-control-name*="company"]',
      '.artdeco-entity-lockup__caption'
    ];
    
    for (const selector of companySelectors) {
      const elements = document.querySelectorAll(selector);
      for (const element of elements) {
        const text = element.textContent.trim();
        if (text && text.length > 1 && text.length < 150) {
          data.prospect_company = text;
          console.log('Found company:', text);
          break;
        }
      }
      if (data.prospect_company) break;
    }

    // Fallback: Try to extract from page text if specific selectors fail
    if (!data.prospect_name || !data.prospect_company) {
      console.log('Using fallback extraction...');
      
      // Try to get name from page title
      if (!data.prospect_name) {
        const titleMatch = document.title.match(/^([^|]+)/);
        if (titleMatch) {
          const name = titleMatch[1].trim();
          if (name && name.length > 2 && name.length < 100) {
            data.prospect_name = name;
            console.log('Found name from title:', name);
          }
        }
      }
      
      // Try to find company in visible text
      if (!data.prospect_company) {
        const bodyText = document.body.innerText;
        const companyMatch = bodyText.match(/at\s+([A-Z][A-Za-z\s&,.-]+?)(?:\s*\||$)/);
        if (companyMatch && companyMatch[1]) {
          data.prospect_company = companyMatch[1].trim();
          console.log('Found company from text:', data.prospect_company);
        }
      }
    }

    // Extract full bio/about section for AI summarization
    // Sales Nav specific selectors
    const summarySelectors = [
      // Sales Nav 2024/2025 layouts
      'section.profile-summary',
      'div.profile-summary',
      'section[data-test-profile-summary]',
      'div[data-test-profile-summary]',
      '.profile-topcard__summary',
      '[data-test-id="about-section"]',
      '.pv-about-section',
      '.inline-show-more-text',
      'section[data-section="summary"]',
      'div[class*="about"] div[class*="show-more"]',
      // Try broader search
      'section:has(h2:contains("About"))',
      'div.artdeco-card section'
    ];
    
    let fullBio = '';
    
    // Try specific selectors first
    for (const selector of summarySelectors) {
      try {
        const summaryElement = document.querySelector(selector);
        if (summaryElement && summaryElement.textContent.trim()) {
          fullBio = summaryElement.textContent.trim();
          // Filter out section headers
          fullBio = fullBio.replace(/^About\s*/i, '').trim();
          if (fullBio.length > 50) {
            console.log('Found bio using selector:', selector, 'length:', fullBio.length);
            break;
          }
        }
      } catch (e) {
        // Skip invalid selectors
      }
    }
    
    // PRIORITY: Try to find About section directly in DOM first
    if (!fullBio) {
      console.log('Trying direct DOM About section extraction...');
      
      // Find all headings that say "About"
      const allHeadings = document.querySelectorAll('h2, h3, div[class*="heading"], div[class*="title"]');
      for (const heading of allHeadings) {
        if (heading.textContent.trim().toLowerCase() === 'about') {
          console.log('Found About heading in DOM');
          // Get the next sibling or parent's next sibling that contains text
          let contentElement = heading.nextElementSibling;
          if (!contentElement && heading.parentElement) {
            contentElement = heading.parentElement.nextElementSibling;
          }
          
          if (contentElement) {
            const text = contentElement.textContent.trim();
            if (text.length > 50 && !text.includes('Relationship') && !text.includes('Experience')) {
              fullBio = text.replace(/Show (more|less)/gi, '').trim();
              console.log('Found bio via DOM traversal, length:', fullBio.length);
              break;
            }
          }
        }
      }
    }
    
    // Fallback: Look for "About" section in page text
    if (!fullBio) {
      console.log('Trying About section extraction from page text...');
      const bodyText = document.body.innerText;
      const lines = bodyText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
      
      console.log('Total lines in page:', lines.length);
      
      // Find "About" heading followed by actual bio content (not UI elements)
      let aboutIndex = -1;
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].toLowerCase();
        if (line === 'about' || line === 'about this profile') {
          // Check if next few lines contain bio-like content
          let hasBioContent = false;
          for (let j = i + 1; j < i + 5 && j < lines.length; j++) {
            const nextLine = lines[j];
            // Look for bio indicators (longer text, not UI elements)
            if (nextLine.length > 20 && 
                !nextLine.includes('Relationship') &&
                !nextLine.includes('Experience') &&
                !nextLine.includes('Get insights') &&
                !nextLine.includes('Generate Lead')) {
              hasBioContent = true;
              break;
            }
          }
          if (hasBioContent) {
            aboutIndex = i;
            console.log('Found About with bio content at line', i, ':', lines[i]);
            break;
          } else {
            console.log('Skipping About at line', i, '- no bio content after it');
          }
        }
      }
      
      if (aboutIndex >= 0) {
        // Extract lines after "About" until we hit another section
        const stopWords = ['experience', 'education', 'licenses', 'skills', 'activity', 'recommendations', 'recent post', 'mutual connection', 'teamlink'];
        let bioLines = [];
        
        // Debug: show next 30 lines after About
        console.log('Lines after About:');
        for (let i = aboutIndex + 1; i < aboutIndex + 31 && i < lines.length; i++) {
          console.log(`  Line ${i}: "${lines[i]}"`);
        }
        
        for (let i = aboutIndex + 1; i < lines.length && i < aboutIndex + 40; i++) {
          const line = lines[i];
          const lineLower = line.toLowerCase();
          
          // Stop at next major section
          if (stopWords.some(word => lineLower === word || lineLower.startsWith(word + ' '))) {
            console.log('Stopping at:', line);
            break;
          }
          
          // Skip common UI elements but NOT "Relationship" as a stop word
          if (line.includes('Message') || line.includes('Connect') || 
              line.includes('Save to') || line.includes('Send InMail') ||
              line.includes('Account has') || line.includes('intent') ||
              line.includes('View profile') || line.includes('See all') ||
              line.includes('Get insights') || line.includes('BETA') ||
              line.includes('Learn more') || line.includes('Enrich or push') ||
              line.includes('Push to') || line.includes('FIND EMAIL') ||
              line.includes('FIND PHONE') || line.includes('Powered by') ||
              line.includes('Not added to') || line.includes('Email') === line ||
              line.includes('Phone') === line || line.includes('CRM') === line ||
              lineLower === 'relationship' ||
              line.length < 10) {
            console.log('Skipping UI line:', line);
            continue;
          }
          
          bioLines.push(line);
          console.log('Added bio line:', line);
        }
        
        if (bioLines.length > 0) {
          fullBio = bioLines.join('\n');
          console.log('Found bio after About heading, length:', fullBio.length, 'lines:', bioLines.length);
        } else {
          console.log('No bio lines found after About heading');
        }
      } else {
        console.log('About heading not found in page text');
      }
    }
    
    // Clean up the bio - remove common Sales Nav UI text
    if (fullBio) {
      fullBio = fullBio
        .replace(/Account has.*?intent/gi, '')
        .replace(/Buyer intent/gi, '')
        .replace(/Save to list/gi, '')
        .replace(/Send InMail/gi, '')
        .replace(/View similar/gi, '')
        .replace(/Show more/gi, '')
        .replace(/Show less/gi, '')
        .trim();
      
      console.log('Cleaned bio text:', fullBio);
    }
    
    // Store full bio for AI summarization
    data.full_bio = fullBio;
    
    // DO NOT auto-fill unique_fact - leave empty for manual entry
    data.unique_fact = '';

    console.log('Extraction complete:', data);

  } catch (error) {
    console.error('Error extracting prospect data:', error);
  }

  return data;
}

// Create floating button
function createFloatingButton() {
  // Check if button already exists
  if (document.getElementById('ghost-note-button')) {
    return;
  }

  const button = document.createElement('button');
  button.id = 'ghost-note-button';
  button.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
    </svg>
    <span>Send to Ghost Note</span>
  `;
  
  button.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 9999;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;

  button.addEventListener('mouseenter', () => {
    button.style.transform = 'translateY(-2px)';
    button.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
  });

  button.addEventListener('mouseleave', () => {
    button.style.transform = 'translateY(0)';
    button.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
  });

  button.addEventListener('click', async () => {
    button.disabled = true;
    button.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v6l4 2"/>
      </svg>
      <span>Extracting...</span>
    `;

    const data = await extractProspectData();
    
    // Validate data
    if (!data.prospect_name || !data.prospect_company) {
      alert('Could not extract prospect data. Please make sure you are on a Sales Navigator profile page.');
      button.disabled = false;
      button.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <span>Send to Ghost Note</span>
      `;
      return;
    }

    // Get Ghost Note URL from storage
    chrome.storage.sync.get(['ghostNoteUrl'], async (result) => {
      const baseUrl = result.ghostNoteUrl || 'http://localhost:8000';
      
      console.log('Full bio extracted:', data.full_bio ? `${data.full_bio.length} chars` : 'NONE');
      console.log('Fallback unique fact:', data.unique_fact);
      
      // If we have a bio, summarize it with AI
      let uniqueFact = data.unique_fact || '';
      if (data.full_bio && data.full_bio.length > 50) {
        button.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          <span>Summarizing bio...</span>
        `;
        
        try {
          const response = await fetch(`${baseUrl}/api/summarize-bio`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              bio_text: data.full_bio,
              prospect_name: data.prospect_name,
              prospect_title: data.prospect_title
            })
          });
          
          if (response.ok) {
            const result = await response.json();
            console.log('Summarization API response:', result);
            if (result.summary) {
              uniqueFact = result.summary;
              console.log('AI summarized bio:', uniqueFact);
            } else {
              console.log('No summary returned, using fallback');
            }
          } else {
            console.error('Summarization API failed:', response.status);
          }
        } catch (error) {
          console.error('Failed to summarize bio:', error);
          // Continue with original bio if summarization fails
        }
      }
      
      console.log('Final unique fact to send:', uniqueFact);
      
      // Build URL with query parameters
      const params = new URLSearchParams({
        prospect_name: data.prospect_name,
        prospect_title: data.prospect_title || '',
        prospect_company: data.prospect_company,
        unique_fact: data.unique_fact || '',
        linkedin_insight: uniqueFact || '',
        linkedin_url: data.linkedin_url
      });

      const url = `${baseUrl}?${params.toString()}`;
      
      // Open Ghost Note in new tab
      window.open(url, '_blank');

      // Reset button
      setTimeout(() => {
        button.disabled = false;
        button.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 13l4 4L19 7"/>
          </svg>
          <span>Sent!</span>
        `;
        
        setTimeout(() => {
          button.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <span>Send to Ghost Note</span>
          `;
        }, 2000);
      }, 500);
    });
  });

  document.body.appendChild(button);
}

// Initialize when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', createFloatingButton);
} else {
  createFloatingButton();
}

// Re-create button on navigation (Sales Nav is a SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    setTimeout(createFloatingButton, 1000);
  }
}).observe(document, { subtree: true, childList: true });
