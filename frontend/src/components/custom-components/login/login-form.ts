import { z } from "zod";

export interface LoginFormInterface {
    email: string;
    password: string;
  }
  
export const LoginForm = z.object({
    email: z
      .string()
      .email({ message: "Invalid email address" })
      .max(40, { message: "Username cannot exceed 20 characters" }),
    password: z
      .string()
      .min(8, { message: "Password must be at least 8 characters long" })
      .regex(/[a-z]/, {
        message: "Password must include a lowercase letter",
      })
      .regex(/[A-Z]/, {
        message: "Password must include an uppercase letter",
      })
      .regex(/\d/, { message: "Password must include at least one number" })
      .regex(/[@$!%*?&#]/, {
        message:
          "Password must include at least one special character (@, $, !, %, *, ?, &, #)",
      }),
  });