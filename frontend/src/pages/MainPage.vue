<script setup lang="ts">
import { useRouter } from "vue-router";
import { onMounted, ref, computed } from "vue";
import Button from "@/components/ui/button/Button.vue";
import ItemSearch from "@/components/ItemSearch/ItemSearch.vue";
import { User } from "lucide-vue-next";
import ItemDisplay from "@/components/ItemDisplay/ItemDisplay.vue";
import { Item } from "@/components/ItemSearch/ItemSearch.types";
import { DisplayItem } from "@/components/ItemDisplay/ItemDisplay.types";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const router = useRouter();
const isLoggedIn = ref(false);

const items = ref<DisplayItem[]>();
const totalItems = ref<number>(0);
const pageNumber = ref<number>(1);
const itemsPerPage = 15;

const totalPages = computed(() => {
  return Math.ceil(totalItems.value / itemsPerPage);
});

const handleGetItems = async () => {
  const start = (pageNumber.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;

  const fetchResults = await fetch(
    `http://localhost:8000/items/?start=${start}&end=${end}`,
    {
      method: "GET",
    },
  );

  console.log("Raw fetch results:", fetchResults);

  const itemResults = await fetchResults.json();

  console.log("item results:", itemResults);

  if (!itemResults.success) {
    throw Error(itemResults.status);
  }

  totalItems.value = itemResults.total_count;
  console.log("Total items count:", totalItems.value);

  items.value = itemResults.items.map((item: Item) => ({
    id: item.id,
    title: item.title,
    description: item.description,
    auction_end_date: item.auction_end_date,
    minimum_bid: item.minimum_bid,
    current_bid: item.current_bid,
  }));

  console.log("formatted items:", items.value);
};

const goLogin = () => {
  router.push("/login");
};

const goSignup = () => {
  router.push("/signup");
};

onMounted(async () => {
  await handleGetItems();
});
</script>

<template>
  <div class="min-w-svw min-h-svh w-full h-full">
    <div class="pb-6 shadow-sm">
      <div class="fixed top-6 right-5 z-50 flex gap-3">
        <template v-if="!isLoggedIn">
          <Button class="h-8" @click="goLogin">Login</Button>
          <Button class="h-8" @click="goSignup">Signup</Button>
        </template>
        <template v-else>
          <Button class="flex items-center gap-2 h-8">
            <User class="size-4" />
            <span>Profile</span>
          </Button>
        </template>
      </div>

      <div class="flex justify-center pt-6">
        <div
          class="relative w-96 [&_[data-slot=command-input-wrapper]]:h-8 [&_[data-slot=command-input]]:h-8 [&_[data-slot=command-input]]:py-1 [&_[data-slot=command-list]]:absolute [&_[data-slot=command-list]]:top-full [&_[data-slot=command-list]]:left-0 [&_[data-slot=command-list]]:right-0 [&_[data-slot=command-list]]:mt-1 [&_[data-slot=command-list]]:z-50 [&_[data-slot=command-list]]:rounded-lg [&_[data-slot=command-list]]:border [&_[data-slot=command-list]]:shadow-lg [&_[data-slot=command-list]]:bg-popover [&_[data-slot=command-list]]:max-h-[300px] [&_[data-slot=command-list]]:overflow-y-auto"
        >
          <ItemSearch />
        </div>
      </div>
    </div>

    <div class="mt-4 pb-20">
      <ItemDisplay :items="items" />
    </div>

    <div class="fixed bottom-0 left-0 right-0 py-4 flex justify-center">
      <Pagination
        v-slot="{ page }"
        v-model:page="pageNumber"
        :items-per-page="itemsPerPage"
        :total="totalItems"
        @update:page="handleGetItems"
      >
        <PaginationContent>
          <PaginationPrevious />
          <PaginationItem
            v-for="pageNum in totalPages"
            :key="pageNum"
            size="icon-sm"
            :value="pageNum"
            :is-active="pageNum === pageNumber"
          ></PaginationItem>
          <PaginationEllipsis v-if="totalPages > 3" :index="3" />
          <PaginationNext />
        </PaginationContent>
      </Pagination>
    </div>
  </div>
</template>
