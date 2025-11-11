"use client";

import { FieldStatusBox } from "@/components/custom-components/field-status-box";
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

export default function Register() {
  const [kratosFlowId, setKratosFlowId] = useState("");
  const [csrfToken, setCSRFToken] = useState("");

  const loginForm = useForm<LoginFormInterface>({
    defaultValues: { email: "", password: "" },
    resolver: zodResolver(LoginForm),
    mode: "onChange",
  });

  
  useEffect(() => {
    async function registerWithKratos() {
      if (kratosFlowId) return;
      try {
        const response = await fetch(
          `${backendUrl()}/self-service/registration/browser`,
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
    registerWithKratos();
  }, [kratosFlowId]);

  const {
    register,
    handleSubmit,
    formState: { errors, dirtyFields },
  } = loginForm;

  async function registerUser() {
    try {
      const response = await fetch(
        `${backendUrl()}/self-service/registration?flow=${kratosFlowId}`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken,
          },
          body: JSON.stringify({
            method: "password",
            csrf_token: csrfToken,
            password: loginForm.getValues("password"),
            traits: {
              email: loginForm.getValues("email"),
            },
          }),
        }
      );

      if (!response.ok) {
        console.log("Failed to register", response);
      }
    } catch (error) {
      console.error("Failed to register", error);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      <section className="flex flex-col items-center justify-start w-1/3 h-fit bg-gray-200 rounded-[6px]">
        <h1 className="text-2xl font-semibold w-full p-4 bg-gray-300 rounded-t-[6px]">
          Register
        </h1>
        <form className="flex flex-col gap-2 w-4/5 h-full justify-center p-3" {...loginForm} onSubmit={handleSubmit(registerUser)}>
          <div className="flex flex-col gap-2 h-full justify-center p-5 m-1 rounded-[6px] outline outline-gray-400 text-gray-600">
            Welcome to Aerrus Cloud! To access the features of the application
            please create an account.
          </div>
          <div className="flex flex-row items-center justify-center gap-4">
            <Input
              className="h-8"
              placeholder="Email"
              {...register("email")}
              autoComplete="off"
            />
            <FieldStatusBox
              status={
                dirtyFields.email
                  ? errors.email
                    ? "error"
                    : "success"
                  : "info"
              }
              message={
                dirtyFields.email
                  ? errors.email
                    ? errors.email.message
                    : "You have entered a valid email!"
                  : "Please enter an email."
              }
            />
          </div>
          <div className="flex flex-row items-center justify-center gap-4">
            <Input
              className="h-8"
              placeholder="Password"
              type="password"
              {...register("password")}
            />
            <FieldStatusBox
              status={
                dirtyFields.password
                  ? errors.password
                    ? "error"
                    : "success"
                  : "info"
              }
              message={
                dirtyFields.password
                  ? errors.password
                    ? errors.password.message
                    : "You have entered a valid password!"
                  : "Please enter a password."
              }
            />
          </div>
          <Button className="mt-10" type='submit'> Submit </Button>
        </form>
      </section>
    </div>
  );
}
