import { Router, type Request } from "express"
import multer from "multer"
import { config } from "../config.js"
import { requireAuth, type AuthedRequest } from "../middleware/auth.js"

type AssetType = "video" | "image" | "audio"

type UploadedFile = {
  fieldname: string
  originalname: string
  filename: string
  mimetype: string
  size: number
}

const storage = multer.diskStorage({
  destination: (_req: Request, _file: UploadedFile, cb: (error: Error | null, destination: string) => void) =>
    cb(null, config.uploadDir),
  filename: (_req: Request, file: UploadedFile, cb: (error: Error | null, filename: string) => void) => {
    const timestamp = Date.now()
    const safeName = file.originalname.replace(/[^\w.-]+/g, "_")
    cb(null, `${timestamp}_${safeName}`)
  }
})

const upload = multer({ storage })

const mapType = (fieldname: string): AssetType => {
  if (fieldname === "images") return "image"
  if (fieldname === "audios") return "audio"
  return "video"
}

const validateMime = (type: AssetType, mime?: string | null) => {
  if (!mime) return false
  if (type === "video") return mime.startsWith("video/")
  if (type === "image") return mime.startsWith("image/")
  return mime.startsWith("audio/")
}

const buildUrl = (req: AuthedRequest, filename: string) => {
  const base = `${req.protocol}://${req.get("host")}`
  return `${base}/${config.uploadDir}/${encodeURIComponent(filename)}`
}

export const assetsRouter = Router()

assetsRouter.use(requireAuth)

assetsRouter.post(
  "/upload",
  upload.fields([
    { name: "videos", maxCount: 8 },
    { name: "images", maxCount: 20 },
    { name: "audios", maxCount: 8 }
  ]),
  (req: AuthedRequest, res) => {
    const files = (req as AuthedRequest & { files?: Record<string, UploadedFile[]> }).files
    const assets = {
      videos: (files?.videos || []).map((file) => {
        const type = mapType(file.fieldname)
        const valid = validateMime(type, file.mimetype)
        return {
          url: buildUrl(req, file.filename),
          type,
          source: "upload",
          status: valid ? "validated" : "invalid",
          size: file.size,
          mime: file.mimetype,
          error: valid ? undefined : "mime mismatch"
        }
      }),
      images: (files?.images || []).map((file) => {
        const type = mapType(file.fieldname)
        const valid = validateMime(type, file.mimetype)
        return {
          url: buildUrl(req, file.filename),
          type,
          source: "upload",
          status: valid ? "validated" : "invalid",
          size: file.size,
          mime: file.mimetype,
          error: valid ? undefined : "mime mismatch"
        }
      }),
      audios: (files?.audios || []).map((file) => {
        const type = mapType(file.fieldname)
        const valid = validateMime(type, file.mimetype)
        return {
          url: buildUrl(req, file.filename),
          type,
          source: "upload",
          status: valid ? "validated" : "invalid",
          size: file.size,
          mime: file.mimetype,
          error: valid ? undefined : "mime mismatch"
        }
      })
    }
    res.json({ assets })
  }
)
