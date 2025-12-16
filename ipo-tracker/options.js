// Options page script

document.addEventListener("DOMContentLoaded", () => {
  const autoRefreshCheckbox = document.getElementById("autoRefresh");
  const refreshIntervalInput = document.getElementById("refreshInterval");
  const saveBtn = document.getElementById("saveBtn");
  const statusDiv = document.getElementById("status");

  // Load current settings
  loadSettings();

  // Save settings
  saveBtn.addEventListener("click", async () => {
    const settings = {
      autoRefresh: autoRefreshCheckbox.checked,
      refreshInterval: parseInt(refreshIntervalInput.value) * 60000, // Convert to milliseconds
    };

    try {
      await chrome.storage.local.set({ settings });
      showStatus("Settings saved successfully!", true);

      // Update background script if needed
      chrome.runtime.sendMessage({ action: "updateSettings", settings });
    } catch (error) {
      console.error("Error saving settings:", error);
      showStatus("Error saving settings", false);
    }
  });

  async function loadSettings() {
    try {
      const result = await chrome.storage.local.get(["settings"]);
      const settings = result.settings || {
        autoRefresh: false,
        refreshInterval: 3600000,
      };

      autoRefreshCheckbox.checked = settings.autoRefresh;
      refreshIntervalInput.value = settings.refreshInterval / 60000; // Convert from milliseconds
    } catch (error) {
      console.error("Error loading settings:", error);
    }
  }

  function showStatus(message, success) {
    statusDiv.textContent = message;
    statusDiv.className = success ? "success" : "";
    setTimeout(() => {
      statusDiv.className = "";
      statusDiv.textContent = "";
    }, 3000);
  }
});
