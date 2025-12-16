// Popup script for IPO Tracker extension

document.addEventListener("DOMContentLoaded", () => {
  const refreshBtn = document.getElementById("refreshBtn");
  const settingsBtn = document.getElementById("settingsBtn");
  const ipoList = document.getElementById("ipoList");
  const autoRefreshStatus = document.getElementById("autoRefreshStatus");
  const lastRefresh = document.getElementById("lastRefresh");

  // Load saved IPOs from storage
  loadIPOs();

  // Load auto-refresh status
  loadAutoRefreshStatus();

  // Update last refresh time
  updateLastRefreshTime();

  // Refresh button handler
  refreshBtn.addEventListener("click", async () => {
    refreshBtn.textContent = "Refreshing...";
    refreshBtn.disabled = true;

    try {
      // Send message to background script to refresh data
      const response = await chrome.runtime.sendMessage({ action: "refresh" });
      console.log("Refresh response:", response);

      // Reload IPOs
      await loadIPOs();

      // Update last refresh time
      updateLastRefreshTime();

      // Show success feedback
      refreshBtn.textContent = "Refreshed!";
      setTimeout(() => {
        refreshBtn.textContent = "Refresh Data";
        refreshBtn.disabled = false;
      }, 1000);
    } catch (error) {
      console.error("Error refreshing:", error);
      refreshBtn.textContent = "Error";
      setTimeout(() => {
        refreshBtn.textContent = "Refresh Data";
        refreshBtn.disabled = false;
      }, 2000);
    }
  });

  // Settings button handler
  settingsBtn.addEventListener("click", () => {
    // Open options page or show settings
    chrome.runtime.openOptionsPage();
  });

  // Load IPOs from storage
  async function loadIPOs() {
    try {
      const result = await chrome.storage.local.get(["trackedIPOs"]);

      console.log(result);
      const ipos = result.trackedIPOs || [];

      if (ipos.length === 0) {
        ipoList.innerHTML = '<p class="empty-state">No IPOs tracked yet</p>';
        return;
      }

      ipoList.innerHTML = ipos
        .map(
          (ipo) => `
        <div class="ipo-item">
          <div class="ipo-header">
            <h3>${ipo.companyName || ipo.ipoName || "Unknown"}</h3>
            <span class="ipo-category ${ipo.category?.toLowerCase() || ""}">${
            ipo.category || ""
          }</span>
          </div>
          <div class="ipo-details">
            <p class="ipo-date">
              <strong>Open:</strong> ${ipo.openDate || "TBD"} | 
              <strong>Close:</strong> ${ipo.closeDate || "TBD"}
            </p>
            <p class="ipo-price">
              <strong>Price Band:</strong> ${ipo.priceBand || "TBD"}
            </p>
            <p class="ipo-size">
              <strong>Issue Size:</strong> ${ipo.issueSize || "TBD"} | 
              <strong>Lot Size:</strong> ${ipo.lotSize || "N/A"}
            </p>
            ${
              ipo.importantDates?.listingDate
                ? `<p class="ipo-listing"><strong>Listing:</strong> ${ipo.importantDates.listingDate}</p>`
                : ""
            }
          </div>
          ${
            ipo.links?.detailPageUrl
              ? `<a href="${ipo.links.detailPageUrl}" target="_blank" class="ipo-link">View Details</a>`
              : ""
          }
        </div>
      `
        )
        .join("");
    } catch (error) {
      console.error("Error loading IPOs:", error);
      ipoList.innerHTML = '<p class="empty-state">Error loading IPOs</p>';
    }
  }

  // Load auto-refresh status
  async function loadAutoRefreshStatus() {
    try {
      const response = await chrome.runtime.sendMessage({
        action: "getSettings",
      });
      if (response.success && response.settings) {
        const settings = response.settings;
        if (settings.autoRefresh) {
          const intervalMinutes = settings.refreshInterval / 60000;
          autoRefreshStatus.innerHTML = `
            <div class="status-indicator active">
              <span class="status-icon">🔄</span>
              <span>Auto-refresh: Every ${intervalMinutes} minute${
            intervalMinutes !== 1 ? "s" : ""
          }</span>
            </div>
          `;
        } else {
          autoRefreshStatus.innerHTML = `
            <div class="status-indicator">
              <span class="status-icon">⏸️</span>
              <span>Auto-refresh: Disabled</span>
            </div>
          `;
        }
      }
    } catch (error) {
      console.error("Error loading auto-refresh status:", error);
    }
  }

  // Update last refresh time
  async function updateLastRefreshTime() {
    try {
      const result = await chrome.storage.local.get(["lastRefresh"]);
      if (result.lastRefresh) {
        const lastRefreshDate = new Date(result.lastRefresh);
        const now = new Date();
        const diffMs = now - lastRefreshDate;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        let timeAgo = "";
        if (diffMins < 1) {
          timeAgo = "Just now";
        } else if (diffMins < 60) {
          timeAgo = `${diffMins} minute${diffMins !== 1 ? "s" : ""} ago`;
        } else if (diffHours < 24) {
          timeAgo = `${diffHours} hour${diffHours !== 1 ? "s" : ""} ago`;
        } else {
          timeAgo = `${diffDays} day${diffDays !== 1 ? "s" : ""} ago`;
        }

        lastRefresh.innerHTML = `
          <span class="last-refresh-text">Last updated: ${timeAgo}</span>
        `;
      } else {
        lastRefresh.innerHTML = `
          <span class="last-refresh-text">Last updated: Never</span>
        `;
      }
    } catch (error) {
      console.error("Error updating last refresh time:", error);
    }
  }

  // Listen for storage changes to update status
  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === "local") {
      if (changes.settings) {
        loadAutoRefreshStatus();
      }
      if (changes.lastRefresh) {
        updateLastRefreshTime();
      }
      if (changes.trackedIPOs) {
        loadIPOs();
      }
    }
  });
});
