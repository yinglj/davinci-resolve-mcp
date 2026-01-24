import type { Server } from "socket.io"
import { Task } from "../models/Task.js"
import type { TaskDocument } from "../models/Task.js"
import type { TaskAssetInput, TaskAssetItem, TaskAssets, TaskInput, TaskStatus } from "../types.js"
import { callMcp } from "./mcpClient.js"

let socketServer: Server | null = null

export function setSocket(server: Server) {
  socketServer = server
}

function emitTaskUpdate(task: TaskDocument) {
  if (socketServer) {
    socketServer.emit("task:update", task)
  }
}

export async function listTasks(ownerId?: string) {
  const query = ownerId ? { ownerId } : {}
  return Task.find(query).sort({ updatedAt: -1 }).lean()
}

export async function getTaskById(id: string, ownerId?: string) {
  const query = ownerId ? { _id: id, ownerId } : { _id: id }
  return Task.findOne(query).lean()
}

const allowedExtensions = {
  video: ["mp4", "mov", "mkv", "webm"],
  image: ["png", "jpg", "jpeg", "gif", "webp"],
  audio: ["mp3", "wav", "aac", "flac", "ogg"]
}

const normalizeUrls = (values?: string[]) =>
  (values || []).map((value) => value.trim()).filter(Boolean)

const detectExtension = (url: string) => {
  const value = url.split("?")[0]
  const parts = value.split(".")
  if (parts.length < 2) {
    return ""
  }
  return parts[parts.length - 1].toLowerCase()
}

const matchesType = (type: TaskAssetItem["type"], mime?: string, extension?: string) => {
  if (mime) {
    if (type === "video") return mime.startsWith("video/")
    if (type === "image") return mime.startsWith("image/")
    if (type === "audio") return mime.startsWith("audio/")
  }
  if (extension) {
    return allowedExtensions[type].includes(extension)
  }
  return false
}

const fetchMetadata = async (url: string) => {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 8000)
  try {
    const response = await fetch(url, { method: "HEAD", signal: controller.signal })
    const mime = response.headers.get("content-type") || undefined
    const length = response.headers.get("content-length") || undefined
    const size = length ? Number(length) : undefined
    return { ok: response.ok, mime, size: Number.isFinite(size) ? size : undefined }
  } catch {
    return { ok: false, mime: undefined, size: undefined }
  } finally {
    clearTimeout(timeout)
  }
}

const prepareAsset = async (url: string, type: TaskAssetItem["type"]): Promise<TaskAssetItem> => {
  let parsedUrl = ""
  try {
    parsedUrl = new URL(url).toString()
  } catch {
    return { url, type, source: "url", status: "invalid", error: "invalid url" }
  }
  const metadata = await fetchMetadata(parsedUrl)
  const extension = detectExtension(parsedUrl)
  const valid = metadata.ok && matchesType(type, metadata.mime, extension)
  if (!metadata.ok && !extension) {
    return { url: parsedUrl, type, source: "url", status: "unverified" }
  }
  if (!matchesType(type, metadata.mime, extension)) {
    return { url: parsedUrl, type, source: "url", status: "invalid", mime: metadata.mime }
  }
  return {
    url: parsedUrl,
    type,
    source: "url",
    status: valid ? "validated" : "unverified",
    mime: metadata.mime,
    size: metadata.size
  }
}

const prepareAssets = async (input?: TaskAssetInput): Promise<TaskAssets | undefined> => {
  if (!input) {
    return undefined
  }
  const videos = normalizeUrls(input.videos)
  const images = normalizeUrls(input.images)
  const audios = normalizeUrls(input.audios)
  const [videoItems, imageItems, audioItems] = await Promise.all([
    Promise.all(videos.map((url) => prepareAsset(url, "video"))),
    Promise.all(images.map((url) => prepareAsset(url, "image"))),
    Promise.all(audios.map((url) => prepareAsset(url, "audio")))
  ])
  return {
    videos: videoItems.length ? videoItems : undefined,
    images: imageItems.length ? imageItems : undefined,
    audios: audioItems.length ? audioItems : undefined
  }
}

export async function createTask(input: TaskInput, ownerId?: string) {
  const assets = await prepareAssets(input.assets)
  const hasInvalidAsset = ["videos", "images", "audios"].some((key) => {
    const list = assets?.[key as keyof TaskAssets]
    return Array.isArray(list) && list.some((item) => item.status === "invalid")
  })
  const initialStatus: TaskStatus =
    input.mcp && !hasInvalidAsset ? "running" : hasInvalidAsset ? "failed" : "pending"
  const task = await Task.create({
    ownerId,
    title: input.title,
    prompt: input.prompt,
    scenarioId: input.scenarioId,
    scenarioVersion: input.scenarioVersion,
    assets,
    status: initialStatus,
    steps: input.steps || [],
    mcp: input.mcp,
    retryCount: 0,
    error: hasInvalidAsset ? "素材校验未通过" : undefined
  })
  const taskObject = task.toObject()
  emitTaskUpdate(taskObject)
  if (input.mcp && !hasInvalidAsset) {
    void runMcpTask(taskObject._id.toString(), input.mcp)
  }
  return taskObject
}

export async function retryTask(id: string, ownerId?: string) {
  const query = ownerId ? { _id: id, ownerId } : { _id: id }
  const task = await Task.findOne(query)
  if (!task) {
    return null
  }
  if (!task.mcp) {
    return task.toObject()
  }
  task.status = "running"
  task.error = undefined
  task.result = undefined
  task.retryCount = (task.retryCount || 0) + 1
  await task.save()
  const taskObject = task.toObject()
  emitTaskUpdate(taskObject)
  void runMcpTask(taskObject._id.toString(), task.mcp)
  return taskObject
}

async function runMcpTask(id: string, mcp: NonNullable<TaskInput["mcp"]>) {
  try {
    const result = await callMcp(mcp)
    const updated = await Task.findByIdAndUpdate(
      id,
      { status: "completed", result },
      { new: true }
    ).lean()
    if (updated) {
      emitTaskUpdate(updated)
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error"
    const updated = await Task.findByIdAndUpdate(
      id,
      { status: "failed", error: message },
      { new: true }
    ).lean()
    if (updated) {
      emitTaskUpdate(updated)
    }
  }
}
