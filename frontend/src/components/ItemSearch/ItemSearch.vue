<script setup lang="ts">
import { useRouter } from "vue-router";
import { ref } from "vue";
import { SearchItem, SearchItems, Item } from "./ItemSearch.types";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import { Button } from "../ui/button";
import { ShoppingCart, CornerDownLeft } from "lucide-vue-next";

const router = useRouter();

const items = ref<SearchItems>();
const searchString = ref<string | undefined>(undefined);
const inputFocused = ref<boolean>(false);

const handleSearch = async () => {
  try {
    const fetchResults = await fetch(
      `http://localhost:8000/items/?search=${searchString.value}&start=0&end=5`,
      {
        method: "GET",
      },
    );

    console.log("Raw fetch results:", fetchResults);

    const itemResults = await fetchResults.json();

    console.log("Item results:", itemResults);

    if (!itemResults.success) {
      throw Error(itemResults.status);
    }

    items.value = itemResults.items.map((item: Item) => ({
      id: item.id,
      title: item.title,
    }));

    console.log("Formatted items:", items.value);
  } catch (err) {
    console.error(`Error searching for "/${searchString.value}"/:`, err);
  }
};

const handleSearchEnter = () => {};

const handleItemClick = (itemID: string) => {
  console.log("Clicked item ID:", itemID); // NOTE: Remove once Item page is created and add proper redirect
  //router.push()
};
</script>

<template>
  <Command class="flex rounded-lg border shadow-md" :disable-filter="true">
    <CommandInput
      v-model="searchString"
      placeholder="Search"
      @update:modelValue="handleSearch"
      @keydown.enter="handleSearchEnter"
      @focus="inputFocused = true"
      @blur="inputFocused = false"
    />
    <CommandList v-if="inputFocused && searchString">
      <CommandEmpty v-if="!items?.length">
        No Items Matching Your Search
      </CommandEmpty>
      <CommandGroup v-else heading="Results">
        <CommandItem
          v-for="item in items"
          :key="item.id"
          :value="item.title"
          @mousedown.prevent
          @select="handleItemClick(item.id)"
          class="hover:bg-accent hover:text-accent-foreground"
        >
          <div class="flex items-center justify-between w-full">
            <span class="text-left">{{ item.title }}</span>
            <div class="bg-muted/60 rounded p-1 ml-2">
              <CornerDownLeft class="w-3 h-3 text-muted-foreground" />
            </div>
          </div>
        </CommandItem>
      </CommandGroup>
    </CommandList>
  </Command>
</template>
