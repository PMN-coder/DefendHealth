const { app, BrowserWindow } = require('electron')

function createWindow () {
  const win = new BrowserWindow({
    width: 900,
    height: 750,
    webPreferences: { nodeIntegration: true }
  })
  win.loadFile('index.html')
}

app.whenReady().then(createWindow)