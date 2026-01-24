import mongoose, { Schema } from "mongoose"

export type UserDocument = {
  email: string
  name: string
  passwordHash: string
  createdAt: Date
  updatedAt: Date
}

const UserSchema = new Schema<UserDocument>(
  {
    email: { type: String, required: true, unique: true, lowercase: true, index: true },
    name: { type: String, required: true },
    passwordHash: { type: String, required: true }
  },
  { timestamps: true }
)

export const User = mongoose.model<UserDocument>("User", UserSchema)
