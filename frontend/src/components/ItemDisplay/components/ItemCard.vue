<script setup lang="ts">
import { Card, CardContent } from "@/components/ui/card";
import { DisplayItem } from "../ItemDisplay.types";
import { ImageIcon } from "lucide-vue-next";
import { useRouter } from "vue-router";

const props = defineProps<{
  item: DisplayItem;
}>();

const router = useRouter();

const handleCardClick = () => {
  router.push(`itemDetailsPage/${props.item.id}`);
};
</script>

<template>
  <Card
    class="overflow-hidden h-[200px] flex flex-col cursor-pointer hover:shadow-lg transition-shadow"
    @click="handleCardClick"
  >
    <CardContent class="p-3 flex flex-col h-full">
      <div class="flex gap-3 h-[100px]">
        <div class="flex-shrink-0">
          <img
            v-if="props.item.image"
            :src="props.item.image"
            :alt="props.item.title"
            class="w-24 h-24 object-cover rounded-lg"
          />
          <div
            v-else
            class="w-24 h-24 bg-muted rounded-lg flex items-center justify-center"
          >
            <ImageIcon class="w-8 h-8 text-muted-foreground" />
          </div>
        </div>

        <div class="flex-1 min-w-0 flex flex-col">
          <h3 class="text-sm font-semibold mb-3 line-clamp-2">
            {{ props.item.title }}
          </h3>

          <div class="space-y-0.5 mt-auto">
            <div class="flex items-center gap-1.5">
              <span class="text-[10px] text-muted-foreground"
                >Minimum Bid:</span
              >
              <span class="text-xs font-medium"
                >${{ props.item.minimum_bid }}</span
              >
            </div>

            <div class="flex items-center gap-1.5">
              <span class="text-[10px] text-muted-foreground"
                >Current Bid:</span
              >
              <span class="text-xs font-medium"
                >${{ props.item.current_bid || props.item.minimum_bid }}</span
              >
            </div>

            <div class="flex items-center gap-1.5">
              <span class="text-[10px] text-muted-foreground"
                >Auction Ends:</span
              >
              <span class="text-xs font-medium">{{
                props.item.auction_end_date
              }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-2">
        <p class="text-xs text-muted-foreground line-clamp-2 leading-normal">
          {{ props.item.description }}
        </p>
      </div>
    </CardContent>
  </Card>
</template>
