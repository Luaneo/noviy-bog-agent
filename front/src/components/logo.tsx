"use client";

import { useState, useEffect } from "react";
import { useTheme } from "next-themes";
import Image from "next/image";
import darkLogo from "@/../public/logo-dark.svg";
import lightLogo from "@/../public/logo-light.svg";

export default function Logo() {
  const [mounted, setMounted] = useState(false);
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <Image
      src={resolvedTheme === "light" ? lightLogo : darkLogo}
      height={32}
      alt="Техподдержка РОСАТОМ"
    />
  );
}
