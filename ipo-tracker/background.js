// Background service worker for IPO Tracker extension

// Initialize auto-refresh on startup
async function initializeAutoRefresh() {
  try {
    if (typeof chrome !== "undefined" && chrome.alarms) {
      const result = await chrome.storage.local.get(["settings"]);
      const settings = result.settings || {
        autoRefresh: false,
        refreshInterval: 3600000,
      };

      // Clear any existing alarm first
      await chrome.alarms.clear("refreshIPOs");

      // Only create alarm if auto-refresh is enabled
      if (settings.autoRefresh) {
        chrome.alarms.create("refreshIPOs", {
          periodInMinutes: settings.refreshInterval / 60000,
        });
        console.log(
          "Auto-refresh enabled:",
          settings.refreshInterval / 60000,
          "minutes"
        );
      } else {
        console.log("Auto-refresh is disabled");
      }
    }
  } catch (error) {
    console.warn("Error initializing auto-refresh:", error);
  }
}

// Install event - runs when extension is first installed or updated
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log("IPO Tracker extension installed/updated:", details.reason);

  if (details.reason === "install") {
    // Initialize default storage
    await chrome.storage.local.set({
      trackedIPOs: [],
      settings: {
        autoRefresh: false,
        refreshInterval: 3600000, // 1 hour in milliseconds
      },
    });
  }

  // Initialize auto-refresh if enabled
  await initializeAutoRefresh();
});

// Initialize auto-refresh when service worker starts
initializeAutoRefresh();

// Message handler from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Message received:", request);

  if (request.action === "refresh") {
    // Handle refresh action
    refreshIPOData()
      .then((data) => {
        sendResponse({ success: true, data });
      })
      .catch((error) => {
        sendResponse({ success: false, error: error.message });
      });

    // Return true to indicate we will send a response asynchronously
    return true;
  }

  if (request.action === "saveIPO") {
    // Save IPO to storage
    saveIPO(request.data)
      .then(() => {
        sendResponse({ success: true });
      })
      .catch((error) => {
        sendResponse({ success: false, error: error.message });
      });

    return true;
  }

  if (request.action === "updateSettings") {
    // Handle settings update from options page
    initializeAutoRefresh()
      .then(() => {
        sendResponse({ success: true });
      })
      .catch((error) => {
        sendResponse({ success: false, error: error.message });
      });

    return true;
  }

  if (request.action === "getSettings") {
    // Get current settings
    chrome.storage.local
      .get(["settings"])
      .then((result) => {
        sendResponse({ success: true, settings: result.settings });
      })
      .catch((error) => {
        sendResponse({ success: false, error: error.message });
      });

    return true;
  }
});

// Refresh IPO data
async function refreshIPOData() {
  try {
    const response = await fetch(
      "http://localhost:8003/scrap/upcoming_ipos?use_gemini=true&clean_html=true"
    );

    // Check if response is ok
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Fetched IPO data:", data);

    // Extract IPOs from gemini_analysis if available, otherwise use ipos array
    const ipos = data.gemini_analysis?.ipos || data.ipos || [];

    // Save to storage with last refresh timestamp
    await chrome.storage.local.set({
      trackedIPOs: ipos,
      lastRefresh: new Date().toISOString(),
    });

    return ipos;
  } catch (error) {
    console.error("Error refreshing IPO data:", error);

    // If it's a network error (like connection refused), provide helpful message
    if (
      error.message.includes("Failed to fetch") ||
      error.message.includes("NetworkError")
    ) {
      throw new Error(
        "Cannot connect to localhost:8003. Make sure your API server is running."
      );
    }

    throw error;
  }
}

// Save IPO to storage
async function saveIPO(ipoData) {
  try {
    const result = await chrome.storage.local.get(["trackedIPOs"]);
    const ipos = result.trackedIPOs || [];

    // Check if IPO already exists
    const exists = ipos.some((ipo) => ipo.name === ipoData.name);
    if (!exists) {
      ipos.push(ipoData);
      await chrome.storage.local.set({ trackedIPOs: ipos });
    }

    return true;
  } catch (error) {
    console.error("Error saving IPO:", error);
    throw error;
  }
}

// Periodic refresh (if enabled in settings)
// Check if alarms API is available
try {
  if (typeof chrome !== "undefined" && chrome.alarms) {
    chrome.alarms.onAlarm.addListener(async (alarm) => {
      if (alarm.name === "refreshIPOs") {
        // Double-check that auto-refresh is still enabled before refreshing
        const result = await chrome.storage.local.get(["settings"]);
        const settings = result.settings || { autoRefresh: false };

        if (settings.autoRefresh === true) {
          console.log("Auto-refresh alarm fired - refreshing IPO data");
          refreshIPOData();
        } else {
          console.log(
            "Auto-refresh alarm fired but auto-refresh is disabled - clearing alarm"
          );
          chrome.alarms.clear("refreshIPOs");
        }
      }
    });
  }
} catch (error) {
  console.warn("Alarms API not available:", error);
}

// Set up periodic refresh when settings change
chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === "local" && changes.settings) {
    try {
      if (typeof chrome !== "undefined" && chrome.alarms) {
        const settings = changes.settings.newValue;

        // Always clear existing alarm first
        chrome.alarms.clear("refreshIPOs");

        // Only create new alarm if auto-refresh is explicitly enabled
        if (settings && settings.autoRefresh === true) {
          chrome.alarms.create("refreshIPOs", {
            periodInMinutes: settings.refreshInterval / 60000,
          });
          console.log(
            "Auto-refresh enabled:",
            settings.refreshInterval / 60000,
            "minutes"
          );
        } else {
          console.log("Auto-refresh disabled - alarm cleared");
        }
      }
    } catch (error) {
      console.warn("Error setting up alarms:", error);
    }
  }
});
