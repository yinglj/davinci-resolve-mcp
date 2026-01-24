import "dotenv/config"
import http from "http"
import { Server } from "socket.io"
import { createApp } from "./app.js"
import { connectDatabase } from "./db.js"
import { config } from "./config.js"
import { setSocket } from "./services/taskService.js"

async function start() {
  await connectDatabase()
  const app = createApp()
  const server = http.createServer(app)
  const io = new Server(server, {
    cors: { origin: config.corsOrigin, credentials: true }
  })
  setSocket(io)
  server.listen(config.port, () => {
    console.log(`Backend listening on ${config.port}`)
  })
}

start().catch((error) => {
  console.error(error)
  process.exit(1)
})
