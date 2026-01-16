<script setup lang="ts">
import "vue-sonner/style.css";
import MainLogo from "./assets/Asset1.svg";
import { Toaster } from "@/components/ui/sonner";
import { onMounted, computed } from "vue";
import { RouterView, useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/userStore";
import { Button } from "@/components/ui/button";
import { User } from "lucide-vue-next";

const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

const showAuthButtons = computed(() => {
  const currentPath = route.path;
  return currentPath !== "/login" && currentPath !== "/signup";
});

const goLogin = () => {
  const currentPath = route.fullPath;
  router.push({ path: "/login", query: { redirect: currentPath } });
};

const goSignup = () => {
  const currentPath = route.fullPath;
  router.push({ path: "/signup", query: { redirect: currentPath } });
};

const goHome = () => {
  router.push("/");
};

onMounted(async () => {
  // Fetch CSRF token on app mount
  await fetch("http://localhost:8000/", {
    credentials: "include",
  });

  // Check if user is already logged in
  await userStore.fetchUserProfile();
});
</script>

<template>
  <Toaster position="top-center" class="z-[100]" />
  <button
    @click="goHome"
    class="fixed top-6 left-5 z-50 w-1/8 cursor-pointer hover:opacity-80 transition-opacity"
  >
    <MainLogo class="w-full" />
  </button>

  <!-- Persistent Auth/Profile Buttons -->
  <div v-if="showAuthButtons" class="fixed top-6 right-5 z-50 flex gap-3">
    <template v-if="!userStore.isLoggedIn">
      <Button variant="outline" class="h-8 shadow-sm" @click="goLogin"
        >Login</Button
      >
      <Button variant="outline" class="h-8 shadow-sm" @click="goSignup"
        >Signup</Button
      >
    </template>
    <template v-else>
      <button
        class="flex items-center gap-2 h-8 pl-3 pr-2 hover:opacity-80 transition-opacity"
      >
        <span class="text-sm font-medium">Profile</span>
        <div
          class="w-6 h-6 rounded-full overflow-hidden flex-shrink-0 bg-muted"
        >
          <img
            v-if="userStore.user.value?.profile_picture"
            :src="userStore.user.value?.profile_picture"
            :alt="`${userStore.user.value?.first_name} ${userStore.user.value?.last_name}`"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <User class="w-4 h-4 text-muted-foreground" />
          </div>
        </div>
      </button>
    </template>
  </div>

  <main class="h-full w-full min-w-lvw min-h-lvh bg-zinc-100">
    <RouterView class="bg-zinc-100 h-min-full" />
  </main>
</template>
