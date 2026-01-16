<script setup lang="ts">
import { getCSRFToken } from "@/utils/csrf";
import { useRouter } from "vue-router";
import { ref } from "vue";
import { toast } from "vue-sonner";
import LoginModal from "@/components/LoginModal/LoginModal.vue";
import { useUserStore } from "@/stores/userStore";

const user = ref<any>();
const router = useRouter();
const userStore = useUserStore();

const login = async (email: string, password: string): Promise<JSON> => {
  const csrfToken = getCSRFToken();

  if (!csrfToken) {
    throw Error("No CSRF Token - make sure cookies are enabled");
  }

  const response = await fetch("http://localhost:8000/login/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    credentials: "include", // Important: sends cookies
    body: JSON.stringify({ email, password }),
  });

  return response.json();
};

const handleLogin = async (email: string, password: string) => {
  try {
    user.value = await login(email, password);

    if (user.value.error) {
      openErrorPopup();
    } else if (user.value.success) {
      console.log("Login successful:", user.value);
      
      // Save user data to store
      userStore.setUser(user.value.user);
      
      toast("Success", {
        description: "Login successful! Redirecting...",
      });
      
      const redirectTo = (router.currentRoute.value.query.redirect as string) || "/";
      setTimeout(() => {
        router.push(redirectTo);
      }, 1500);
    }
  } catch (err) {
    console.error("Error while logging in:", err);
  }
};

const openErrorPopup = () => {
  toast("Error", {
    description: "Invalid email or password",
    action: {
      label: "Close",
      onClick: () => console.log("close"),
    },
  });
};
</script>

<template>
  <div class="min-w-lvw min-h-lvh flex items-center justify-center">
    <LoginModal
      @loginPressed="
        (email, password) => {
          handleLogin(email, password);
        }
      "
    ></LoginModal>
  </div>
</template>
