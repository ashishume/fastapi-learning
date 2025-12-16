# IPO Tracker Chrome Extension

A Chrome extension boilerplate for tracking IPO (Initial Public Offering) information and updates.

## Features

- **Popup Interface**: Quick access to IPO information
- **Background Service Worker**: Handles data fetching and storage
- **Content Script**: Can extract IPO data from web pages
- **Settings Page**: Configure auto-refresh and other options
- **Local Storage**: Saves tracked IPOs locally

## Project Structure

```
ipo-tracker/
├── manifest.json          # Extension configuration
├── popup.html            # Popup UI
├── popup.js              # Popup logic
├── popup.css             # Popup styling
├── background.js         # Background service worker
├── content.js            # Content script
├── options.html          # Settings page
├── options.js            # Settings page logic
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

## Setup Instructions

### 1. Create Icons

You need to create icon files for the extension. Create an `icons` folder and add:

- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

You can use any image editor or online tool to create these icons.

### 2. Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in the top right)
3. Click "Load unpacked"
4. Select the `ipo-tracker` directory
5. The extension should now appear in your extensions list

### 3. Test the Extension

1. Click the extension icon in the Chrome toolbar
2. The popup should open showing the IPO Tracker interface
3. Click "Settings" to configure options
4. Click "Refresh Data" to test data fetching

## Development

### Manifest V3

This extension uses Manifest V3, the latest Chrome extension format. Key features:

- Service worker instead of background pages
- Improved security and performance
- Modern JavaScript APIs

### Customization

1. **API Integration**: Update `background.js` to connect to your IPO data API
2. **UI Styling**: Modify `popup.css` to match your design
3. **Data Extraction**: Enhance `content.js` to extract IPO data from specific websites
4. **Permissions**: Add required permissions in `manifest.json` if needed

### Adding API Integration

To connect to a real API, update the `refreshIPOData()` function in `background.js`:

```javascript
async function refreshIPOData() {
  try {
    const response = await fetch("https://your-api-endpoint.com/ipos");
    const data = await response.json();

    await chrome.storage.local.set({ trackedIPOs: data });
    return data;
  } catch (error) {
    console.error("Error refreshing IPO data:", error);
    throw error;
  }
}
```

## Permissions

Current permissions:

- `storage`: For saving IPO data locally
- `activeTab`: For accessing current tab information
- `host_permissions`: For making API requests (currently set to all HTTPS sites)

Adjust permissions in `manifest.json` based on your needs.

## Building for Production

1. Test thoroughly in development mode
2. Remove console.log statements
3. Minify JavaScript files (optional)
4. Create a zip file of the extension directory
5. Submit to Chrome Web Store (if publishing)

## License

MIT License - feel free to use this boilerplate for your projects.
