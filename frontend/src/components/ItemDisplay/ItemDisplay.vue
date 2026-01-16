<script setup lang="ts">
import ItemCard from "./components/ItemCard.vue";
import { DisplayItem } from "./ItemDisplay.types";

defineProps<{
  items: DisplayItem[];
}>();
</script>

<template>
  <div class="py-6 px-4">
    <div
      class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 auto-rows-max"
    >
      <ItemCard v-for="item in items" :key="item.id" :item="item" />
    </div>
  </div>
</template>
