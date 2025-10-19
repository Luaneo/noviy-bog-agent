"use client";

import Logo from "@/components/logo";
import MyMarkdown from "@/components/my-markdown";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupTextarea,
} from "@/components/ui/input-group";
import { Spinner } from "@/components/ui/spinner";
import { ArrowUpIcon, ThumbsDown, ThumbsUp } from "lucide-react";
import { useRef, useState } from "react";
import { twMerge } from "tailwind-merge";

export default function Home() {
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const sendMessageRef = useRef<HTMLButtonElement>(null);
  const [status, setStatus] = useState<"idle" | "pending" | "streaming">(
    "idle"
  );
  const [messages, setMessages] = useState<
    Array<{
      by: "user" | "agent";
      message: string;
      liked?: boolean;
    }>
  >([
    {
      by: "user",
      message: "Что ты умеешь?",
    },
    {
      by: "agent",
      message:
        "# Привет!\nЯ — агент техподдержки.\n\nОпишите проблему и я помогу:\n- С доступом\n- С настройками ПО\n- С диагностикой ошибок\n- С поиском инструкций\n<TechSupport />",
    },
  ]);
  const [streamingMessage, setStreamingMessage] = useState<string | null>(null);

  const sendQuestion = async () => {
    if (!textAreaRef.current) {
      return;
    }
    const question = textAreaRef.current.value;
    setMessages([
      ...messages,
      {
        by: "user",
        message: question,
      },
    ]);
    textAreaRef.current.value = "";

    setStatus("pending");
    const response = await fetch(`http://localhost:8000/question/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        [
          ...messages,
          {
            by: "user",
            message: question,
          },
        ].slice(2)
      ),
    });
    if (!response.ok) {
      setMessages([
        ...messages,
        {
          by: "user",
          message: question,
        },
        {
          by: "agent",
          message: "*Ошибка на сервере, немного подождите и повторите вопрос.*",
        },
      ]);
      setStatus("idle");
      return;
    }

    if (!response.body) {
      throw "Response from /question/stream does not have a body";
    }
    setStatus("streaming");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let curMessage = "";
    setStreamingMessage(curMessage);
    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        console.log("done");
        break;
      }
      const chunk = decoder.decode(value, { stream: true });
      curMessage += chunk;
      setStreamingMessage(curMessage);
    }
    reader.releaseLock();

    setStatus("idle");
    setMessages([
      ...messages,
      {
        by: "user",
        message: question,
      },
      {
        by: "agent",
        message: curMessage.slice(0, curMessage.length - 14),
      },
    ]);
    setStreamingMessage(null);
  };

  return (
    <div className="p-5 flex flex-col items-center min-h-[100vh] mb-44">
      <div className="flex justify-between max-w-2xl w-[calc(100%-40px)] py-5 fixed top-0 bg-background">
        <div>
          <Logo />
        </div>
        <ThemeToggle />
      </div>
      <div className="flex flex-col gap-2 max-w-2xl w-full mt-15">
        {messages.map((message, index) => (
          <div key={index} className="flex w-full">
            {message.by === "agent" ? (
              <>
                <div className="max-w-[80%] bg-card py-3 px-5 rounded-2xl border-2 border-border rounded-bl-none leading-7 shadow-primary/10 shadow-lg">
                  <MyMarkdown>{message.message}</MyMarkdown>
                </div>
                <div className="flex items-end pl-2 gap-2">
                  <Button
                    variant={message.liked === true ? "outline" : "ghost"}
                    onClick={() => {
                      if (message.liked === true) {
                        message.liked = undefined;
                      } else {
                        message.liked = true;
                      }
                      setMessages([...messages]);
                    }}
                  >
                    <ThumbsUp />
                  </Button>
                  <Button
                    variant={message.liked === false ? "outline" : "ghost"}
                    onClick={() => {
                      if (message.liked === false) {
                        message.liked = undefined;
                      } else {
                        message.liked = false;
                      }
                      setMessages([...messages]);
                    }}
                  >
                    <ThumbsDown />
                  </Button>
                </div>
                <div className="flex-1" /> {/* spacer */}
              </>
            ) : (
              <>
                <div className="flex-1" /> {/* spacer */}
                <div className="max-w-[80%] bg-secondary py-3 px-5 rounded-2xl border-2 border-border rounded-br-none leading-7 shadow-primary/10 shadow-lg">
                  <MyMarkdown>{message.message}</MyMarkdown>
                </div>
              </>
            )}
          </div>
        ))}
        {status === "pending" ||
          (status === "streaming" && streamingMessage === "" && (
            <div className="flex w-full">
              <div className="max-w-[80%] bg-card py-3 px-5 rounded-2xl border-2 border-border rounded-bl-none leading-7 shadow-primary/10 shadow-lg">
                <Spinner />
              </div>
              <div className="flex-1" /> {/* spacer */}
            </div>
          ))}
        {status === "streaming" && streamingMessage && (
          <div className="flex w-full">
            <div className="max-w-[80%] bg-card py-3 px-5 rounded-2xl border-2 border-border rounded-bl-none leading-7 shadow-primary/10 shadow-lg">
              <MyMarkdown>{streamingMessage}</MyMarkdown>
            </div>
            <div className="flex-1" /> {/* spacer */}
          </div>
        )}
      </div>

      <div className="max-w-2xl w-[calc(100%-40px)] fixed bottom-5">
        <InputGroup className="!bg-card shadow-primary/25 shadow-md">
          <InputGroupTextarea
            placeholder="Вопрос агенту техподдержки"
            ref={textAreaRef}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && status === "idle") {
                e.preventDefault();
                sendMessageRef.current?.click();
              }
            }}
          />
          <InputGroupAddon align="inline-end">
            <InputGroupButton
              variant={status === "idle" ? "default" : "ghost"}
              className={twMerge(
                "rounded-full mr-2",
                status === "idle" ? "cursor-pointer" : "cursor-wait"
              )}
              size="icon-xs"
              onClick={status === "idle" ? sendQuestion : () => {}}
              ref={sendMessageRef}
            >
              <ArrowUpIcon />
              <span className="sr-only">Отправить</span>
            </InputGroupButton>
          </InputGroupAddon>
        </InputGroup>
      </div>
    </div>
  );
}
