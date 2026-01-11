<script setup lang="ts">
import "vue-sonner/style.css";
import MainLogo from "./assets/Asset1.svg";
import { Toaster } from "@/components/ui/sonner";
import { onMounted } from "vue";
import { RouterView } from "vue-router";

onMounted(async () => {
  // Fetch CSRF token on app mount
  await fetch("http://localhost:8000/", {
    credentials: "include",
  });
});
</script>

<template>
  <Toaster position="top-center" />
  <MainLogo class="fixed top-6 left-5 z-50 w-1/8" />
  <main class="h-full w-full min-w-lvw min-h-lvh bg-zinc-700">
    <RouterView class="bg-zinc-700 h-min-full" />
  </main>
</template>
