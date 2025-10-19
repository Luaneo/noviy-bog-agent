"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { mdxComponent, MdxComponents } from "react-markdown-with-mdx";
import z from "zod";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { CheckCircle2Icon } from "lucide-react";
import { useState } from "react";

function ChangePassword(props: any) {
  return (
    <Dialog>
      <form>
        <DialogTrigger asChild>
          <Button variant="outline" className="mt-4 mb-2 w-full">
            Изменить пароль
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Изменение пароля</DialogTitle>
            <DialogDescription>
              Введите текущий пароль, чтобы установить новый. Предыдущий пароль
              инвалидируется.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-3">
              <Label htmlFor="current-password">Текущий пароль</Label>
              <Input
                id="current-password"
                name="current-password"
                type="password"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="new-password">Новый пароль</Label>
              <Input id="new-password" name="new-password" type="password" />
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Отмена</Button>
            </DialogClose>
            <Button type="submit" disabled>Подтвердить</Button>
          </DialogFooter>
        </DialogContent>
      </form>
    </Dialog>
  );
}

function TechSupport(props: any) {
  const [summoned, setSummoned] = useState<boolean>(false);

  return summoned ? (
    <Alert className="w-full mt-4 mb-2">
      <CheckCircle2Icon />
      <AlertTitle>Поддержка уже в пути</AlertTitle>
      <AlertDescription>Среднее время ответа – 5 минут.</AlertDescription>
    </Alert>
  ) : (
    <Button
      variant="outline"
      className="mt-4 mb-2 w-full"
      onClick={() => {
        setTimeout(() => setSummoned(true), 200)
      }}
    >
      Вызвать оператора
    </Button>
  );
}

const mdxComponents: MdxComponents = {
  ChangePassword: mdxComponent(ChangePassword, z.object({})),
  TechSupport: mdxComponent(TechSupport, z.object({})),
};

export default mdxComponents;
