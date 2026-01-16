<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import PlaceBidModal from "@/components/PlaceBidModal/PlaceBidModal.vue";
import MessageModal from "@/components/MessageModal/MessageModal.vue";
import { Button } from "@/components/ui/button";
import { calculateDaysAgo } from "@/utils/date";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ImageIcon, Send } from "lucide-vue-next";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const route = useRoute();
const router = useRouter();

const itemID = Array.isArray(route.params.id) ? route.params.id[0] : route.params.id;
const item = ref<any>(); //NOTE: Add type of item I'm just lazy rn
const itemBidHistory = ref<any>(); //NOTE: Add typpe when I'm not a lazy peice of shit
const itemMessages = ref<any>();
const placeBidModalRef = ref();
const messageModalRef = ref();

const daysAgo = computed(() => {
  if (!item.value?.created_at) return 0;
  return calculateDaysAgo(item.value.created_at);
});

const formattedEndDate = computed(() => {
  if (!item.value?.auction_end_date) return "";
  const endDate = new Date(item.value.auction_end_date);
  return endDate.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
});

const getItemDetails = async () => {
  try {
    const fetchResults = await fetch(`http://localhost:8000/items/${itemID}/`, {
      method: "GET",
    });

    if (!fetchResults.ok) {
      // NOTE: Add proper error message here
    }

    const itemResults = await fetchResults.json();

    item.value = {
      item_image: itemResults.item.item_image ?? undefined,
      title: itemResults.item.title,
      description: itemResults.item.description,
      highest_bid: itemResults.item.highest_bid ?? undefined,
      minimum_bid: itemResults.item.minimum_bid,
      auction_end_date: itemResults.item.auction_end_date,
      created_at: itemResults.item.created_at,
      is_active: itemResults.item.is_active,
    };
  } catch (err) {
    console.error("Error fetching item details:", err);
  }
};

const getItemBids = async () => {
  try {
    const fetchResults = await fetch(
      `http://localhost:8000/items/${itemID}/bids/`,
      {
        method: "GET",
        credentials: "include",
      },
    );

    if (!fetchResults.ok) {
      // NOTE: Add proper error message here when I'm not lazy and stupid
    }

    const bidsResults = await fetchResults.json();

    itemBidHistory.value = bidsResults.bids.map((bid) => ({
      id: bid.id,
      amount: bid.bid_amount,
      timestamp: bid.created_at,
      bidder: bid.bidder.name,
    }));
  } catch (err) {
    console.error("Error fetching item bid details:", err);
  }
};

const getItemMessages = async () => {
  try {
    const fetchResults = await fetch(
      `http://localhost:8000/items/${itemID}/messages/`,
      {
        method: "GET",
        credentials: "include",
      },
    );

    if (!fetchResults.ok) {
      const errorData = await fetchResults.json().catch(() => ({}));
      const errorMessage = errorData.error || `Failed to fetch messages: ${fetchResults.status} ${fetchResults.statusText}`;
      console.error("Error fetching item messages:", errorMessage);
      return;
    }

    const messagesResults = await fetchResults.json();

    if (messagesResults.success) {
      itemMessages.value = messagesResults.messages;
    } else {
      console.error("Error fetching item messages:", messagesResults.error || "Unknown error");
    }
  } catch (err) {
    console.error("Error fetching item messages:", err);
  }
};

const openBidModal = () => {
  if (placeBidModalRef.value) {
    placeBidModalRef.value.isOpen = true;
  }
};

const openMessageModal = () => {
  if (messageModalRef.value) {
    messageModalRef.value.isOpen = true;
  }
};

const handleBidPlaced = async () => {
  await getItemDetails();
  await getItemBids();
};

onMounted(async () => {
  await getItemDetails();
  await getItemBids();
  await getItemMessages();
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-8">
    <div class="space-x-2 w-full max-w-6xl space-y-4">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{{ item?.title || "Item Details" }}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <Card v-if="item" class="overflow-hidden relative">
        <!-- Messages Button -->
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger as-child>
              <button
                class="absolute top-4 right-4 z-10 p-2 hover:bg-muted rounded-md transition-colors"
                @click="openMessageModal"
              >
                <Send class="w-5 h-5" />
              </button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Messages</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <div class="flex flex-col md:flex-row">
          <!-- Item Image -->
          <div
            class="w-full md:w-96 h-[450px] flex-shrink-0 overflow-hidden p-4"
          >
            <img
              v-if="item.item_image"
              :src="item.item_image"
              :alt="item.title"
              class="w-full h-full object-cover rounded-lg"
            />
            <div
              v-else
              class="w-full h-full bg-muted flex flex-col items-center justify-center rounded-lg"
            >
              <ImageIcon class="w-16 h-16 text-muted-foreground mb-2" />
              <span class="text-sm text-muted-foreground">No Image</span>
            </div>
          </div>

          <!-- Item Details -->
          <div class="flex-1 flex flex-col">
            <CardHeader>
              <CardTitle class="text-3xl">{{ item.title }}</CardTitle>
              <CardDescription class="mb-4">
                Listed {{ daysAgo }} {{ daysAgo === 1 ? "day" : "days" }} ago
              </CardDescription>
            </CardHeader>

            <CardContent class="flex-1 flex flex-col space-y-0">
              <div class="space-y-2">
                <!-- Description -->
                <div>
                  <p class="text-sm text-muted-foreground mb-1">Description</p>
                  <p class="text-base">{{ item.description }}</p>
                </div>

                <Separator />

                <!-- Current Highest Bid -->
                <div>
                  <p class="text-sm text-muted-foreground mb-1">
                    Current Highest Bid
                  </p>
                  <p class="text-4xl font-bold">
                    ${{
                      (item.highest_bid ?? item.minimum_bid).toLocaleString()
                    }}
                  </p>
                </div>

                <Separator />

                <!-- Auction End Date -->
                <div>
                  <p class="text-sm text-muted-foreground mb-1">Auction Ends</p>
                  <p class="text-lg font-semibold">{{ formattedEndDate }}</p>
                </div>
              </div>

              <!-- Place Bid Button -->
              <div class="space-y-2 mt-auto">
                <p
                  v-if="!item.is_active"
                  class="text-center text-sm font-semibold text-destructive"
                >
                  Auction has ended
                </p>
                <Button
                  size="lg"
                  class="w-full"
                  :disabled="!item.is_active"
                  @click="openBidModal"
                >
                  Place Bid
                </Button>
              </div>
            </CardContent>
          </div>
        </div>
      </Card>

      <!-- Hidden Modals -->
      <PlaceBidModal
        v-if="item"
        ref="placeBidModalRef"
        :itemID="itemID"
        :item-title="item.title"
        :current-highest-bid="item.highest_bid ?? item.minimum_bid"
        :auction-end-time="item.auction_end_date"
        :bidHistory="itemBidHistory"
        @bid-placed="handleBidPlaced"
      />

      <MessageModal
        v-if="item"
        ref="messageModalRef"
        :item-id="itemID"
        :item-title="item.title"
        :messages="itemMessages"
        @messages-updated="getItemMessages"
      />
    </div>
  </div>
</template>
