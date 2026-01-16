<script setup lang="ts">
import { ref, watch, onUnmounted } from "vue";
import { toast } from "vue-sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getCSRFToken } from "@/utils/csrf";

interface Bid {
  id: number;
  amount: number;
  bidder: string;
  timestamp: string;
}

const props = defineProps<{
  itemID: string;
  itemTitle: string;
  currentHighestBid: number;
  auctionEndTime: string;
  bidHistory?: Bid[];
}>();

const emit = defineEmits<{
  bidPlaced: [];
}>();

const userBid = ref<number>();
const isOpen = ref(false);
const countdown = ref({
  days: 0,
  hours: 0,
  minutes: 0,
  seconds: 0,
});

let countdownInterval: number | null = null;

const calculateCountdown = () => {
  const now = new Date().getTime();
  const endTime = new Date(props.auctionEndTime).getTime();
  const timeRemaining = endTime - now;

  if (timeRemaining <= 0) {
    countdown.value = { days: 0, hours: 0, minutes: 0, seconds: 0 };
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
    return;
  }

  const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
  const hours = Math.floor(
    (timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
  );
  const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

  countdown.value = { days, hours, minutes, seconds };
};

const startCountdown = () => {
  calculateCountdown();
  countdownInterval = window.setInterval(calculateCountdown, 1000);
};

const stopCountdown = () => {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
};

watch(isOpen, (newValue) => {
  if (newValue) {
    startCountdown();
  } else {
    stopCountdown();
  }
});

onUnmounted(() => {
  stopCountdown();
});

const formatTime = (num: number) => String(num).padStart(2, "0");

const handleCloseModal = () => {
  userBid.value = undefined;
  isOpen.value = false;
};

const handlePlaceBid = async () => {
  if (!userBid.value) {
    toast.error("Must enter a bid amount", {
      action: {
        label: "Close",
        onClick: () => {},
      },
    });
    return;
  }

  const minimumRequiredBid = props.currentHighestBid + 1;
  if (userBid.value < minimumRequiredBid) {
    toast.error(`Bid must be at least $${minimumRequiredBid.toLocaleString()}`, {
      action: {
        label: "Close",
        onClick: () => {},
      },
    });
    return;
  }

  const csrfToken = getCSRFToken();

  try {
    const fetchResults = await fetch("http://localhost:8000/bids/create/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken ?? "",
      },
      credentials: "include",
      body: JSON.stringify({
        item_id: props.itemID,
        bid_amount: userBid.value,
      }),
    });

    if (!fetchResults.ok) {
      // NOTE: Add proper error when I'm not lazy as fuck
    }

    const bidResult = await fetchResults.json();

    if (bidResult.success) {
      toast.success("Bid placed successfully!", {
        action: {
          label: "Close",
          onClick: () => {},
        },
      });
      emit("bidPlaced");
      isOpen.value = false;
    } else {
      toast.error(bidResult.error || "Failed to place bid", {
        action: {
          label: "Close",
          onClick: () => {},
        },
      });
    }
  } catch (err) {
    console.error("Error placing bid:", err);
  }
};

defineExpose({
  isOpen,
});
</script>

<template>
  <Dialog v-model:open="isOpen" @update:open="(open) => { if (!open) userBid = undefined; }">
    <DialogTrigger as-child>
      <slot />
    </DialogTrigger>
    <DialogContent class="sm:max-w-[600px]">
      <DialogHeader>
        <DialogTitle>{{ props.itemTitle }}</DialogTitle>
        <DialogDescription>Place your bid for this item</DialogDescription>
      </DialogHeader>

      <div class="space-y-6 py-4">
        <!-- Countdown Timer -->
        <div>
          <Label class="text-sm text-muted-foreground">Auction Ends In</Label>
          <div class="text-3xl font-bold text-primary mt-2">
            {{ formatTime(countdown.days) }}:{{
              formatTime(countdown.hours)
            }}:{{ formatTime(countdown.minutes) }}:{{
              formatTime(countdown.seconds)
            }}
          </div>
          <p class="text-xs text-muted-foreground mt-1">
            Days : Hours : Minutes : Seconds
          </p>
        </div>

        <Separator />

        <!-- Bidding Section -->
        <div class="grid grid-cols-2 gap-6">
          <!-- Current Highest Bid -->
          <div class="space-y-2">
            <Label class="text-sm text-muted-foreground"
              >Current Highest Bid</Label
            >
            <div
              class="flex flex-col items-center justify-center h-24 bg-muted rounded-lg"
            >
              <span class="text-4xl font-bold"
                >${{ props.currentHighestBid.toLocaleString() }}</span
              >
            </div>
          </div>

          <!-- Your Bid Input -->
          <div class="space-y-2">
            <Label for="bid-amount">Your Bid</Label>
            <div class="flex flex-col gap-2">
              <div
                class="relative flex items-center h-24 bg-muted rounded-lg px-4"
              >
                <span class="text-3xl font-semibold text-muted-foreground mr-2"
                  >$</span
                >
                <Input
                  id="bid-amount"
                  v-model="userBid"
                  type="number"
                  placeholder="Enter amount"
                  class="border-0 bg-transparent text-3xl font-semibold h-full focus-visible:ring-0 focus-visible:ring-offset-0 p-0"
                  :min="props.currentHighestBid + 1"
                />
              </div>
              <p class="text-xs text-muted-foreground">
                Minimum bid: ${{
                  (props.currentHighestBid + 1).toLocaleString()
                }}
              </p>
            </div>
          </div>
        </div>

        <Separator />

        <!-- Live Bids Section -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <Label class="text-sm font-semibold">Bid History</Label>
            <Badge variant="secondary"
              >{{ props.bidHistory?.length ?? 0 }} bids</Badge
            >
          </div>

          <ScrollArea class="h-[200px] w-full rounded-md border p-4">
            <div
              v-if="!props.bidHistory?.length"
              class="flex items-center justify-center h-full text-muted-foreground text-sm"
            >
              No bids yet. Be the first to bid!
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="bid in props.bidHistory"
                :key="bid.id"
                class="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
              >
                <div class="flex items-center gap-3">
                  <Badge variant="outline" class="font-mono">
                    ${{ bid.amount.toLocaleString() }}
                  </Badge>
                  <span class="text-sm font-medium">{{ bid.bidder }}</span>
                </div>
                <span class="text-xs text-muted-foreground">{{
                  bid.timestamp
                }}</span>
              </div>
            </div>
          </ScrollArea>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="handleCloseModal">Cancel</Button>
        <Button type="submit" @click="handlePlaceBid">Place Bid</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
