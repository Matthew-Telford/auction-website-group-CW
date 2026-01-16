<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import ItemSearch from "@/components/ItemSearch/ItemSearch.vue";
import ItemDisplay from "@/components/ItemDisplay/ItemDisplay.vue";
import { Item } from "@/components/ItemSearch/ItemSearch.types";
import { DisplayItem } from "@/components/ItemDisplay/ItemDisplay.types";
import { calculateVisiblePages } from "@/utils/pagination";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const items = ref<DisplayItem[]>();
const totalItems = ref<number>(0);
const pageNumber = ref<number>(1);
const itemsPerPage = 15;

const totalPages = computed(() => {
  return Math.ceil(totalItems.value / itemsPerPage);
});

const paginationData = computed(() => {
  return calculateVisiblePages({
    currentPage: pageNumber.value,
    totalPages: totalPages.value,
  });
});

const visiblePageNumbers = computed(() => paginationData.value.visiblePageNumbers);
const showRightEllipsis = computed(() => paginationData.value.showRightEllipsis);

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
    current_bid: item.highest_bid || item.minimum_bid,
    image: item.item_image,
  }));

  console.log("formatted items:", items.value);
};

onMounted(async () => {
  await handleGetItems();
});
</script>

<template>
  <div class="min-w-svw min-h-svh w-full h-full">
    <div class="pb-6 shadow-sm">
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
            v-for="pageNum in visiblePageNumbers"
            :key="pageNum"
            size="icon-sm"
            :value="pageNum"
            :is-active="pageNum === pageNumber"
          ></PaginationItem>
          <PaginationEllipsis v-if="showRightEllipsis" />
          <PaginationNext />
        </PaginationContent>
      </Pagination>
    </div>
  </div>
</template>
