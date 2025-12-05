"use server";

import { revalidatePath } from "next/cache";

let tasks: Array<{ title: string; description: string }> = [];

export async function addTask(formData: FormData) {
  const title = formData.get("title") as string;
  const description = formData.get("description") as string;

  tasks.push({ title, description });
  revalidatePath("/");
}

export async function getTasks() {
  return tasks;
}
