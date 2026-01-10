<template>
  <main class="h-full w-full min-w-lvw min-h-lvh bg-zinc-700">
    <RouterView class="bg-zinc-700 h-min-full" />
  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { RouterView } from "vue-router";

export default defineComponent({
  components: { RouterView },
});
</script>
