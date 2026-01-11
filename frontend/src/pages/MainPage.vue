<script setup lang="ts">
import { useRouter } from "vue-router";
import Button from "@/components/ui/button/Button.vue";

const router = useRouter();

const goLogin = () => {
  router.push("/login");
};
</script>

<template>
  <div class="flex justify-center items-center w-full h-full bg-slate-500">
    <Button @click="goLogin">Login</Button>
  </div>
</template>
