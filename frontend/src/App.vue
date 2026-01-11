<template>
  <Toaster position="top-center" />
  <main class="h-full w-full min-w-lvw min-h-lvh bg-zinc-700">
    <RouterView class="bg-zinc-700 h-min-full" />
  </main>
</template>

<script setup lang="ts">
import "vue-sonner/style.css";
import { Toaster } from "@/components/ui/sonner";
import { onMounted } from "vue";
import { RouterView } from "vue-router";

onMounted(async () => {
  // Fetch CSRF token on app mount
  await fetch("http://localhost:8000/", {
    credentials: "include",
  });
  console.log("CSRF cookie initialized");
});
</script>
