// Content script for IPO Tracker extension
// This script runs in the context of web pages

(function () {
  "use strict";

  console.log("IPO Tracker content script loaded");

  // Listen for messages from popup or background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractIPOData") {
      // Extract IPO-related data from the current page
      const ipoData = extractDataFromPage();
      sendResponse({ success: true, data: ipoData });
    }

    return true;
  });

  // Extract IPO data from the current page
  function extractDataFromPage() {
    const data = {
      url: window.location.href,
      title: document.title,
      timestamp: new Date().toISOString(),
    };

    // TODO: Add specific extraction logic based on IPO tracking websites
    // Example: Look for IPO-related elements on the page

    return data;
  }

  // Optional: Highlight IPO-related content on the page
  function highlightIPOContent() {
    // Implementation for highlighting IPO mentions
  }
})();
