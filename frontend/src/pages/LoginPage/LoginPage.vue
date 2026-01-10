<script setup lang="ts">
import { getCSRFToken } from "@/utils/csrf";
import { useRouter } from "vue-router";
import { ref, onMounted } from "vue";
import LoginModal from "@/components/LoginModal/LoginModal.vue";

let csrfToken: string | null;
const user = ref<any>();
const router = useRouter();

const email = ref<string>();
const password = ref<string>();

const login = async (email: string, password: string): Promise<JSON> => {
  if (!csrfToken) {
    throw Error("No CSRF Token");
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
  } catch (err) {
    console.error("Error while logging in:", err);
  }
};

const handleGoToSignup = () => {
  router.push("/signup");
};

onMounted(() => {
  csrfToken = getCSRFToken();
});
</script>

<template>
  <div class="min-w-lvw min-h-lvh flex items-center justify-center">
    <LoginModal
      @loginPressed="
        (email, password) => {
          handleLogin(email, password);
        }
      "
      @signupPressed="handleGoToSignup"
    ></LoginModal>
  </div>
</template>
