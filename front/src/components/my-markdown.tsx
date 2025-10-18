import * as React from "react";
import Markdown from "react-markdown";
import { Separator } from "./ui/separator";

export default function MyMarkdown(
  props: React.ComponentProps<typeof Markdown>
) {
  return (
    <Markdown
      components={{
        h1({ className, ...props }) {
          return (
            <h1
              className={
                "scroll-m-20 text-2xl font-extrabold tracking-tight " +
                className
              }
              {...props}
            />
          );
        },
        h2({ className, ...props }) {
          return (
            <h2
              className={
                "scroll-m-20 text-2xl font-bold tracking-tight " + className
              }
              {...props}
            />
          );
        },
        h3({ className, ...props }) {
          return (
            <h3
              className={
                "scroll-m-20 text-2xl font-semibold tracking-tight " + className
              }
              {...props}
            />
          );
        },
        h4({ className, ...props }) {
          return (
            <h4
              className={
                "scroll-m-20 text-xl font-semibold tracking-tight " + className
              }
              {...props}
            />
          );
        },
        p({ className, ...props }) {
          return (
            <p
              className={"leading-7 [&:not(:first-child)]:mt-6 " + className}
              {...props}
            />
          );
        },
        ul({ className, ...props }) {
          return (
            <ul
              className={
                "my-3 [&:last-child]:mb-0 ml-6 list-disc [&>li]:mt-2 " +
                className
              }
              {...props}
            />
          );
        },
        ol({ className, ...props }) {
          return (
            <ol
              className={
                "my-3 [&:last-child]:mb-0 ml-6 list-decimal [&>li]:mt-2 " +
                className
              }
              {...props}
            />
          );
        },
        blockquote({ className, ...props }) {
          return (
            <blockquote
              className={"mt-6 border-l-2 pl-6 italic " + className}
              {...props}
            />
          );
        },
        code({ className, ...props }) {
          return (
            <code
              className={
                "bg-muted relative rounded px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold " +
                className
              }
              {...props}
            />
          );
        },
        hr({ className, ...props }) {
          return <Separator className={className} {...props} />;
        },
      }}
      {...props}
    />
  );
}
