const { app, BrowserWindow } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

// Check if running in development mode
const isDev = !app.isPackaged

// Backend process reference
let backendProcess = null

// Start the backend server
function startBackend() {
  if (isDev) {
    console.log('Development mode: Backend should be started manually')
    return Promise.resolve()
  }

  return new Promise((resolve, reject) => {
    // In production, the backend exe is in the resources folder
    const backendExePath = path.join(process.resourcesPath, 'backend', 'ScriptEditorAPI.exe')
    
    console.log('Starting backend from:', backendExePath)
    
    try {
      // Spawn the backend process
      backendProcess = spawn(backendExePath, [], {
        stdio: ['ignore', 'pipe', 'pipe'],
        windowsHide: false
      })

      // Log backend stdout
      backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`)
      })

      // Log backend stderr
      backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`)
      })

      // Handle backend process exit
      backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`)
        backendProcess = null
      })

      backendProcess.on('error', (err) => {
        console.error('Failed to start backend:', err)
        reject(err)
      })

      // Wait a bit for the backend to start
      // In a production app, you might want to poll the health endpoint
      setTimeout(() => {
        console.log('Backend started successfully')
        resolve()
      }, 2000)

    } catch (err) {
      console.error('Failed to spawn backend process:', err)
      reject(err)
    }
  })
}

// Stop the backend server
function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend process...')
    
    // On Windows, we need to kill the process tree
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t'])
    } else {
      backendProcess.kill('SIGTERM')
    }
    
    backendProcess = null
  }
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
      devTools: true,
    },
    title: 'LingChat Script Editor',
  })

  // In development, load from Vite dev server
  if (isDev) {
    mainWindow.loadURL('http://localhost:5174')
    mainWindow.webContents.openDevTools()
  } else {
    // In production, load the built files
    // __dirname points to electron folder inside app.asar
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
    // Open DevTools for debugging (remove in production)
    mainWindow.webContents.openDevTools()
  }

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    require('electron').shell.openExternal(url)
    return { action: 'deny' }
  })
}

// App lifecycle
app.whenReady().then(async () => {
  try {
    // Start backend first
    await startBackend()
    
    // Then create the window
    createWindow()

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow()
      }
    })
  } catch (err) {
    console.error('Failed to start application:', err)
    app.quit()
  }
})

// Clean up on window close
app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// Clean up on app quit
app.on('will-quit', () => {
  stopBackend()
})

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err)
  stopBackend()
})