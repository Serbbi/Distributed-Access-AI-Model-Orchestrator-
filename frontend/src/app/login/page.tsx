"use client";

import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  LoginForm,
  LoginFormInterface,
} from "@/components/custom-components/login/login-form";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { backendUrl } from "@/config";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/custom-components/auth/auth-provider/auth-provider";

export default function Login() {
  const [kratosFlowId, setKratosFlowId] = useState("");
  const [csrfToken, setCSRFToken] = useState("");
  const router = useRouter();
  const { checkSessionToken } = useAuth();

  useEffect(() => {
    async function loginWithKratos() {
      if (kratosFlowId) return;
      try {
        const response = await fetch(
          `${backendUrl()}/self-service/login/browser`,
          {
            credentials: "include",
            headers: { Accept: "application/json" },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setKratosFlowId(data.id);
        const csrfNode = data.ui.nodes.find(
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (node: any) => node.attributes.name === "csrf_token"
        );
        if (csrfNode) {
          setCSRFToken(csrfNode.attributes.value);
        }
      } catch (error) {
        console.error("Error fetching Kratos flow:", error);
      }
    }
    loginWithKratos();
  }, [kratosFlowId]);

  const loginForm = useForm<LoginFormInterface>({
    defaultValues: { email: "", password: "" },
    resolver: zodResolver(LoginForm),
    mode: "onChange",
  });

  const { register, handleSubmit } = loginForm;

  async function login() {
    try {
      const response = await fetch(
        `${backendUrl()}/self-service/login?flow=${kratosFlowId}`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken,
          },
          body: JSON.stringify({
            method: "password",
            password_identifier: loginForm.getValues("email"),
            password: loginForm.getValues("password"),
            csrf_token: csrfToken,
          }),
        }
      );

      if (!response.ok) {
        console.log("Failed to login", response);
      } else {
        if (checkSessionToken) {
          await checkSessionToken();
        }
        router.push("/");
      }
    } catch (error) {
      console.error("Failed to login", error);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      <section className="flex flex-col items-center justify-start w-1/3 h-fit bg-gray-200 rounded-[6px]">
        <h1 className="text-2xl font-semibold w-full p-4 bg-gray-300 rounded-t-[6px]">
          Login
        </h1>
        <div className="flex flex-col gap-2 w-4/5 h-full justify-center p-3">
          <div className="flex flex-col gap-2 h-full justify-center p-5 m-1 rounded-[6px] outline outline-gray-400 text-gray-600">
            To login into Aerrus Cloud please enter your email and password.
          </div>
          <form onSubmit={handleSubmit(login)}>
            <div className="flex flex-row items-center justify-center gap-4">
              <Input
                className="h-8"
                placeholder="Email"
                {...register("email")}
              />
            </div>
            <div className="flex flex-row items-center justify-center gap-4">
              <Input
                className="h-8"
                placeholder="Password"
                type="password"
                {...register("password")}
              />
            </div>
            <Button className="mt-10" type="submit">
              Login
            </Button>
          </form>
        </div>
      </section>
    </div>
  );
}
